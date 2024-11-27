import os
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from decimal import Decimal

# Define a dictionary for state name to state code mapping for all U.S. states
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

def get_state_code(state_name):
    """Converts state name to state code."""
    return STATE_NAME_TO_CODE.get(state_name)

def list_available_states(data_path: str = "DataOutput/EV_GAS_Registrations_by_state.csv") -> list:
    """Return a list of available states in the dataset."""
    df = pd.read_csv(data_path)
    return sorted(df['State'].unique())

def calculate_registration_trend(state_name: str, prediction_year: int, vehicle_type: str, data_path: str, degree: int = 2) -> dict:
    """
    Calculate registration trend and prediction for EV or Gas vehicles using polynomial regression.
    """
    df = pd.read_csv(data_path)
    state_data = df[df['State'] == state_name].copy()
    if state_data.empty:
        return None

    sales_column = 'EV Sales' if vehicle_type == 'EV' else 'Gas Sales'
    X = state_data['Year'].values.reshape(-1, 1)
    y = state_data[sales_column].values

    # Create polynomial features
    poly_features = PolynomialFeatures(degree=degree, include_bias=False)
    X_poly = poly_features.fit_transform(X)
    
    # Fit polynomial regression
    model = LinearRegression().fit(X_poly, y)
    
    future_years = np.arange(2016, prediction_year + 1).reshape(-1, 1)
    future_years_poly = poly_features.transform(future_years)
    predictions = model.predict(future_years_poly)
    
    return {
        'years': future_years.flatten(),
        'historical_sales': y,
        'predicted_sales': predictions,
        #'coefficients': model.coef_,
        'r_squared': model.score(X_poly, y)
    }

def calculate_growth_rate(state_name: str, prediction_year: int, vehicle_type: str, data_path: str, degree: int = 2) -> dict:
    """
    Calculate growth rate trend and prediction for EV or Gas vehicles using polynomial regression.
    """
    df = pd.read_csv(data_path)
    state_data = df[df['State'] == state_name].copy()
    if state_data.empty:
        return None
    
    sales_column = 'EV Sales' if vehicle_type == 'EV' else 'Gas Sales'
    state_data['Growth_Rate'] = state_data[sales_column].pct_change() * 100
    state_data = state_data.dropna()

    X = state_data['Year'].values.reshape(-1, 1)
    y = state_data['Growth_Rate'].values

    # Create polynomial features
    poly_features = PolynomialFeatures(degree=degree, include_bias=False)
    X_poly = poly_features.fit_transform(X)
    
    # Fit polynomial regression
    model = LinearRegression().fit(X_poly, y)

    future_years = np.arange(2017, prediction_year + 1).reshape(-1, 1)
    future_years_poly = poly_features.transform(future_years)
    predictions = model.predict(future_years_poly)
    
    return {
        'years': future_years.flatten(),
        'historical_growth': y,
        'predicted_growth': predictions,
        'coefficients': model.coef_,
        'r_squared': model.score(X_poly, y)
    }

def calculate_co2_per_wh(state_code, data_path, prediction_year, degree: int = 2):
    """Calculate CO2 emissions per watt-hour for each state using polynomial regression."""
    df = pd.read_csv(data_path)
    state_data = df[df['State'] == state_code].copy()
    if state_data.empty:
        return None

    X = state_data['Year'].values.reshape(-1, 1)
    y = state_data['CO2/Wh'].values

    # Create polynomial features
    poly_features = PolynomialFeatures(degree=degree, include_bias=False)
    X_poly = poly_features.fit_transform(X)
    
    # Fit polynomial regression
    model = LinearRegression().fit(X_poly, y)

    future_years = np.arange(2016, prediction_year + 1).reshape(-1, 1)
    future_years_poly = poly_features.transform(future_years)
    predictions = model.predict(future_years_poly)
    
    return {
        'years': future_years.flatten(),
        'historical_emissions': y,
        'predicted_emissions': predictions,
        #'coefficients': model.coef_,
        'r_squared': model.score(X_poly, y)
    }

def calculate_ev_demand(state_name: str, state_code: str, prediction_year: int, ev_data_path: str, annual_kwh_per_ev: int = 3372, degree: int = 2) -> dict:
    """Calculate projected EV electricity demand using polynomial regression."""
    df = pd.read_csv(ev_data_path)
    state_data = df[df['State'] == state_name].copy()
    if state_data.empty:
        return None

    X = state_data['Year'].values.reshape(-1, 1)
    y = state_data['EV Sales'].values

    # Create polynomial features
    poly_features = PolynomialFeatures(degree=degree, include_bias=False)
    X_poly = poly_features.fit_transform(X)
    
    # Fit polynomial regression
    model = LinearRegression().fit(X_poly, y)

    historical_years = np.arange(2016, 2023)
    future_years = np.arange(2023, prediction_year + 1).reshape(-1, 1)
    
    historical_ev = state_data[state_data['Year'].isin(historical_years)]['EV Sales'].values
    historical_demand = (historical_ev * annual_kwh_per_ev) / 1000

    future_years_poly = poly_features.transform(future_years)
    future_ev = model.predict(future_years_poly)
    future_demand = (future_ev * annual_kwh_per_ev) / 1000
    
    return {
        'historical_years': historical_years,
        'historical_demand': historical_demand,
        'future_years': future_years.flatten(),
        'future_demand': future_demand,
        'coefficients': model.coef_,
        'annual_demand_change': np.mean(np.diff(historical_demand))
    }

def calculate_ev_emissions(state_name: str, prediction_year: int, ev_data_path: str, emissions_data_path: str, annual_kwh_per_ev: int = 3372, degree: int = 2) -> dict:
    """Calculate projected EV charging emissions using polynomial regression."""
    state_code = get_state_code(state_name)

    ev_df = pd.read_csv(ev_data_path)
    emissions_df = pd.read_csv(emissions_data_path)

    ev_state_data = ev_df[ev_df['State'] == state_name].copy()
    emissions_state_data = emissions_df[emissions_df['State'] == state_code].copy()

    if ev_state_data.empty or emissions_state_data.empty:
        print(f"No data available for {state_name} ({state_code}) in the given files.")
        return None

    # Create polynomial features
    poly_features = PolynomialFeatures(degree=degree, include_bias=False)

    # Fit EV sales model
    X_ev = ev_state_data['Year'].values.reshape(-1, 1)
    y_ev = ev_state_data['EV Sales'].values
    X_ev_poly = poly_features.fit_transform(X_ev)
    ev_model = LinearRegression().fit(X_ev_poly, y_ev)

    # Fit emissions rate model
    X_em = emissions_state_data['Year'].values.reshape(-1, 1)
    y_em = emissions_state_data['CO2/Wh'].values
    X_em_poly = poly_features.fit_transform(X_em)
    em_model = LinearRegression().fit(X_em_poly, y_em)

    historical_years = np.arange(2016, 2023)
    future_years = np.arange(2023, prediction_year + 1).reshape(-1, 1)
    
    historical_ev = ev_state_data[ev_state_data['Year'].isin(historical_years)]['EV Sales'].values
    historical_emissions_rate = emissions_state_data[emissions_state_data['Year'].isin(historical_years)]['CO2/Wh'].values

    historical_demand = (historical_ev * annual_kwh_per_ev) / 1000
    historical_emissions = historical_demand * historical_emissions_rate

    future_years_poly = poly_features.transform(future_years)
    future_ev = ev_model.predict(future_years_poly)
    future_emissions_rate = em_model.predict(future_years_poly)

    future_demand = (future_ev * annual_kwh_per_ev) / 1000
    future_emissions = future_demand * future_emissions_rate
    
    return {
        'historical_years': historical_years,
        'historical_emissions': historical_emissions,
        'future_years': future_years.flatten(),
        'future_emissions': future_emissions,
        'annual_emissions_change': np.mean(np.diff(historical_emissions))
    }

def calculate_ev_emissions_percent_change(state_name: str, prediction_year: int, ev_data_path: str, emissions_data_path: str, annual_kwh_per_ev: int = 3372, degree: int = 2) -> dict:
    """Calculate projected EV charging emissions, including emissions rate percentage change using polynomial regression."""
    state_code = get_state_code(state_name)

    ev_df = pd.read_csv(ev_data_path)
    emissions_df = pd.read_csv(emissions_data_path)

    ev_state_data = ev_df[ev_df['State'] == state_name].copy()
    emissions_state_data = emissions_df[emissions_df['State'] == state_code].copy()

    if ev_state_data.empty or emissions_state_data.empty:
        print(f"No data available for {state_name} ({state_code}) in the given files.")
        return None

    # Create polynomial features
    poly_features = PolynomialFeatures(degree=degree, include_bias=False)

    # Fit EV sales model
    X_ev = ev_state_data['Year'].values.reshape(-1, 1)
    y_ev = ev_state_data['EV Sales'].values
    X_ev_poly = poly_features.fit_transform(X_ev)
    ev_model = LinearRegression().fit(X_ev_poly, y_ev)

    # Fit emissions rate model
    X_em = emissions_state_data['Year'].values.reshape(-1, 1)
    y_em = emissions_state_data['CO2/Wh'].values
    X_em_poly = poly_features.fit_transform(X_em)
    em_model = LinearRegression().fit(X_em_poly, y_em)

    historical_years = np.arange(2016, 2023)
    future_years = np.arange(2023, prediction_year + 1).reshape(-1, 1)
    
    historical_ev = ev_state_data[ev_state_data['Year'].isin(historical_years)]['EV Sales'].values
    historical_emissions_rate = emissions_state_data[emissions_state_data['Year'].isin(historical_years)]['CO2/Wh'].values

    historical_demand = (historical_ev * annual_kwh_per_ev) / 1000
    historical_emissions = historical_demand * historical_emissions_rate

    future_years_poly = poly_features.transform(future_years)
    future_ev = ev_model.predict(future_years_poly)
    future_emissions_rate = em_model.predict(future_years_poly)

    future_demand = (future_ev * annual_kwh_per_ev) / 1000
    future_emissions = future_demand * future_emissions_rate

    # Calculate the percentage change in emissions rate (year-over-year)
    emissions_rate_percentage_change = np.diff(np.concatenate(([historical_emissions_rate[-1]], future_emissions_rate))) / historical_emissions_rate[-1] * 100
    
    return {
        'historical_years': historical_years,
        'historical_emissions': historical_emissions,
        'future_years': future_years.flatten(),
        'future_emissions': future_emissions,
        'annual_emissions_change': np.mean(np.diff(historical_emissions)),
        'emissions_rate_percentage_change': emissions_rate_percentage_change
    }

if __name__ == "__main__":
    # Define paths and parameters
    data_path = "DataOutput/EV_GAS_Registrations_by_state.csv"
    emissions_data_path = "DataOutput/emission_16-22.csv"
    state_name = "California"
    prediction_year = 2030
    polynomial_degree = 2  # Default degree for polynomial regression

    # Run example functions
    print("Available States:", list_available_states(data_path))
    print("\nEV Registration Trend:", calculate_registration_trend(state_name, prediction_year, "EV", data_path, polynomial_degree))
    print("\nEV Emissions Projection:", calculate_ev_emissions(state_name, prediction_year, data_path, emissions_data_path, degree=polynomial_degree))
    print("\nRATE CHANGE:", calculate_ev_emissions_percent_change(state_name, prediction_year, data_path, emissions_data_path, degree=polynomial_degree))
    
    # Additional example calls to showcase other functions
    print("\nGas Registration Trend:", calculate_registration_trend(state_name, prediction_year, "Gas", data_path, polynomial_degree))
    print("\nEV Growth Rate:", calculate_growth_rate(state_name, prediction_year, "EV", data_path, polynomial_degree))
    print("\nCO2 per Wh Projection:", calculate_co2_per_wh(get_state_code(state_name), emissions_data_path, prediction_year, polynomial_degree))
    print("\nEV Demand Projection:", calculate_ev_demand(state_name, get_state_code(state_name), prediction_year, data_path, degree=polynomial_degree))
