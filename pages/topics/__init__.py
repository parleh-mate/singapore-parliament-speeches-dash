from dash import html, dcc, Input, Output
import dash_bootstrap_components as dbc
import plotly_express as px
import pandas as pd
import textwrap

from utils import PARTY_COLOURS, parliaments, parliament_sessions

def topics_layout():
    return html.Div(
        [
            html.H1("Parliamentary topics Analysis"),
            
            # Dropdowns Section
            dbc.Row([
                dbc.Col([
                    html.Label("Select a Parliament Session:"),
                    dcc.Dropdown(
                        id='parliament-dropdown-topics',
                        options=[{'label': session, 'value': session} for session in parliament_sessions],
                        value=parliament_sessions[0],  # Set default
                        placeholder='Select a parliament session',
                        searchable=False,
                        clearable=False
                    ),
                ], md=4),
                dbc.Col([
                    html.Label("Select a Constituency:"),
                    dcc.Dropdown(
                        id='constituency-dropdown-topics',
                        options=[],  # Will be populated via callback
                        value='All',
                        placeholder='Select a constituency',
                        searchable=False,
                        clearable=False
                    )
                ], md=4, id='constituency-dropdown-container-topics', style={'display': 'none'}),
                dbc.Col([
                    html.Label("Select a Member Name:"),
                    dcc.Dropdown(
                        id='member-dropdown-topics',
                        options=[],  # Will be populated via callback
                        value='All',
                        placeholder='Select a member name',
                        searchable=False,
                        clearable=False
                    )
                ], md=4),
            ], className="mb-4"),
                        dbc.Accordion(
                [
                    dbc.AccordionItem(
                        [
                            html.P(
                                [
                                    "Topics are assigned to speeches by GPT based on a set list of topics generated using a combination of unsupervised modeling and subjective human interpretation of model outputs. This is early stage work and we are working on engineering prompts or fine tuning models to return more valid results. More information can be found in the methodology section."
                                ]
                            )
                        ],
                        title=html.Span(
                            "How are topics derived?",
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
                        id='topics-graph',
                        config={"responsive": True},
                        style={'minHeight': '500px'}
                    )
                ], width=12)
            ]),
        ],
        className='content'
    )

def topics_callbacks(app, data):
    # Callback to control visibility of the Constituency dropdown
    @app.callback(
        Output('constituency-dropdown-container-topics', 'style'),
        Input('parliament-dropdown-topics', 'value')
    )
    def toggle_constituency_dropdown(selected_parliament):
        if selected_parliament != 'All':
            return {'display': 'block'}
        else:
            return {'display': 'none'}

    # Callback to update Constituency options based on selected session
    @app.callback(
        [Output('constituency-dropdown-topics', 'options'),
        Output('constituency-dropdown-topics', 'value')],
        Input('parliament-dropdown-topics', 'value')
    )
    def update_constituency_options(selected_parliament):
        if selected_parliament == 'All':
            # If 'All' is selected, reset options to include only 'All'
            return [{'label': 'All', 'value': 'All'}], 'All'
        topics_df = data['topics']
        
        # Filter the dataframe based on the selected parliament session
        topics_df = topics_df[topics_df['parliament'] == parliaments[selected_parliament]]
        # Get unique constituencies
        constituencies = sorted(topics_df['member_constituency'].unique())
        # Add 'All' option
        options = [{'label': 'All', 'value': 'All'}] + [{'label': const, 'value': const} for const in constituencies]
        return options, 'All'

    # Callback to update Member Name options based on selected session and constituency
    @app.callback(
        [Output('member-dropdown-topics', 'options'),
        Output('member-dropdown-topics', 'value')],
        [Input('parliament-dropdown-topics', 'value'),
        Input('constituency-dropdown-topics', 'value')]
    )
    def update_member_options(selected_parliament, selected_constituency):
        topics_df = data['topics']
        # Start with filtering by parliament session
        topics_df = topics_df[topics_df['parliament'] == parliaments[selected_parliament]]

        # Further filter by constituency if not 'All'
        if selected_constituency and selected_constituency != 'All':
            topics_df = topics_df[topics_df['member_constituency'] == selected_constituency]
        # Get unique member names
        members = sorted(topics_df['member_name'].unique())
        # Add 'All' option
        options = [{'label': 'All', 'value': 'All'}] + [{'label': member, 'value': member} for member in members]
        return options, 'All'

    # Callback to update the topics graph and table on Page 1
    @app.callback(
        Output('topics-graph', 'figure'),
        [Input('parliament-dropdown-topics', 'value'),
        Input('constituency-dropdown-topics', 'value'),
        Input('member-dropdown-topics', 'value')]
    )
    def update_graph_and_table(selected_parliament, selected_constituency, selected_member):

        topics_df = data['topics']

        # Filter by parliament
        topics_df = topics_df[topics_df['parliament'] == parliaments[selected_parliament]]
        
        # Further filter based on selected_constituency
        if selected_constituency != 'All' and selected_constituency:

            topics_df = topics_df[topics_df['member_constituency'] == selected_constituency]
        
        # Further filter based on selected_member
        if selected_member != 'All' and selected_member:

            topics_df = topics_df[topics_df['member_name'] == selected_member]

        # grouping and aggregation here instead of SQL to retain member name information for filtering first

        topics_df = topics_df.groupby(['member_party', 'topic_assigned']).agg({'count_speeches': 'sum'}).reset_index()

        topics_df['perc_speeches'] = topics_df['count_speeches']*100 / topics_df.groupby('member_party')['count_speeches'].transform('sum')

        # wrap text for later
        topics_df['topic_assigned'] = topics_df['topic_assigned'].apply(lambda x: '<br>'.join(textwrap.wrap(x, 30)))

        # ministry addressed graph

        # create orders manually

        orders = []
        for i in ['count_speeches', 'perc_speeches']:
            orders.append(topics_df.groupby('topic_assigned').sum().sort_values(i).index)

        count_order, prop_order = orders

        # Create the initial figure with count_speeches
        fig_count = px.bar(
            topics_df,
            x='count_speeches',
            y='topic_assigned',
            color='member_party',
            barmode='relative',
            color_discrete_map=PARTY_COLOURS,
            custom_data="member_party"
        )

        fig_count.update_traces(
            hovertemplate=
                '<b>%{y}</b><br>' +
                'Party: %{customdata[0]}<br>' +
                'Total Speeches: %{x}<extra></extra>'  # Removes the secondary box with trace name
        )

        # Create a separate figure for perc_speeches
        fig_prop = px.bar(
            topics_df,
            x='perc_speeches',
            y='topic_assigned',
            color='member_party',
            barmode='relative',
            color_discrete_map=PARTY_COLOURS,
            custom_data='member_party'
        )

        fig_prop.update_traces(
            hovertemplate=
                '<b>%{y}</b><br>' +
                'Party: %{customdata[0]}<br>' +
                'Percentage Speeches: %{x:.1f}<extra></extra>'  # Removes the secondary box with trace name
        )

        # Combine the two figures by adding traces from fig_prop to fig_count
        for trace in fig_prop.data:
            fig_count.add_trace(trace)

        # Total number of traces per view
        num_traces = len(fig_count.data) // 2

        # Initially, show only count traces and hide proportion traces
        for i, trace in enumerate(fig_count.data):
            if i >= num_traces:
                trace.visible = False

        # Define the buttons
        buttons = [
            dict(
                label="Count",
                method="update",
                args=[
                    {"visible": [True]*num_traces + [False]*num_traces},
                    {"title": "Speeches assigned to Topics",
                    "xaxis": {"title": "Speeches",
                            "showgrid": True,
                            "gridwidth": 1,
                            "gridcolor": 'LightGray'},
                    "yaxis": {
                            "title": "Ministry Addressed",
                            "categoryorder": "array",
                            "categoryarray": count_order,
                            "tickfont": {"size": 10}
                        }}
                ]
            ),
            dict(
                label="Percentage",
                method="update",
                args=[
                    {"visible": [False]*num_traces + [True]*num_traces},
                    {"title": "Speeches assigned to Topics",
                    "xaxis": {"title": "Percentage of Speeches",
                            "showgrid": True,
                            "gridwidth": 1,
                            "gridcolor": 'LightGray'},
                    "yaxis": {
                            "title": "Ministry Addressed",
                            "categoryorder": "array",
                            "categoryarray": prop_order,
                            "tickfont": {"size": 10}
                        }}
                ]
            )
        ]

        # Update the layout to include the buttons
        fig_count.update_layout(
            height=600,
            legend=dict(title=dict(text='Party'),
                        yanchor="bottom",
                        y=0,
                        xanchor="right",
                        x=0.99),
            margin=dict(l=0, r=0, t=80),
            updatemenus=[
                dict(
                    type="buttons",
                    direction="left",
                    buttons=buttons,
                    pad={"r": 10, "t": 10},
                    showactive=True,
                    x=1,
                    xanchor="right",
                    y=1,
                    yanchor="bottom"
                )
            ],
            title=dict(
                text="Speeches assigned to Topics",
            ),
            xaxis_title="Speeches",
            yaxis_title="Ministry Addressed",
            template='plotly_white'
        )

        fig_count.update_yaxes(
            categoryorder='array',
            categoryarray=count_order,
            tickfont=dict(
                size=10)
        )

        fig_count.update_xaxes(showgrid=True, gridwidth=1, gridcolor='LightGray')
        
        return fig_count