import plotly.graph_objects as go
from sklearn.linear_model import LinearRegression
import pandas as pd

from data2Regressions import (
    list_available_states,
    calculate_registration_trend,
    calculate_growth_rate,
    calculate_co2_per_wh,
    calculate_ev_demand,
    calculate_ev_emissions
)

def plot_registration_trend(state_name: str, prediction_year: int, vehicle_type: str, data_path: str, degree: int = 2):
    """
    Plot registration trends using polynomial regression results with Plotly.
    Returns a Plotly figure object.
    """
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    
    # Get the data from the registration trend calculation
    data = calculate_registration_trend(state_name, prediction_year, vehicle_type, data_path, degree)
    if data is None:
        print(f"No data available for {state_name}")
        return None

    # Create figure
    fig = go.Figure()
    
    # Add historical data as scatter plot
    historical_years = data['years'][:len(data['historical_sales'])]
    fig.add_trace(
        go.Scatter(
            x=historical_years,
            y=data['historical_sales'],
            mode='markers',
            name='Historical Data',
            marker=dict(
                size=8,
                color='blue',
            )
        )
    )
    
    # Add predictions as line
    fig.add_trace(
        go.Scatter(
            x=data['years'],
            y=data['predicted_sales'],
            mode='lines',
            name=f'Polynomial Predictions (degree={degree})',
            line=dict(
                color='red',
                dash='dash'
            )
        )
    )
    
    # Update layout
    fig.update_layout(
        title=dict(
            text=f'{vehicle_type} Registration Trend in {state_name}<br>R² = {data["r_squared"]:.3f}',
            x=0.5,
            xanchor='center'
        ),
        xaxis_title='Year',
        yaxis_title=f'{vehicle_type} Registrations',
        showlegend=True,
        template='plotly_white',
        hovermode='x unified',
        xaxis=dict(
            showgrid=True,
            gridwidth=1,
            gridcolor='lightgray'
        ),
        yaxis=dict(
            showgrid=True,
            gridwidth=1,
            gridcolor='lightgray'
        )
    )
    
    return fig

def plot_growth_rate(state_name: str, prediction_year: int, vehicle_type: str, data_path: str, degree: int = 2):
    """
    Plot growth rate trends using polynomial regression results with Plotly.
    Returns a Plotly figure object.
    """
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    
    # Get the data from the growth rate calculation
    data = calculate_growth_rate(state_name, prediction_year, vehicle_type, data_path, degree)
    if data is None:
        print(f"No data available for {state_name}")
        return None

    # Create figure
    fig = go.Figure()
    
    # Add historical data as scatter plot
    historical_years = data['years'][:len(data['historical_growth'])]
    fig.add_trace(
        go.Scatter(
            x=historical_years,
            y=data['historical_growth'],
            mode='markers',
            name='Historical Growth',
            marker=dict(
                size=8,
                color='blue',
            )
        )
    )
    
    # Add predictions as line
    fig.add_trace(
        go.Scatter(
            x=data['years'],
            y=data['predicted_growth'],
            mode='lines',
            name=f'Polynomial Predictions (degree={degree})',
            line=dict(
                color='red',
                dash='dash'
            )
        )
    )
    
    # Update layout
    fig.update_layout(
        title=dict(
            text=f'{vehicle_type} Registration Growth Rate in {state_name}<br>R² = {data["r_squared"]:.3f}',
            x=0.5,
            xanchor='center'
        ),
        xaxis_title='Year',
        yaxis_title='Growth Rate (%)',
        showlegend=True,
        template='plotly_white',
        hovermode='x unified',
        xaxis=dict(
            showgrid=True,
            gridwidth=1,
            gridcolor='lightgray'
        ),
        yaxis=dict(
            showgrid=True,
            gridwidth=1,
            gridcolor='lightgray'
        )
    )
    
    # Add a horizontal line at y=0 for reference
    fig.add_hline(y=0, line_dash="dot", line_color="gray", opacity=0.5)
    
    return fig

def plot_co2_emissions(state_code: str, prediction_year: int, emissions_data_path: str, degree: int = 2):
    """
    Plot CO2 emissions per watt-hour trends using polynomial regression results with Plotly.
    Parameters:
        state_code: str - Two letter state code
        prediction_year: int - Year up to which to predict
        emissions_data_path: str - Path to the emissions data CSV file
        degree: int - Degree of polynomial regression (default=2)
    Returns a Plotly figure object.
    """
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    
    # Get the data from the emissions calculation - note the correct parameter order
    data = calculate_co2_per_wh(state_code, emissions_data_path, prediction_year, degree)
    if data is None:
        print(f"No data available for state code: {state_code}")
        return None

    # Create figure
    fig = go.Figure()
    
    # Add historical data as scatter plot
    historical_years = data['years'][:len(data['historical_emissions'])]
    fig.add_trace(
        go.Scatter(
            x=historical_years,
            y=data['historical_emissions'],
            mode='markers',
            name='Historical CO₂/Wh',
            marker=dict(
                size=8,
                color='blue',
            )
        )
    )
    
    # Add predictions as line
    fig.add_trace(
        go.Scatter(
            x=data['years'],
            y=data['predicted_emissions'],
            mode='lines',
            name=f'Polynomial Predictions (degree={degree})',
            line=dict(
                color='red',
                dash='dash'
            )
        )
    )
    
    # Update layout
    fig.update_layout(
        title=dict(
            text=f'CO₂ Emissions per Watt-hour in {state_code}<br>R² = {data["r_squared"]:.3f}',
            x=0.5,
            xanchor='center'
        ),
        xaxis_title='Year',
        yaxis_title='CO₂/Wh',
        showlegend=True,
        template='plotly_white',
        hovermode='x unified',
        xaxis=dict(
            showgrid=True,
            gridwidth=1,
            gridcolor='lightgray'
        ),
        yaxis=dict(
            showgrid=True,
            gridwidth=1,
            gridcolor='lightgray'
        )
    )
    
    return fig


def plot_ev_demand(state_name, state_code, prediction_year, ev_data_path):
    data = calculate_ev_demand(state_name, state_code, prediction_year, ev_data_path)
    if data is None:
        print(f"No data available for {state_name}.")
        return
    
    annual_demand_change = data['annual_demand_change']
    formula_text = f"Annual Demand Change ≈ {annual_demand_change:.0f} MWh/year"
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=data['historical_years'],
        y=data['historical_demand'],
        mode='markers',
        name='Historical Demand',
        marker=dict(size=10, color='#2ecc71', symbol='circle')
    ))
    fig.add_trace(go.Scatter(
        x=data['future_years'],
        y=data['future_demand'],
        mode='lines',
        name='Projected Demand',
        line=dict(color='#27ae60', dash='dash')
    ))
    fig.update_layout(
        title=f'EV Electricity Demand in {state_name}<br>{formula_text}',
        xaxis_title='Year',
        yaxis_title='Electricity Demand (MWh)',
        template='plotly_white'
    )
    return fig
    #fig.show()

def plot_ev_emissions(state_name, prediction_year, ev_data_path, emissions_data_path):
    """
    Creates a plot showing EV charging emissions trends
    
    Args:
        state_name (str): Name of the state
        state_code (str): Not used (kept for compatibility)
        prediction_year (int): Year to predict emissions for
        ev_data_path (str): Path to the EV registration data file
        emissions_data_path (str): Path to the emissions data file
    """
    try:
        print(f"Calling calculate_ev_emissions with:")
        print(f"state_name: {state_name}")
        print(f"prediction_year: {prediction_year}")
        print(f"ev_data_path: {ev_data_path}")
        print(f"emissions_data_path: {emissions_data_path}")
        
        data = calculate_ev_emissions(
            state_name=state_name,             # first arg
            prediction_year=prediction_year,    # second arg 
            ev_data_path=ev_data_path,         # third arg
            emissions_data_path=emissions_data_path  # fourth arg
        )
        
        if data is None:
            print(f"No data available for {state_name}.")
            return None
        
        annual_emissions_change = data['annual_emissions_change']
        formula_text = f"Annual Emissions Change ≈ {annual_emissions_change:.1f} metric tons/year"
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=data['historical_years'],
            y=data['historical_emissions'],
            mode='markers',
            name='Historical Emissions',
            marker=dict(size=10, color='#e74c3c', symbol='circle')
        ))
        fig.add_trace(go.Scatter(
            x=data['future_years'],
            y=data['future_emissions'],
            mode='lines',
            name='Projected Emissions',
            line=dict(color='#c0392b', dash='dash')
        ))
        fig.update_layout(
            title=f'EV Charging Emissions in {state_name}<br>{formula_text}',
            xaxis_title='Year',
            yaxis_title='CO2 Emissions (metric tons)',
            template='plotly_white'
        )
        return fig
        
    except Exception as e:
        print(f"Error in plot_ev_emissions: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return None


def plot_ev_gas_proportion(state_name, prediction_year=None, data_path="output/combined_ev_gas_sales_by_state.csv"):
    """
    Creates a pie chart showing the proportion of EV and Gas vehicle registrations for a specific state.
    Uses historical data if available for the specified year; otherwise, applies regression for predictions.
    """
    # Load the data
    df = pd.read_csv(data_path)
    
    # Filter data for the specified state
    state_data = df[df['State'] == state_name]
    
    # Check if state data is available
    if state_data.empty:
        print(f"No data available for {state_name}.")
        return
    
    # If no prediction year is provided, use the most recent year in the dataset
    if prediction_year is None:
        prediction_year = state_data['Year'].max()

    # Check if the requested year is in the historical data
    if prediction_year in state_data['Year'].values:
        # Use historical data directly
        data_for_year = state_data[state_data['Year'] == prediction_year].iloc[0]
        ev_sales = data_for_year['EV Sales']
        gas_sales = data_for_year['Gas Sales']
    else:
        # Apply regression to predict EV and Gas sales for the prediction_year
        X = state_data['Year'].values.reshape(-1, 1)
        
        # Predict EV Sales
        ev_model = LinearRegression()
        ev_model.fit(X, state_data['EV Sales'].values)
        ev_sales = ev_model.predict([[prediction_year]])[0]
        
        # Predict Gas Sales
        gas_model = LinearRegression()
        gas_model.fit(X, state_data['Gas Sales'].values)
        gas_sales = gas_model.predict([[prediction_year]])[0]
    
    # Create the pie chart
    fig = go.Figure(data=[go.Pie(
        labels=['EV Sales', 'Gas Sales'],
        values=[ev_sales, gas_sales],
        hole=0.3  # Optional: create a donut chart
    )])
    
    # Update layout
    fig.update_layout(
        title=f"{'Predicted ' if prediction_year > state_data['Year'].max() else ''}Vehicle Registration Proportion in {state_name} ({prediction_year})",
        template='plotly_white'
    )
    
    # Show the chart
    return fig
    #fig.show















# Example usage
if __name__ == "__main__":

     # Define paths and parameters
    data_path = "DataOutput/EV_GAS_Registrations_by_state.csv"
    emissions_data_path = "DataOutput/emission_16-22.csv"
    state_name = "CA"
    state_code = "CA"  # Get state code from state name
    prediction_year = 2030
    polynomial_degree = 2

    # Create CO2 emissions plot
    fig = plot_co2_emissions(state_code, emissions_data_path, prediction_year, polynomial_degree)
    if fig is not None:
        fig.show()


    # state_name = "California"
    # state_code = "CA"
    # prediction_year = 2030
    # ev_data_path = "DataOutput/EV_GAS_Registrations_by_state.csv"
    # emissions_data_path = "DataOutput/emission_16-22.csv"


    # plot_ev_gas_proportion(state_name, prediction_year, ev_data_path)
    # plot_registration_trend(state_name, prediction_year, "EV", ev_data_path)
    # plot_registration_trend(state_name, prediction_year, "Gas", ev_data_path)
    # plot_growth_rate(state_name, prediction_year, "EV", ev_data_path)
    # plot_growth_rate(state_name, prediction_year, "Gas", ev_data_path)
    # plot_co2_emissions(state_code, prediction_year, emissions_data_path)
    # plot_ev_demand(state_name, state_code, prediction_year, ev_data_path)
    # plot_ev_emissions(state_name, prediction_year, ev_data_path, emissions_data_path)