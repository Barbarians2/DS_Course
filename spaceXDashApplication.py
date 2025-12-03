# Import required libraries
import pandas as pd
import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create options for the Launch Site dropdown
launch_sites = spacex_df['Launch Site'].unique().tolist()
dropdown_options = [{'label': 'All Sites', 'value': 'ALL'}]
for site in launch_sites:
    dropdown_options.append({'label': site, 'value': site})

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                dcc.Dropdown(id='site-dropdown',
                                             options=dropdown_options,
                                             value='ALL',
                                             placeholder="Select a Launch Site here",
                                             searchable=True
                                ),
                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):", style={'padding-top': '20px'}),
                                
                                # TASK 3: Add a slider to select payload range
                                dcc.RangeSlider(id='payload-slider',
                                                min=0, max=10000, step=1000,
                                                marks={i: f'{i}' for i in range(0, 10001, 1000)},
                                                value=[min_payload, max_payload]
                                ),
                                html.Br(),

                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])



# TASK 2: Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value')
)
def get_pie_chart(entered_site):
    if entered_site == 'ALL':
        # Calculate total success and failure for all sites
        total_success = spacex_df[spacex_df['class'] == 1].shape[0]
        total_failure = spacex_df[spacex_df['class'] == 0].shape[0]

        # Pie chart for ALL sites
        fig = px.pie(
            values=[total_success, total_failure],
            names=['Success (1)', 'Failure (0)'],
            title='Total Success vs. Failure Launches for All Sites',
            color_discrete_sequence=['green', 'red']
        )
        return fig
    else:
        # Filter data for the selected site
        filtered_df = spacex_df[spacex_df['Launch Site'] == entered_site]
        
        # Calculate success and failure counts for the specific site
        class_counts = filtered_df['class'].value_counts().reset_index()
        class_counts.columns = ['class', 'count']

        # Pie chart for the specific site
        fig = px.pie(
            class_counts,
            values='count',
            names='class',
            title=f'Launch Outcomes for Site: {entered_site}',
            color='class',
            color_discrete_map={0: 'red', 1: 'green'}
        )
        return fig


# TASK 4: Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [Input(component_id='site-dropdown', component_property='value'),
     Input(component_id='payload-slider', component_property='value')]
)
def get_scatter_chart(entered_site, payload_range):
    low, high = payload_range

    # Filter data based on the payload range selected by the slider
    filtered_payload_df = spacex_df[
        (spacex_df['Payload Mass (kg)'] >= low) & 
        (spacex_df['Payload Mass (kg)'] <= high)
    ]

    if entered_site != 'ALL':
        # Filter further by the selected launch site
        filtered_payload_df = filtered_payload_df[
            filtered_payload_df['Launch Site'] == entered_site
        ]
        title_text = f'Payload vs. Launch Outcome for Site: {entered_site}'
    else:
        title_text = 'Payload vs. Launch Outcome for All Sites'

    # Create the scatter plot
    fig = px.scatter(
        filtered_payload_df,
        x='Payload Mass (kg)',
        y='class',
        color='Booster Version Category', # Color coded by Booster Version
        title=title_text,
        hover_data=['Launch Site'],
    )
        
    return fig


# Run the app
if __name__ == '__main__':
    app.run(debug=True)
