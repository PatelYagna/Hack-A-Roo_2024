import os
import pandas as pd
import decimal as d



def extract_co2_emissions(filepath, start_year, end_year):
    """
    Extracts CO₂ emissions data for each state within a defined timeline from the specified Excel file.
    """
    # Load data with specified headers and skip any footer rows if necessary
    df = pd.read_excel(filepath, header=4, skiprows=[56, 57])
    
    # Convert year columns to integers for compatibility with DataFrame column types
    year_columns = [year for year in range(start_year, end_year + 1)]
    columns_to_keep = ['State'] + year_columns
    filtered_df = df[columns_to_keep]
    
    return filtered_df


def extract_annual_generation(filepath, start_year, end_year):
    """
    Extracts annual generation data, filtering for 'Total Electric Power Industry' and 'Total' energy source.
    """
    # Load data with the appropriate header
    df = pd.read_excel(filepath, header=1)

    # Filter for the desired rows based on type and energy source
    filtered_df = df[
        (df['TYPE OF PRODUCER'] == 'Total Electric Power Industry') &
        (df['ENERGY SOURCE'] == 'Total') &
        (df['YEAR'].between(start_year, end_year))
    ]

    return filtered_df


def calculate_co2_per_wh(co2_filepath, generation_filepath, start_year, end_year, output_file):
    """
    Calculates CO₂ emissions per watt-hour by state and year, saving the results to a CSV.
    """
    # Load data
    annual_state_CO2 = extract_co2_emissions(co2_filepath, start_year, end_year)
    annual_state_electricity = extract_annual_generation(generation_filepath, start_year, end_year)

    # State abbreviation mapping
    state_name_abbreviation = {
        "Alabama": "AL", "Alaska": "AK", "Arizona": "AZ", "Arkansas": "AR", "California": "CA",
        "Colorado": "CO", "Connecticut": "CT", "Delaware": "DE", "Florida": "FL", "Georgia": "GA",
        "Hawaii": "HI", "Idaho": "ID", "Illinois": "IL", "Indiana": "IN", "Iowa": "IA",
        "Kansas": "KS", "Kentucky": "KY", "Louisiana": "LA", "Maine": "ME", "Maryland": "MD",
        "Massachusetts": "MA", "Michigan": "MI", "Minnesota": "MN", "Mississippi": "MS", "Missouri": "MO",
        "Montana": "MT", "Nebraska": "NE", "Nevada": "NV", "New Hampshire": "NH", "New Jersey": "NJ",
        "New Mexico": "NM", "New York": "NY", "North Carolina": "NC", "North Dakota": "ND", "Ohio": "OH",
        "Oklahoma": "OK", "Oregon": "OR", "Pennsylvania": "PA", "Rhode Island": "RI", "South Carolina": "SC",
        "South Dakota": "SD", "Tennessee": "TN", "Texas": "TX", "Utah": "UT", "Vermont": "VT",
        "Virginia": "VA", "Washington": "WA", "West Virginia": "WV", "Wisconsin": "WI", "Wyoming": "WY"
    }

    # Dictionary to store calculated CO2 per Wh data
    annual_state_CO2_to_Wh = {"State": [], "Year": [], "CO2/Wh": []}

    for year in range(start_year, end_year + 1):
        for index, row in annual_state_CO2.iterrows():
            current_state_abbreviated = state_name_abbreviation.get(row["State"])
            if not current_state_abbreviated:
                continue

            annual_state_CO2_to_Wh["State"].append(current_state_abbreviated)
            annual_state_CO2_to_Wh["Year"].append(year)

            state_carbon_production = row[year]
            row_of_interest = annual_state_electricity.loc[
                (annual_state_electricity["YEAR"] == year) &
                (annual_state_electricity["STATE"] == current_state_abbreviated)
            ]

            if row_of_interest.empty:
                annual_state_CO2_to_Wh["CO2/Wh"].append(None)
                continue

            state_electricity_production = row_of_interest["GENERATION (Megawatthours)"].iloc[0]

            # Convert CO₂ to kg and generation to watt-hours
            state_carbon_production_kg = d.Decimal(state_carbon_production) * d.Decimal(1e9)
            state_electricity_production_Wh = d.Decimal(state_electricity_production) * d.Decimal(1e6)

            state_kg_CO2_per_Wh = state_carbon_production_kg / state_electricity_production_Wh
            annual_state_CO2_to_Wh["CO2/Wh"].append(float(state_kg_CO2_per_Wh))

    # Save results to a CSV
    output_df = pd.DataFrame(annual_state_CO2_to_Wh)
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    output_df.to_csv(output_file, index=False)
    print(f"Data successfully saved to: {output_file}")

# Example usage
co2_filepath = 'CSVData/USDOE_annual_CO2_per_state_power_generation.xlsx'
generation_filepath = 'CSVData/USDOE_annual_generation_state.xls'
start_year = 2016
end_year = 2022
output_file = 'DataOutput/emission_16-22.csv'

calculate_co2_per_wh(co2_filepath, generation_filepath, start_year, end_year, output_file)





#EV/GAS SALES DATA GENERATION
import os
import pandas as pd

def process_ev_sales_data(filepath, output_file):
    """
    Processes EV and Gasoline sales data by state and year, saving the results to a CSV file.
    
    Parameters:
        filepath (str): Path to the Excel file containing EV sales data.
        output_file (str): Path to save the output CSV file.
    """
    # Debug information
    #print(f"Looking for EV data file at: {filepath}")
    
    # Verify if the file exists
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"EV data file not found at: {filepath}")

    # Load the Excel file
    data = pd.read_excel(filepath, sheet_name='Sheet1')
    
    # Check if necessary columns are present, and handle accordingly
    required_columns = ['State', 'Electric (EV)', 'Biodiesel', 'Ethanol/Flex (E85)', 'Compressed Natural Gas (CNG)',
                        'Propane', 'Hydrogen', 'Methanol', 'Gasoline', 'Diesel', 'Year']
    
    missing_columns = [col for col in required_columns if col not in data.columns]
    if missing_columns:
        raise KeyError(f"Missing required columns: {missing_columns}")
    
    # Combine EV, PHEV, and HEV into a single 'EV Sales' column (add other types as needed)
    data['EV Sales'] = data['Electric (EV)']
    
    # Combine Gasoline, Diesel, and other fuel types into a single 'Gas Sales' column
    data['Gas Sales'] = (
        data['Biodiesel'] +
        data['Ethanol/Flex (E85)'] +
        data['Compressed Natural Gas (CNG)'] +
        data['Propane'] +
        data['Hydrogen'] +
        data['Methanol'] +
        data['Gasoline'] +
        data['Diesel']
    )

    # Select only the necessary columns for output
    output_data = data[['State', 'EV Sales', 'Gas Sales', 'Year']]
    
    # Create output directory if it doesn't exist
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    # Save the result to a CSV file
    output_data.to_csv(output_file, index=False)
    print(f"Data successfully saved to: {output_file}")

# Example usage
input_file = 'CSVDATA/USDOE_VehicleRegistrationCountbyState.xlsx'
output_file = 'DataOutput/EV_GAS_Registrations_by_state.csv'
process_ev_sales_data(input_file, output_file)