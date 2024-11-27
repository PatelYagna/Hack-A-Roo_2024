# GeoData3Generation.py
import sys
import os
import pandas as pd

# Add the path of the directory containing GeoDataAnalysis to Python's path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Now, import the necessary modules
from GeoDataAnalysis.GeoData1Analysis import generate_emissions_projection
from GeoDataAnalysis.GeoData2Models import create_3d_state_map

# Configuration for paths and parameters
PREDICTION_YEAR = 2030
EV_DATA_PATH = "DataOutput/EV_GAS_Registrations_by_state.csv"
EMISSIONS_DATA_PATH = "DataOutput/emission_16-22.csv"
GEOJSON_PATH = "GeoData/US_states.geojson"
OUTPUT_HTML = "GeoOutput/projected_emissions_map2.html"

# Step 1: Dynamically load all states and their codes from the EV data file
def load_state_data(ev_data_path):
    df = pd.read_csv(ev_data_path)
    
    # Check for 'State' column only
    if 'State' not in df.columns:
        raise KeyError("The dataset must contain a 'State' column.")
    
    # Extract unique state names
    unique_states = df['State'].dropna().drop_duplicates().tolist()
    
    return unique_states

# Step 2: Generate emissions data for the prediction year for all states
STATE_DATA = load_state_data(EV_DATA_PATH)

projected_emissions = generate_emissions_projection(
    data=STATE_DATA,
    prediction_year=PREDICTION_YEAR,
    ev_data_path=EV_DATA_PATH,
    emissions_data_path=EMISSIONS_DATA_PATH
)

# Check if projections were successfully created
if projected_emissions:
    # Step 3: Use create_3d_state_map to visualize the projections on a 3D map
    create_3d_state_map(
        data=projected_emissions,                # List of tuples (state_code, projected_emission)
        geojson_path=GEOJSON_PATH,               # Path to GeoJSON file for state boundaries
        height_scale=10,                         # Scale height for extrusions (adjust as needed)
        power_transform=1,                       # Apply power transformation to emphasize differences
        output_html=OUTPUT_HTML,                 # Path to save the HTML file
        enable_3d=True,                          # Enable 3D extrusion
        map_style="light",                       # Choose map style
        value_column_name="Projected Emissions"  # Name for value column in tooltip
    )
    print(f"Map generated and saved to {OUTPUT_HTML}. Open the file in a browser to view the map.")
else:
    print("No projected emissions data available for visualization.")



def calculate_state_emissions_data(year, emissions_data_path="DataOutput/emission_16-22.csv"):
    """
    Calculate state emissions data for the specified year.
    
    Parameters:
        year (int): The year for which to calculate emissions data.
        emissions_data_path (str): Path to the CSV file containing emissions data.
        
    Returns:
        emissions_df (DataFrame): A DataFrame with calculated emissions data for each state.
        summary_stats (dict): Summary statistics of emissions data for the specified year.
    """
    # Load emissions data
    emissions_df = pd.read_csv(emissions_data_path)
    
    # Filter data for the specified year
    emissions_df = emissions_df[emissions_df["Year"] == year]
    
    if emissions_df.empty:
        raise ValueError(f"No emissions data available for the year {year}.")
    
    # Calculate summary statistics
    total_emissions = emissions_df["CO2/Wh"].sum()
    total_evs = emissions_df["EV Sales"].sum() if "EV Sales" in emissions_df.columns else None
    avg_emissions = emissions_df["CO2/Wh"].mean()
    
    summary_stats = {
        "total_emissions": total_emissions,
        "total_evs": total_evs,
        "avg_emissions": avg_emissions
    }
    
    return emissions_df, summary_stats