from shiny import ui, App, render, reactive, session, run_app
from shinywidgets import output_widget, render_widget, render_pydeck, render_plotly
import pandas as pd
import json
import sys
import os
import numpy as np
import pydeck as pdk

# Add the path to DataAnalysis so Python can locate data3Models and data2Regressions
sys.path.append(os.path.join(os.path.dirname(__file__), '../DataAnalysis'))
ev_data_path = "DataOutput/EV_GAS_Registrations_by_state.csv"


# Set up paths for modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../GeoDataAnalysis')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../DataAnalysis')))

ev_data_path = "DataOutput/EV_GAS_Registrations_by_state.csv"

# Import necessary functions and mappings
from data3Models import plot_registration_trend, plot_co2_emissions, plot_ev_demand, plot_ev_emissions
from data2Regressions import calculate_ev_emissions, calculate_ev_emissions_percent_change
from GeoData1Analysis import calculate_ev_emissions, STATE_NAME_TO_CODE





# Now, import the necessary functions
from data3Models import (
    plot_registration_trend,
    plot_co2_emissions,
    plot_ev_demand,
    plot_ev_emissions
)

# Sample data function to fetch available states
def list_available_states(data_path: str) -> list:
    df = pd.read_csv(data_path)
    return sorted(df['State'].unique())

# Load GeoJSON for map (assuming 'states.geojson' file path)
with open("GeoData/US_states.geojson", "r") as f:
    states_geojson = json.load(f)

# Define UI
app_ui = ui.page_fluid(
    ui.tags.style("""
    .h-100 { height: 100% !important; }
    .card-body { height: calc(100vh - 150px) !important; }
    .card { height: 100% !important; }
    #map_view { height: 100% !important; }
    .compact-card { padding: 0.5rem !important; }
    .compact-card .card-body { padding: 0.5rem !important; height: auto !important; }
    
    /* Overlay card styles */
    .overlay-card {
        position: absolute;
        bottom: 10px;
        left: 10px;
        width: 200px;
        background-color: white;
        border-radius: 5px;
        box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.3);
        z-index: 1000;
        padding: 10px;
    }
"""),


    ui.div(
        {"class": "container-fluid mt-2"},
        # Header Row
        ui.div(
            {"class": "row mb-3"},
            ui.div(
                {"class": "col-12"},
                ui.div(
                    {"class": "d-flex justify-content-between align-items-center bg-light p-2 rounded"},
                    ui.div(
                        {"class": "d-flex flex-column"},
                        ui.h4("EV Impact Analysis", class_="m-0"),
                        ui.p("By Daniel Huynh, Duy Lam, Yagna Patel, Kevin Yu", class_="m-0 text-muted")
                    ),
                    
                )
            )
        )
    ),



    ui.div(
        {"class": "container-fluid mt-3"},
        
        # Control Panel Row for State Selection and Year Slider
        ui.div(
            {"class": "row mb-3"},
            ui.div(
                {"class": "col-6"},
                ui.div(
                    {"class": "compact-card"},
                    ui.input_select("state_ev", "Select State for EV Registration:", choices=list_available_states(ev_data_path))
                )
                
            ),
            ui.div(
                {"class": "col-6"},
                ui.div(
                    {"class": "compact-card"},
                    ui.input_slider("year", "Prediction Year", min=2023, max=2035, value=2030)
                )
            )
        ),
        
        # Graphs Row
        ui.div(
            {"class": "row"},
            ui.div(
                {"class": "col-6"},
                ui.div(
                    {"class": "graph-card"},
                    output_widget("ev_registration_plot")
                )
            ),
            ui.div(
                {"class": "col-6"},
                ui.div(
                    {"class": "graph-card"},
                    output_widget("co2_plot")
                )
            ),
            ui.div(
                {"class": "col-6"},
                ui.div(
                    {"class": "graph-card"},
                    output_widget("ev_demand_plot")
                )
            ),
            ui.div(
                {"class": "col-6"},
                ui.div(
                    {"class": "graph-card"},
                    output_widget("ev_emissions_plot")
                )
            )
        ),
        


        ui.div(
    {"class": "col-12 h-100"},
    ui.card(
        ui.card_header(
            ui.div(
                {"class": "d-flex justify-content-between align-items-center"},
                ui.h3("Charging Emissions Slope Percent Change Annual Prediction", class_="card-title m-0"),
                ui.div(
                    {"class": "d-flex gap-2"},
                    ui.input_select(
                        "map_style2",  # Changed to avoid duplicate ID
                        None,
                        ["light", "dark"],
                        selected="light",
                        width="150px"
                    ),
                    ui.input_switch("enable_3d2", "3D View", value=False),  # Changed to avoid duplicate ID
                    ui.input_switch("show_counties2", "Show Counties", value=False)  # Changed to avoid duplicate ID
                )
            )
        ),
        ui.card_body(
            ui.div(
                #{"style": "position: relative; height: 400px;"},
                {"style": "position: relative; height: 100%;"},
                output_widget("percent_map_view"),
                # Overlay Card
                ui.div(
                    {"class": "overlay-card"},
                        ui.h6("Key Information"),
                    ui.div(
                        ui.p("Colors indicate emissions slope percent change"),
                        ui.div(
                            {"style": "display: flex; align-items: center; margin-bottom: 5px;"},
                            ui.div({"style": "width: 20px; height: 20px; background-color: #674E9E; margin-right: 5px;"}),
                            ui.span("High Decrease")
                        ),
                        ui.div(
                            {"style": "display: flex; align-items: center; margin-bottom: 5px;"},
                            ui.div({"style": "width: 20px; height: 20px; background-color: #3D85C6; margin-right: 5px;"}),
                            ui.span("Low Decrease")
                        ),
                        ui.div(
                            {"style": "display: flex; align-items: center; margin-bottom: 5px;"},
                            ui.div({"style": "width: 20px; height: 20px; background-color: #6AA84F; margin-right: 5px;"}),
                            ui.span("Minimal Change")
                        ),
                        ui.div(
                            {"style": "display: flex; align-items: center; margin-bottom: 5px;"},
                            ui.div({"style": "width: 20px; height: 20px; background-color: #F1C232; margin-right: 5px;"}),
                            ui.span("Low Increase")
                        ),
                        ui.div(
                            {"style": "display: flex; align-items: center;"},
                            ui.div({"style": "width: 20px; height: 20px; background-color: #CC0000; margin-right: 5px;"}),
                            ui.span("High Increase")
                        )
                    )
                )
            ),
            class_="h-100"
        ),
        full_screen=True,
        class_="compact-card"
    )
    ),





    ui.div(
    {"class": "col-12 h-100"},
    ui.card(
        ui.card_header(
            ui.div(
                {"class": "d-flex justify-content-between align-items-center"},
                ui.h3("EV Charging Emissions Annual Prediction", class_="card-title m-0"),
                ui.div(
                    {"class": "d-flex gap-2"},
                    ui.input_select(
                        "map_style",
                        None,
                        ["light", "dark"],
                        selected="light",
                        width="150px"
                    ),
                    ui.input_switch("enable_3d", "3D View", value=True),
                    ui.input_switch("show_counties", "Show Counties", value=False)
                )
            )
        ),
        ui.card_body(
            ui.div(
                {"style": "position: relative; height: 100%;"},
                output_widget("map_view"),
                # Overlay Card
                ui.div(
                    {"class": "overlay-card"},
                    ui.h6("Key Information"),
                    ui.div(
                        ui.p("Colors indicate EV charging emissions output"),
                        ui.div(
                            {"style": "display: flex; align-items: center; margin-bottom: 5px;"},
                            ui.div({"style": "width: 20px; height: 20px; background-color: #674E9E; margin-right: 5px;"}),
                            ui.span("Very Low")
                        ),
                        ui.div(
                            {"style": "display: flex; align-items: center; margin-bottom: 5px;"},
                            ui.div({"style": "width: 20px; height: 20px; background-color: #3D85C6; margin-right: 5px;"}),
                            ui.span("Low")
                        ),
                        ui.div(
                            {"style": "display: flex; align-items: center; margin-bottom: 5px;"},
                            ui.div({"style": "width: 20px; height: 20px; background-color: #6AA84F; margin-right: 5px;"}),
                            ui.span("Medium")
                        ),
                        ui.div(
                            {"style": "display: flex; align-items: center; margin-bottom: 5px;"},
                            ui.div({"style": "width: 20px; height: 20px; background-color: #F1C232; margin-right: 5px;"}),
                            ui.span("High")
                        ),
                        ui.div(
                            {"style": "display: flex; align-items: center;"},
                            ui.div({"style": "width: 20px; height: 20px; background-color: #CC0000; margin-right: 5px;"}),
                            ui.span("Very High")
                        )
                    )
)
            ),
            class_="h-100"
        ),
        full_screen=True,
        class_="h-100"
    ),

    




)

    )
)



def verify_data_files():
    """Verify that required data files exist and are readable"""
    import os
    
    required_files = [
        "DataOutput/EV_GAS_Registrations_by_state.csv",
        "DataOutput/emission_16-22.csv",
        "GeoData/US_states.geojson"
    ]
    
    for file_path in required_files:
        try:
            if not os.path.exists(file_path):
                print(f"ERROR: Required file not found: {file_path}")
                print(f"Current working directory: {os.getcwd()}")
                continue
                
            if file_path.endswith('.csv'):
                df = pd.read_csv(file_path)
                print(f"\nSuccessfully loaded {file_path}")
                print(f"Columns: {df.columns.tolist()}")
                print(f"First few rows:")
                print(df.head())
            elif file_path.endswith('.geojson'):
                with open(file_path, 'r') as f:
                    data = json.load(f)
                print(f"\nSuccessfully loaded {file_path}")
                
        except Exception as e:
            print(f"ERROR loading {file_path}: {str(e)}")












































# Helper functions
def generate_emissions_projection(data, prediction_year, ev_data_path, emissions_data_path):
    """Generates a list of tuples with projected EV emissions for each state."""
    results = []
    for state_name in data:
        state_code = STATE_NAME_TO_CODE.get(state_name)
        if state_code:
            projection = calculate_ev_emissions(
                state_name=state_name,
                prediction_year=prediction_year,
                ev_data_path=ev_data_path,
                emissions_data_path=emissions_data_path
            )
            if projection:
                projected_emission = projection['future_emissions'][-1]
                results.append((state_code, projected_emission))
    return results

def generate_ev_emissions_percent_change_projection(data, prediction_year, ev_data_path, emissions_data_path):
    """Generates a list of tuples with projected EV emissions for each state."""
    results2 = []
    for state_name in data:
        state_code = STATE_NAME_TO_CODE.get(state_name)
        if state_code:
            projection = calculate_ev_emissions_percent_change(
                state_name=state_name,
                prediction_year=prediction_year,
                ev_data_path=ev_data_path,
                emissions_data_path=emissions_data_path
            )
            if projection:
                projected_emission_percent_change = projection['emissions_rate_percentage_change'][-1]
                results2.append((state_code, projected_emission_percent_change))
    return results2





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
        # Define color stops with smoother transitions in the desired order
        color_low = [103, 78, 167, 140]       # Dark Purple
        color_next = [61, 133, 198, 140]      # Blue
        color_mid_low = [106, 168, 79, 140]   # Green
        color_mid = [241, 194, 50, 140]       # Yellowish
        color_mid_high = [255, 69, 0, 140]    # Bright Red for high values
        color_high = [128, 0, 0, 140]         # Dark Red
        color_peak = [204, 0, 0, 140]         # Medium Red
        color_max = [139, 0, 0, 140]          # Darker Red for extremes

        color_range = [
            color_low,       # Dark Purple
            color_next,      # Blue
            color_mid_low,   # Green
            color_mid,       # Yellowish
            color_mid_high,  # Bright Red
            color_high,      # Dark Red
            color_peak,      # Medium Red
            color_max        # Darker Red
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
    return pdk.Deck(
        layers=[layer],
        initial_view_state=view_state,
        tooltip=tooltip_text,  # Use plain text tooltip with dynamic label
        map_style=map_style
    )
    
    # Ensure the directory exists
    #os.makedirs(os.path.dirname(output_html), exist_ok=True)

    # Save the deck to an HTML file at the specified location
    r.to_html(output_html)
    print(f"Map saved as '{output_html}'. Open this file in a browser to view the map.")
    return r.deck






















def server(input, output, session):
    print("\nVerifying data files...")
    verify_data_files()
    # State name to code mapping
    state_codes = {
        'Alabama': 'AL',
        'Alaska': 'AK',
        'Arizona': 'AZ',
        'Arkansas': 'AR',
        'California': 'CA',
        'Colorado': 'CO',
        'Connecticut': 'CT',
        'Delaware': 'DE',
        'Florida': 'FL',
        'Georgia': 'GA',
        'Hawaii': 'HI',
        'Idaho': 'ID',
        'Illinois': 'IL',
        'Indiana': 'IN',
        'Iowa': 'IA',
        'Kansas': 'KS',
        'Kentucky': 'KY',
        'Louisiana': 'LA',
        'Maine': 'ME',
        'Maryland': 'MD',
        'Massachusetts': 'MA',
        'Michigan': 'MI',
        'Minnesota': 'MN',
        'Mississippi': 'MS',
        'Missouri': 'MO',
        'Montana': 'MT',
        'Nebraska': 'NE',
        'Nevada': 'NV',
        'New Hampshire': 'NH',
        'New Jersey': 'NJ',
        'New Mexico': 'NM',
        'New York': 'NY',
        'North Carolina': 'NC',
        'North Dakota': 'ND',
        'Ohio': 'OH',
        'Oklahoma': 'OK',
        'Oregon': 'OR',
        'Pennsylvania': 'PA',
        'Rhode Island': 'RI',
        'South Carolina': 'SC',
        'South Dakota': 'SD',
        'Tennessee': 'TN',
        'Texas': 'TX',
        'Utah': 'UT',
        'Vermont': 'VT',
        'Virginia': 'VA',
        'Washington': 'WA',
        'West Virginia': 'WV',
        'Wisconsin': 'WI',
        'Wyoming': 'WY',
        'District of Columbia': 'DC'
    }
    
    @output
    @render_widget
    def ev_registration_plot():
        try:
            return plot_registration_trend(input.state_ev(), int(input.year()), "EV", "DataOutput/EV_GAS_Registrations_by_state.csv")
        except Exception as e:
            print(f"Error in ev_registration_plot: {str(e)}")
            return None

    @output
    @render_widget
    def co2_plot():
        try:
            state_name = input.state_ev()
            state_code = state_codes.get(state_name, state_name[:2].upper())
            return plot_co2_emissions(state_code, int(input.year()), "DataOutput/emission_16-22.csv")
        except Exception as e:
            print(f"Error in co2_plot: {str(e)}")
            return None

    @output
    @render_widget
    def ev_demand_plot():
        try:
            state_name = input.state_ev()
            state_code = state_codes.get(state_name, state_name[:2].upper())
            return plot_ev_demand(state_name, state_code, int(input.year()), "DataOutput/EV_GAS_Registrations_by_state.csv")
        except Exception as e:
            print(f"Error in ev_demand_plot: {str(e)}")
            return None

    @output
    @render_widget
    def ev_emissions_plot():
        try:
            state_name = input.state_ev()
            # We don't need state_code anymore since calculate_ev_emissions doesn't use it
            year = int(input.year())
            
            print(f"\nGenerating emissions plot for:")
            print(f"state_name: {state_name}")
            print(f"year: {year}")
            
            fig = plot_ev_emissions(
                state_name=state_name,
                #state_code=None,  # Not used by the underlying function
                prediction_year=year,
                ev_data_path="DataOutput/EV_GAS_Registrations_by_state.csv",
                emissions_data_path="DataOutput/emission_16-22.csv"
            )
            
            if fig is None:
                print(f"No plot generated for {state_name}")
            return fig
            
        except Exception as e:
            print(f"Error in ev_emissions_plot: {str(e)}")
            import traceback
            print(traceback.format_exc())
            return None

    @output
    @render_pydeck
    def map_view():
        PREDICTION_YEAR = int(input.year())
        STATE_DATA = list_available_states(ev_data_path)
        projected_emissions = generate_emissions_projection(
            data=STATE_DATA,
            prediction_year=PREDICTION_YEAR,
            ev_data_path=ev_data_path,
            emissions_data_path="DataOutput/emission_16-22.csv"
        )
        
        return create_3d_state_map(
                data = projected_emissions, 
                geojson_path="GeoData/US_states.geojson", 
                height_scale=100, 
                power_transform=1,
                output_html="emissions.html", 
                enable_3d=input.enable_3d(),
                map_style=input.map_style(), 
                color_range=None,
                value_column_name="Emmision Metric Tons"
            )
    
    @output
    @render_pydeck
    def percent_map_view():
        PREDICTION_YEAR = int(input.year())
        STATE_DATA = list_available_states(ev_data_path)
        projected_emissions_percent_change = generate_ev_emissions_percent_change_projection(
            data=STATE_DATA,
            prediction_year=PREDICTION_YEAR,
            ev_data_path=ev_data_path,
            emissions_data_path="DataOutput/emission_16-22.csv"
        )
        
        return create_3d_state_map(
                data = projected_emissions_percent_change, 
                geojson_path="GeoData/US_states.geojson", 
                height_scale=100, 
                power_transform=1,
                output_html="emissionspercentchange.html", 
                enable_3d=input.enable_3d2(),
                map_style=input.map_style2(), 
                color_range=None,
                value_column_name="Slope Percent Change"
            )


app = App(app_ui, server)

run_app(app)