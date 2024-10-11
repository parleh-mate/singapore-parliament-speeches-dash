import plotly.express as px
from dash import html, dcc, Input, Output
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np

from utils import PARTY_COLOURS, parliaments, parliament_sessions
from load_data import get_data

parliaments_demo = {i:v for i,v in parliaments.items() if i!='All'}

parliament_sessions_demo = [i for i in parliament_sessions if i!="All"]

# demographics layout with dropdowns, graph, and table
def demographics_layout():
    return html.Div(
        [
            html.H1("Parliamentary demographics Analysis"),
            
            # Dropdowns Section
            dbc.Row([
                dbc.Col([
                    html.Label("Select a Parliament Session:"),
                    dcc.Dropdown(
                        id='parliament-dropdown-demographics',
                        options=[{'label': session, 'value': session} for session in parliament_sessions_demo],
                        value=parliament_sessions_demo[0],  # Set default
                        placeholder='Select a parliament session',
                        searchable=False,
                        clearable=False
                    ),
                ], md=4),
            ], className="mb-4"),
            
            # Graph Section with Fixed Height
            dbc.Row([
                dbc.Col([
                    dcc.Graph(
                        id='demographics-age-graph',
                        config={"responsive": True},
                        style={'minHeight': '500px'}
                    )
                ], width=6),

                dbc.Col([
                    dcc.Graph(
                        id='demographics-ethnicity-graph',
                        config={"responsive": True},
                        style={'minHeight': '500px'}
                    )
                ], width=6)
            ]),
        ],
        className='content'
    )

def demographics_callbacks(app):
    # Callback to update the demographics graph and table on Page 1
    @app.callback(
        [Output('demographics-age-graph', 'figure'),
        Output('demographics-ethnicity-graph', 'figure')],
        Input('parliament-dropdown-demographics', 'value')
    )
    def update_graph_and_table(selected_parliament):
        demographics_df = get_data()['demographics']

        # Filter by parliament
        demographics_df = demographics_df[demographics_df['parliament'] == int(parliaments_demo[selected_parliament])]    
        
        # age histogram
        # Create the histogram
        age_histogram = px.histogram(
            demographics_df,
            x='year_age_entered',
            color='party', 
            title='Age at year of first sitting',
            opacity=0.75,
            histnorm='probability',
            color_discrete_map=PARTY_COLOURS,
            barmode='group'
        )

        # Set the size of each bin to 5
        age_histogram.update_traces(xbins=dict(size=5))

        # Adjust the y-axis title
        age_histogram.update_yaxes(title_text="Proportion")

        # Find the minimum and maximum multiples of 5 for tick marks
        min_tick = (np.floor(demographics_df['year_age_entered'].min() / 5) * 5)-5
        max_tick = (np.ceil(demographics_df['year_age_entered'].max() / 5) * 5)+5

        # Create tick values, but exclude the first one (to avoid overlapping with 0)
        tickvals = np.arange(min_tick, max_tick + 1, 5)
        tickvals = tickvals[tickvals != min_tick]  # Remove the first tick to prevent it from overlapping with 0

        # Adjust the x-axis to show ticks in increments of 5, but skip the first one
        age_histogram.update_xaxes(title_text="Year-age at first sitting",
                                   tick0=min_tick, 
                                   dtick=5, 
                                   tickvals=tickvals, 
                                   range=[min_tick, max_tick])

        # ethnicity and gender graph

        ethnicity_df = demographics_df.groupby(['party', 'member_ethnicity', 'gender'])['member_name'].count().reset_index().rename(columns = {"member_name": "count"})

        ethnicity_df['proportion'] = ethnicity_df['count'] / ethnicity_df.groupby('party')['count'].transform('sum')

        custom_order = ['chinese', 'malay', 'indian', 'others']
        ethnicity_df['member_ethnicity'] = pd.Categorical(ethnicity_df['member_ethnicity'], categories=custom_order, ordered=True)

        ethnicity_df = ethnicity_df.sort_values('member_ethnicity')

        # Create x-axis structure: ethnicity (x[0]) and party (x[1]) information
        x = [list(ethnicity_df['member_ethnicity'].values), list(ethnicity_df['party'].values)]

        # Create figure
        ethnicity_fig = go.Figure()

        # Define patterns for genders
        gender_patterns = {'F': '/', 'M': ''}

        # Loop through gender and set patterns for each
        for gender, pattern in gender_patterns.items():
            # Create a temporary dataframe where the current gender is active
            df_tmp = ethnicity_df.mask(ethnicity_df['gender'] != gender, pd.NA)

            # Loop through parties and add bars
            for party in ethnicity_df['party'].unique():
                # Mask the data for the current party
                y = df_tmp['proportion'].mask(ethnicity_df['party'] != party, pd.NA)

                # Add a trace for each party and gender
                ethnicity_fig.add_bar(
                    x=x,  # X-axis is ethnicity and party combination
                    y=y,  # Proportion as the y value
                    name=f'{party} - {gender}',  # Trace name
                    hovertext=ethnicity_df['gender'],  # Display gender info in hover
                    marker_pattern_shape=pattern,  # Apply the pattern based on gender
                    marker_color=PARTY_COLOURS[party],  # Use the custom color for the party
                    hovertemplate="Ethnicity: %{x[0]}<br>" +
                                "Party: %{x[1]}<br>" +
                                "Proportion: %{y}<br>" +
                                "Gender: %{hovertext}<extra></extra>"
                )

        # Final layout adjustments
        ethnicity_fig.update_layout(
            barmode='relative',  # Group the bars by party
            title='Ethnicity and Gender',
            xaxis_title='Ethnicity',
            yaxis_title='Proportion',
            showlegend=True,
            legend=dict(
                title=dict(text='Party - Gender'),
                yanchor="top",
                y=0.99,
                xanchor="right",
                x=0.99
            )
        )       
        
        return age_histogram, ethnicity_fig