# Import required libraries
import pandas as pd
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[
    html.H1('SpaceX Launch Records Dashboard',
            style={'textAlign': 'center', 'color': '#503D36',
                   'font-size': 40}),
    # TASK 1: Add a dropdown list to enable Launch Site selection
    dcc.Dropdown(
        id='site-dropdown',
        options=[
            {'label': 'All Sites', 'value': 'ALL'},
            {'label': 'CCAFS LC-40', 'value': 'CCAFS LC-40'},
            {'label': 'VAFB SLC-4E', 'value': 'VAFB SLC-4E'},
            {'label': 'KSC LC-39A', 'value': 'KSC LC-39A'},
            {'label': 'CCAFS SLC-40', 'value': 'CCAFS SLC-40'}
        ],
        value='ALL',  # Default value
        placeholder="Select a Launch Site here",
        searchable=True
    ),
    html.Br(),
    
    # TASK 2: Add a pie chart to show the total successful launches count for all sites
    dcc.Graph(id='success-pie-chart'),
    
    # TASK 3: Add Range Slider to select Payload Mass range
    html.Label('Select Payload Range (Kg):'),
    dcc.RangeSlider(
        id='payload-slider',
        min=0, max=10000, step=1000,
        marks={i: str(i) for i in range(0, 10001, 2000)},  # Set labels every 2000 Kg
        value=[min_payload, max_payload]  # Set the default range to min and max payload
    ),
    
    html.Br(),
    
    # Graph to display the success scatter plot
    dcc.Graph(id='payload-success-scatter')
])

# Callback function for updating the pie chart based on selected dropdown value
@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value')
)
def get_pie_chart(entered_site):
    filtered_df = spacex_df  # Original DataFrame
    
    # If ALL sites are selected
    if entered_site == 'ALL':
        fig = px.pie(
            filtered_df, 
            values='class',  # Count success (1) and failure (0)
            names='Launch Site',  # Group by 'Launch Site'
            title='Total Successful Launches by Site'
        )
        return fig

    # If a specific site is selected
    else:
        site_data = filtered_df[filtered_df['Launch Site'] == entered_site]
        site_data = site_data['class'].value_counts().reset_index()
        site_data.columns = ['class', 'count']
        fig = px.pie(
            site_data,
            values='count',
            names='class',
            title=f"Total Success and Failure for Site {entered_site}"
        )
        return fig

# Callback function for updating the scatter plot based on selected dropdown and payload range
@app.callback(
    Output(component_id='payload-success-scatter', component_property='figure'),
    [
        Input(component_id='site-dropdown', component_property='value'),
        Input(component_id='payload-slider', component_property='value')
    ]
)
def update_scatter_plot(selected_site, selected_payload_range):
    # Extract the minimum and maximum payload values from the selected payload range
    min_payload, max_payload = selected_payload_range

    # Filter the dataframe based on the selected site and payload range
    filtered_df = spacex_df[(spacex_df['Payload Mass (kg)'] >= min_payload) & 
                             (spacex_df['Payload Mass (kg)'] <= max_payload)]
    
    if selected_site != 'ALL':
        # If a specific site is selected, filter further by site
        filtered_df = filtered_df[filtered_df['Launch Site'] == selected_site]

    # Create a scatter plot with Payload Mass vs. Launch Outcome (class) and color by Booster Version Category
    fig = px.scatter(
        filtered_df, 
        x='Payload Mass (kg)', 
        y='class', 
        color='Booster Version Category',
        title=f'Payload vs Launch Outcome for {selected_site if selected_site != "ALL" else "All Sites"}',
        labels={'class': 'Launch Outcome (Success=1, Failure=0)', 'Payload Mass (kg)': 'Payload Mass (kg)'}
    )
    
    return fig

# Run the app
if __name__ == '__main__':
    app.run_server()
