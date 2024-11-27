import pydeck as pdk
import pandas as pd
import json
import numpy as np
import os

def convert_to_json_compatible(data):
    """Recursively converts numpy types to Python types for JSON compatibility."""
    if isinstance(data, dict):
        return {k: convert_to_json_compatible(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [convert_to_json_compatible(item) for item in data]
    elif isinstance(data, np.integer):
        return int(data)
    elif isinstance(data, np.floating):
        return float(data)
    elif isinstance(data, np.ndarray):
        return data.tolist()
    else:
        return data

def map_value_to_color(value, quantiles, color_range):
    """Maps a value to a color based on quantiles."""
    for i, q in enumerate(quantiles):
        if value <= q:
            return color_range[i]
    return color_range[-1]  # For values above the highest quantile

def create_3d_state_map(data, geojson_path="path/to/states.geojson", height_scale=1000, power_transform=1.5,
                        output_html="3d_state_map.html", enable_3d=True,
                        map_style="mapbox://styles/mapbox/light-v10", color_range=None,
                        value_column_name="Value"):
    """
    Creates a map using pydeck with optional 3D extrusions, adjustable scale, color gradient, and transformation.

    Parameters:
        data (list of tuples): A list where each tuple contains a state abbreviation and a value, e.g., [("CA", 200), ("TX", 150)].
        geojson_path (str): Path to the GeoJSON file containing state boundaries.
        height_scale (int): Scale factor for extrusion height if 3D is enabled.
        power_transform (float): Exponent to apply to each value for height adjustment.
        output_html (str): Path to save the HTML file, e.g., "output/3d_state_map.html".
        enable_3d (bool): Enables 3D extrusion if True; sets elevation to 0 if False.
        map_style (str): Map style URL for background style.
        color_range (list): List of RGB colors for the gradient.
        value_column_name (str): The label for the value shown in the tooltip, e.g., "CO2 Per KWH".
    """
    
    if color_range is None:
    # Define color stops with smoother transitions
        color_low = [128, 0, 0, 140]       # Dark Red
        color_next = [204, 0, 0, 140]      # Medium Red
        color_mid_low = [241, 194, 50, 140] # Yellowish
        color_mid = [106, 168, 79, 140]    # Green
        color_mid_high = [61, 133, 198, 140] # Blue
        color_high = [103, 78, 167, 140]   # Dark Purple
        color_peak = [255, 69, 0, 140]     # Bright Red for high values
        color_max = [139, 0, 0, 140]       # Darker Red for extremes

        color_range = [
            color_low, 
            color_next, 
            color_mid_low, 
            color_mid, 
            color_mid_high, 
            color_high, 
            color_peak, 
            color_max
        ]

    # Convert the data into a DataFrame for easy mapping
    df = pd.DataFrame(data, columns=["state", "value"])

    # Calculate quantiles for adaptive coloring (ignoring outliers)
    quantiles = df["value"].quantile([0.2, 0.4, 0.6, 0.8, 1.0]).values

    # Load GeoJSON file
    with open(geojson_path) as f:
        geojson_data = json.load(f)

    # Map values to each state in the GeoJSON, ensuring NAME and value properties are present
    for feature in geojson_data["features"]:
        state_abbreviation = feature["id"]
        matching_row = df[df["state"] == state_abbreviation]

        # Ensure NAME property is present for tooltip, and set height and display values
        feature_name = feature["properties"].get("NAME", "Unknown")
        if not matching_row.empty:
            original_value = matching_row.iloc[0]["value"]
            transformed_value = (original_value ** power_transform) * height_scale if enable_3d else 0
            display_value = original_value  # Original value for tooltip display
            color = map_value_to_color(original_value, quantiles, color_range)
        else:
            transformed_value = 0  # Default height for states with no data
            display_value = 0  # Default display value for states with no data
            color = [200, 200, 200, 140]  # Default color for states with no data

        # Update properties with transformed and display values, and color
        feature["properties"]["value"] = int(transformed_value)  # Used for 3D extrusion height
        feature["properties"]["display_value"] = display_value  # Value for tooltip display
        feature["properties"]["color"] = color  # Color based on value
        feature["properties"]["NAME"] = feature_name

    # Ensure all data is JSON-compatible
    geojson_data = convert_to_json_compatible(geojson_data)

    # Create the pydeck Layer with optional extruded polygons and dynamic coloring
    layer = pdk.Layer(
        "GeoJsonLayer",
        geojson_data,
        pickable=True,
        stroked=False,
        filled=True,
        extruded=enable_3d,
        wireframe=True,
        get_elevation="properties.value",  # Use the 'value' property for height if 3D is enabled
        get_fill_color="properties.color",  # Use dynamically calculated color
        get_line_color=[255, 255, 255]
    )

    # Set the initial view state for the map
    view_state = pdk.ViewState(
        latitude=37.7749,  # Center the map around the U.S.
        longitude=-96.7129,
        zoom=3,
        pitch=40 if enable_3d else 0  # Only pitch if 3D is enabled
    )

    # Plain text tooltip with dynamic value column name
    tooltip_text = {
        "text": f"State: {{properties.NAME}}\n{value_column_name}: {{properties.display_value}}"
    }

    # Render the map and save to HTML
    r = pdk.Deck(
        layers=[layer],
        initial_view_state=view_state,
        tooltip=tooltip_text,  # Use plain text tooltip with dynamic label
        map_style=map_style
    )
    
    # Ensure the directory exists
    os.makedirs(os.path.dirname(output_html), exist_ok=True)

    # Save the deck to an HTML file at the specified location
    r.to_html(output_html)
    print(f"Map saved as '{output_html}'. Open this file in a browser to view the map.")
    return r

# Example usage
data = [("CA", 200), ("TX", 150), ("NY", 100), ("FL", 180)]
create_3d_state_map(data, geojson_path="GeoData/US_states.geojson", height_scale=200, power_transform=1, output_html="GeoOutput/3d_state_map.html", enable_3d=True, map_style="light", value_column_name="CO2 Per KWH")



def create_3d_county_map(data, geojson_path="path/to/counties.geojson", height_scale=1000, power_transform=1,
                         output_html="3d_county_map.html", enable_3d=True, map_style="light",
                         color_range=None, value_column_name="Value"):
    """
    Creates a map using pydeck for counties with optional 3D extrusions, adjustable scale, color gradient, and transformation.
    """
    if color_range is None:
        # Define default color stops with smoother transitions
        color_low = [75, 0, 130, 140]      # Indigo for lowest values
        color_next = [0, 0, 255, 140]      # Deep Blue
        color_mid = [0, 128, 0, 140]       # Dark Green for mid-range values
        color_high = [255, 165, 0, 140]    # Orange for high values
        color_peak = [255, 69, 0, 140]     # Bright Red for very high values
        color_max = [139, 0, 0, 140]       # Dark Red for extreme values
        color_range = [color_low, color_next, color_mid, color_high, color_peak, color_max]
            
    df = pd.DataFrame(data, columns=["geoid", "value"])
    
    # Calculate quantiles for adaptive coloring (ignoring outliers)
    quantiles = df["value"].quantile([0.2, 0.4, 0.6, 0.8, 1.0]).values
    
    # Load GeoJSON file
    with open(geojson_path) as f:
        geojson_data = json.load(f)
    
    # Map values to each county in the GeoJSON, using GEOID for matching
    for feature in geojson_data["features"]:
        geoid = feature["properties"].get("GEOID")
        matching_row = df[df["geoid"] == geoid]
        
        # Ensure NAME property is present for tooltip, and set height and display values
        county_name = feature["properties"].get("NAME", "Unknown")
        if not matching_row.empty:
            original_value = matching_row.iloc[0]["value"]
            transformed_value = (original_value ** power_transform) * height_scale if enable_3d else 0
            display_value = original_value  # Original value for tooltip display
            color = map_value_to_color(original_value, quantiles, color_range)
        else:
            transformed_value = 0  # Default height for counties with no data
            display_value = 0  # Default display value for counties with no data
            color = [200, 200, 200, 140]  # Default color for counties with no data

        # Update properties with transformed and display values, and color
        feature["properties"]["value"] = int(transformed_value)  # Used for 3D extrusion height
        feature["properties"]["display_value"] = display_value  # Value for tooltip display
        feature["properties"]["color"] = color  # Color based on value
        feature["properties"]["NAME"] = county_name

    # Ensure all data is JSON-compatible
    geojson_data = convert_to_json_compatible(geojson_data)

    # Create the pydeck Layer with optional extruded polygons and dynamic coloring
    layer = pdk.Layer(
        "GeoJsonLayer",
        geojson_data,
        pickable=True,
        stroked=False,
        filled=True,
        extruded=enable_3d,
        wireframe=True,
        get_elevation="properties.value",  # Use the 'value' property for height if 3D is enabled
        get_fill_color="properties.color",  # Use dynamically calculated color
        get_line_color=[255, 255, 255]
    )

    # Set the initial view state for the map
    view_state = pdk.ViewState(
        latitude=37.7749,  # Center the map around the U.S.
        longitude=-96.7129,
        zoom=3,
        pitch=40 if enable_3d else 0  # Only pitch if 3D is enabled
    )

    # Plain text tooltip with dynamic value column name
    tooltip_text = {
        "text": f"County: {{properties.NAME}}\n{value_column_name}: {{properties.display_value}}"
    }

    # Render the map and save to HTML
    r = pdk.Deck(
        layers=[layer],
        initial_view_state=view_state,
        tooltip=tooltip_text,  # Use plain text tooltip with dynamic label
        map_style=map_style
    )
    
    # Ensure the directory exists
    os.makedirs(os.path.dirname(output_html), exist_ok=True)

    # Save the deck to an HTML file at the specified location
    r.to_html(output_html)
    print(f"Map saved as '{output_html}'. Open this file in a browser to view the map.")
    return r

# Example usage
data = [("06037", 200), ("48201", 150), ("36061", 100), ("12086", 180)]  # Example with GEOID values for LA, Houston, Manhattan, and Miami
create_3d_county_map(data, geojson_path="GeoData/US_counties.geojson", height_scale=200, power_transform=1, output_html="GeoOutput/3d_county_map.html")

