import plotly.express as px
from dash import html, dcc, Input, Output
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from scipy.stats import gaussian_kde, norm

from utils import PARTY_COLOURS, ETHNIC_COLOURS, parliaments, parliament_sessions

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
            dbc.Accordion(
                [
                    dbc.AccordionItem(
                        [
                            html.P(
                                [
                                    "The graph on the left shows the age distribution of members within each party. Because we do not have exact member birth dates, age is taken as a member's age in the year of their first sitting for that parliament session. The bars on the percentage plot show the porportion of members within a party that have members that fall into a certain age bin, while the density plot is a smoothed probability distribution. Derived probabilities (Y-axis) on the density plot are redacted since these are irrelevant quantities.",
                                    html.Br(),
                                    html.Br(),
                                    "The graph on the right shows the ethnic and gender distribution of members within each party. Solid bars refer to male members, and striped bars to female members. For example, in the 13th parliament, 27.8% of all NMPs were Chinese males, while 5.6% were Indian females. Please refer to the methodology for more info."
                                ]
                            )
                        ],
                        title=html.Span(
                            "How to understand these graphs?",
                            style={
                                "fontWeight": "bold",
                                "fontSize": "1.1rem"  # Optional: Increase font size
                            }
                        )
                    )
                ],
                start_collapsed=True,
                flush=True,
                className="border border-primary"
            ),
            
            # Graph Section with Fixed Height
            dbc.Row([
                dbc.Col([
                    dcc.Graph(
                        id='demographics-age-graph',
                        config={"responsive": True},
                        style={'minHeight': '500px'}
                    )
                ], xs=12, md=6, className="mb-4"),

                dbc.Col([
                    dcc.Graph(
                        id='demographics-ethnicity-graph',
                        config={"responsive": True},
                        style={'minHeight': '500px'}
                    )
                ], xs=12, md=6, className="mb-4")
            ]),
        ],
        className='content'
    )

def demographics_callbacks(app, data):
    # Callback to update the demographics graph and table on Page 1
    @app.callback(
        [Output('demographics-age-graph', 'figure'),
        Output('demographics-ethnicity-graph', 'figure')],
        Input('parliament-dropdown-demographics', 'value')
    )
    def update_graph_and_table(selected_parliament):
        demographics_df = data['demographics']

        # Filter by parliament
        demographics_df = demographics_df[demographics_df['parliament'] == int(parliaments_demo[selected_parliament])]

        # add all parties
        demographics_hist_df = pd.concat([demographics_df, demographics_df.assign(party='All')])
        
        # age histogram
        # Create the histogram
        age_histogram = px.histogram(
            demographics_hist_df,
            x='year_age_entered',
            color='member_party', 
            opacity=0.75,
            histnorm='percent',
            color_discrete_map=PARTY_COLOURS,
            barmode='group'
        )

        # Set the size of each bin to 5
        age_histogram.update_traces(xbins=dict(size=5))

        # Adjust the x-axis to show ticks in increments of 5, but skip the first one
        age_histogram.update_xaxes(title_text="Year-age at first sitting")
        
        age_histogram.update_layout(legend=dict(
                                        title=dict(text='Party'),
                                        yanchor="top",
                                        y=0.99,
                                        xanchor="left",
                                        x=0.01
                                        ))

        age_histogram.update_traces(
            hovertemplate="<b>Year Age Entered:</b> %{x}<br>" +
            "<b>Percentage:</b> %{y:.1f}<extra></extra>"
            )
        
        # now the density plot 

        age_density = go.Figure()

        # Loop through each party and calculate KDE
        unique_parties = list(demographics_df['member_party'].unique())
        unique_parties.append("All")
        
        for party in unique_parties:
            # Filter the data for each party
            if party=="All":
                party_data = demographics_df['year_age_entered']
            else:
                party_data = demographics_df[demographics_df['member_party'] == party]['year_age_entered']
                
            buffer = 15

            if len(party_data)!=1:
            
                # Calculate KDE with custom bandwidth
                kde = gaussian_kde(party_data, bw_method=0.2)
                
                # Extend the x range slightly beyond the min and max to allow smooth tails
                x_min = np.max([party_data.min() - buffer, 20])
                x_max = np.min([party_data.max() + buffer, 100])
                x_range = np.linspace(x_min, x_max, 1000)
                
                # Evaluate KDE
                kde_values = kde(x_range)
            else:                
                # kde not possible with single value; use pdf and generate distribution
                val = party_data.iloc[0]
                std_dev = 2  # Adjust this value to control the spread of the peak

                # Create x range for the "KDE-like" plot
                x_range = np.linspace(np.max([val-buffer, 20]), np.min([val+buffer, 100]), 1000)  # A range around the single value

                # Calculate the normal distribution (PDF) for the single value
                kde_values = norm.pdf(x_range, loc=party_data, scale=std_dev)
            
            # Add filled density curve to plot
            age_density.add_trace(go.Scatter(
                x=x_range, 
                y=kde_values,
                mode='lines',
                name=party,
                line=dict(color=PARTY_COLOURS[party], width=2),
                fill='tozeroy',  # Fill the area under the curve
                hovertemplate="<b>Age:</b> %{x:.0f}<br>" +
                              f"<b>Party:</b> {party}<extra></extra>"
            ))

        # now combine histogram and density plots

        # Initialize a new figure
        combined_fig = go.Figure()

        # Add histogram traces
        for trace in age_histogram.data:
            combined_fig.add_trace(trace)

        # Add KDE traces
        for trace in age_density.data:
            combined_fig.add_trace(trace)

        # Determine the number of traces for each plot
        num_hist_traces = len(age_histogram.data)
        num_kde_traces = len(age_density.data)

        # axes tick marks

        # Find the minimum and maximum multiples of 5 for tick marks
        min_tick = (np.floor(demographics_df['year_age_entered'].min() / 5) * 5)-5
        max_tick = (np.ceil(demographics_df['year_age_entered'].max() / 5) * 5)+5

        # Create tick values, but exclude the first one (to avoid overlapping with 0)
        tickvals = [i for i in np.arange(min_tick, max_tick + 1, 5) if i!=min_tick]


        # Create buttons
        buttons = [
            dict(
                label="Density",
                method="update",
                args=[
                    {"visible": [False]*num_hist_traces + [True]*num_kde_traces},
                    {
                        "title": "Age Distribution by Party",
                        "xaxis": {"title": "Year-age at first sitting",
                                  "tick0": min_tick,
                                  "dtick": 5,
                                  "tickvals": tickvals,
                                  "range": [min_tick, max_tick]
                                  },
                        "yaxis": {"title": "Density",
                                  "ticks": "",
                                  "showticklabels": False}
                    }
                ]
            ),
            dict(
                label="Percentage",
                method="update",
                args=[
                    {"visible": [True]*num_hist_traces + [False]*num_kde_traces},
                    {
                        "title": "Age Distribution by Party",
                        "xaxis": {"title": "Year-age at first sitting",
                                  "tick0": min_tick,
                                  "dtick": 5,
                                  "tickvals": tickvals,
                                  "range": [min_tick, max_tick]
                                  },
                        "yaxis": {"title": "Percentage"}
                    }
                ]
            )
        ]

        # Update the layout with buttons
        combined_fig.update_layout(
            updatemenus=[
                dict(
                    type="buttons",
                    direction="left",
                    buttons=buttons,
                    pad={"r": 10, "t": 10},
                    showactive=True,
                    x=0.99,
                    xanchor="right",
                    y=1.2,
                    yanchor="top"
                )
            ]
        )

        combined_fig.update_xaxes(
            tick0=min_tick,
            dtick=5,
            tickvals=tickvals,
            range=[min_tick, max_tick]
            )

        # Set initial visibility (e.g., show histogram by default)
        for i in range(num_hist_traces):
            combined_fig.data[i].visible = False
        for i in range(num_kde_traces):
            combined_fig.data[num_hist_traces + i].visible = True

        # Optionally, update axes and layout as needed
        combined_fig.update_layout(
            xaxis_title="Year-age at first sitting",
            yaxis_title="Density",
            title="Age Distribution by Party",
            margin=dict(l=0, r=0),
            legend=dict(
                title=dict(text='Party'),
                yanchor="top",
                y=0.99,
                xanchor="left",
                x=0.01
            ),
            template='plotly_white'
        )

        combined_fig.update_yaxes(ticks = "",
                                  showticklabels= False)

        # ethnicity and gender graph

        ethnicity_parties = demographics_df.groupby(['member_party', 'member_ethnicity', 'gender'])['member_name'].count().reset_index().rename(columns = {"member_name": "count"})

        all_parties = list(ethnicity_parties.member_party.unique())
        all_parties.sort(reverse=True)
        all_parties.append('All')

        # get for all parties
        ethnicity_all = demographics_df.groupby(['member_ethnicity', 'gender'])['member_name'].count().reset_index().rename(columns = {"member_name": "count"})

        ethnicity_all['member_party'] = 'All'

        ethnicity_df = pd.concat([ethnicity_parties, ethnicity_all])

        ethnicity_df['percentage'] = ethnicity_df['count']*100 / ethnicity_df.groupby('member_party')['count'].transform('sum')

        ethnicity_df['member_ethnicity'] = pd.Categorical(ethnicity_df['member_ethnicity'], categories=['chinese', 'malay', 'indian', 'others'], ordered=True)

        ethnicity_df = ethnicity_df.sort_values('member_ethnicity')

        ethnicity_fig = px.bar(
            ethnicity_df, 
            x="percentage", 
            y="member_party", 
            custom_data=["member_ethnicity", "gender", "count"],
            color="member_ethnicity",
            pattern_shape="gender",
            pattern_shape_sequence=["", "x"],
            category_orders={"gender": ["M", "F"]},
            color_discrete_map=ETHNIC_COLOURS
            )

        ethnicity_fig.update_layout(
            title='Ethnic and Gender Distribution by Party',
            yaxis_title='Party',
            xaxis_title='Percentage',
            showlegend=True,
            margin=dict(l=0, r=0),
            legend=dict(
                title=dict(text='Ethnicity, Gender')
            ),
            #yaxis={'categoryorder': 'total ascending'},
            yaxis = {"categoryorder": 'array',
                     "categoryarray": all_parties},
            template='plotly_white'
                )    
        
        ethnicity_fig.update_traces(
            hovertemplate=
                'Ethnicity: %{customdata[0]}<br>' +
                'Gender: %{customdata[1]}<br>' +
                'Party: %{y}<br>' +
                'Percentage: %{x:.1f}<br>' +
                'Count:  %{customdata[2]}<extra></extra>'  # Removes the secondary box with trace name
        )
 
        return combined_fig, ethnicity_fig