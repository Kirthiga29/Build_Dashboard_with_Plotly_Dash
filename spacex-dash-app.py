import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, Input, Output

# Load the dataset
spacex_df = pd.read_csv("spacex_launch_dash.csv")

# Initialize the Dash app
app = Dash(__name__)
# Define the app layout
app.layout = html.Div([
    html.H1("SpaceX Launch Dashboard", style={'textAlign': 'center', 'color': '#503D36', 'font-size': 40}),
    
    # TASK 1: Add a dropdown list to select Launch Site
    html.Div([
        html.Label("Select Launch Site:"),
        dcc.Dropdown(
            id='site-dropdown',
            options=[
                {'label': 'All Sites', 'value': 'ALL'},
                * [{'label': site, 'value': site} for site in spacex_df['Launch Site'].unique()]
            ],
            value='ALL',
            placeholder="Select a Launch Site here",
            searchable=True,
            style={'width': '80%', 'padding': '3px', 'font-size': '20px', 'text-align-last': 'center'}
        ),
    ], style={'margin-bottom': '30px'}),
    # TASK 2: Add a pie chart to show success rate
    dcc.Graph(id='success-pie-chart'),
    
    # TASK 3: Add a range slider for payload
    html.Div([
        html.Label("Payload Range (Kg):"),
        dcc.RangeSlider(
            id='payload-slider',
            min=0,
            max=10000,
            step=1000,
            marks={i: str(i) for i in range(0, 10001, 1000)},
            value=[spacex_df['Payload Mass (kg)'].min(), spacex_df['Payload Mass (kg)'].max()]
        ),
    ], style={'margin-bottom': '30px'}),
    
    # TASK 4: Add a scatter plot for payload vs. outcome
    dcc.Graph(id='success-payload-scatter-chart')
])

# TASK 2 & 4: Add callback functions
@app.callback(
    [Output(component_id='success-pie-chart', component_property='figure'),
     Output(component_id='success-payload-scatter-chart', component_property='figure')],
    [Input(component_id='site-dropdown', component_property='value'),
     Input(component_id='payload-slider', component_property='value')]
)
def update_charts(entered_site, payload_range):
    # Extract payload range
    min_payload, max_payload = payload_range
    
    # Filter dataframe based on payload range (always apply this filter)
    filtered_df = spacex_df[(spacex_df['Payload Mass (kg)'] >= min_payload) & 
                            (spacex_df['Payload Mass (kg)'] <= max_payload)].copy()
    
    # Further filter by site if not ALL
    if entered_site != 'ALL':
        filtered_df = filtered_df[filtered_df['Launch Site'] == entered_site]
    
    # TASK 2: Updated Pie Chart Logic
    if entered_site == 'ALL':
        # For ALL sites: Show successful launches (class=1) count per launch site
        success_counts = filtered_df[filtered_df['class'] == 1].groupby('Launch Site').size().reset_index(name='Success Count')
        fig_pie = px.pie(
            success_counts,
            values='Success Count',
            names='Launch Site',
            title='Successful Launches by Launch Site'
        )
        fig_pie.update_traces(textposition='inside', textinfo='percent+label')
    else:
        # For specific site: Show success vs. failure counts
        class_counts = filtered_df['class'].value_counts().reset_index()
        class_counts['class'] = class_counts['class'].map({1: 'Success', 0: 'Failure'})
        fig_pie = px.pie(
            class_counts,
            values='count',
            names='class',
            title=f'Success vs. Failure for {entered_site}'
        )
        fig_pie.update_traces(textposition='inside', textinfo='percent+label')
    
    # TASK 4: Scatter plot for payload vs. outcome (filtered by site and payload)
    scatter_df = filtered_df if entered_site == 'ALL' else filtered_df
    fig_scatter = px.scatter(
        scatter_df,
        x='Payload Mass (kg)',
        y='class',
        color='Booster Version Category',
        title=f'Payload Mass vs. Launch Outcome for {"All Sites" if entered_site == "ALL" else entered_site}',
        labels={'class': 'Launch Outcome (1=Success, 0=Failure)'}
    )
    fig_scatter.update_layout(
        yaxis=dict(tickmode='array', tickvals=[0, 1], ticktext=['Failure', 'Success'])
    )
    fig_scatter.update_xaxes(title_text='Payload Mass (kg)')
    fig_scatter.update_yaxes(title_text='Launch Outcome')
    
    return fig_pie, fig_scatter

# Run the app
if __name__ == '__main__':
    app.run(debug=True, port=8050)