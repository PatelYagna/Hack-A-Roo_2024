import sys
import os
import pandas as pd

# Add the path to DataAnalysis directory so Python can locate data2Regressions
sys.path.append(os.path.join(os.path.dirname(__file__), '../DataAnalysis'))

from data2Regressions import calculate_ev_emissions  # Correctly import from DataAnalysis/data2Regressions.py

# Dictionary for state name to code conversion
STATE_NAME_TO_CODE = {
    "Alabama": "AL", "Alaska": "AK", "Arizona": "AZ", "Arkansas": "AR",
    "California": "CA", "Colorado": "CO", "Connecticut": "CT", "Delaware": "DE",
    "Florida": "FL", "Georgia": "GA", "Hawaii": "HI", "Idaho": "ID",
    "Illinois": "IL", "Indiana": "IN", "Iowa": "IA", "Kansas": "KS",
    "Kentucky": "KY", "Louisiana": "LA", "Maine": "ME", "Maryland": "MD",
    "Massachusetts": "MA", "Michigan": "MI", "Minnesota": "MN", "Mississippi": "MS",
    "Missouri": "MO", "Montana": "MT", "Nebraska": "NE", "Nevada": "NV",
    "New Hampshire": "NH", "New Jersey": "NJ", "New Mexico": "NM", "New York": "NY",
    "North Carolina": "NC", "North Dakota": "ND", "Ohio": "OH", "Oklahoma": "OK",
    "Oregon": "OR", "Pennsylvania": "PA", "Rhode Island": "RI", "South Carolina": "SC",
    "South Dakota": "SD", "Tennessee": "TN", "Texas": "TX", "Utah": "UT",
    "Vermont": "VT", "Virginia": "VA", "Washington": "WA", "West Virginia": "WV",
    "Wisconsin": "WI", "Wyoming": "WY"
}

def generate_emissions_projection(data, prediction_year, ev_data_path, emissions_data_path):
    """
    Generates a list of tuples with projected EV emissions for each state code for a given prediction year.

    Parameters:
        data (list of str): A list of state names, e.g., ["California", "Texas"].
        prediction_year (int): The year for which projections are to be calculated.
        ev_data_path (str): Path to the EV sales data file.
        emissions_data_path (str): Path to the emissions data file.

    Returns:
        list of tuples: Each tuple contains a state code and its projected EV emissions, e.g., [("CA", 3000.5), ("TX", 2500.1)].
    """
    results = []

    for state_name in data:
        state_code = STATE_NAME_TO_CODE.get(state_name)
        
        if not state_code:
            print(f"State code not found for {state_name}.")
            continue

        projection = calculate_ev_emissions(
            state_name=state_name,
            #state_code=state_code,
            prediction_year=prediction_year,
            ev_data_path=ev_data_path,
            emissions_data_path=emissions_data_path
        )

        if projection:
            # Retrieve the last emission value in the 'future_emissions' for the projection year
            projected_emission = projection['future_emissions'][-1]
            results.append((state_code, projected_emission))
        else:
            print(f"No data available for {state_name} ({state_code}) in the given files.")

    return results

# Example usage
if __name__ == "__main__":
    # List of state names to process
    state_data = ["California", "Texas", "New York", "Florida"]
    prediction_year = 2030

    ev_data_path = "DataOutput/EV_GAS_Registrations_by_state.csv"
    emissions_data_path = "DataOutput/emission_16-22.csv"

    projected_emissions = generate_emissions_projection(state_data, prediction_year, ev_data_path, emissions_data_path)
    print(projected_emissions)