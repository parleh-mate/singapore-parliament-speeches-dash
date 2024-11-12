from dash import html, dcc, Input, Output
import dash_bootstrap_components as dbc
import plotly_express as px
import plotly.graph_objects as go
import numpy as np
import textwrap

from utils import PARTY_COLOURS, parliaments, parliament_sessions

def questions_layout():
    return html.Div(
        [
            html.H1("Parliamentary questions Analysis"),
            
            # Dropdowns Section
            dbc.Row([
                dbc.Col([
                    # Container for the Label and Info Icon
                    html.Div(
                        [
                            html.Label("Select a Parliament Session:"),
                            html.Span(
                                # Info Icon (Bootstrap Icons)
                                html.I(
                                    className="bi bi-info-circle",  # Bootstrap Icon classes
                                    id="questions_parliament-session-info-icon",  # Unique ID for the tooltip
                                    style={
                                        "margin-left": "5px",          # Space between label and icon
                                        "cursor": "pointer",           # Pointer cursor on hover
                                        "color": "#17a2b8",            # Bootstrap's info color
                                        "fontSize": "1rem"             # Icon size
                                    }
                                    # Removed aria_label as it may not be supported directly
                                )
                            )
                        ],
                        style={"display": "flex", "alignItems": "center"}  # Align label and icon vertically
                    ),
                                        # Tooltip Component
                    dbc.Tooltip(
                        "'All' takes the average across all parliamentary sittings from the 12th parliament to current",
                        target="questions_parliament-session-info-icon",  # Link tooltip to the icon's ID
                        placement="right",                      # Position the tooltip to the right of the icon
                        style={
                            "maxWidth": "300px",
                            "textAlign": "left"  # Ensure text is left-aligned within the tooltip
                        }
                    ),
                    dcc.Dropdown(
                        id='parliament-dropdown-questions',
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
                        id='constituency-dropdown-questions',
                        options=[],  # Will be populated via callback
                        value='All',
                        placeholder='Select a constituency',
                        searchable=True,
                        clearable=False
                    )
                ], md=4, id='constituency-dropdown-container-questions', style={'display': 'none'}),
                dbc.Col([
                    html.Label("Select a Member Name:"),
                    dcc.Dropdown(
                        id='member-dropdown-questions',
                        options=[],  # Will be populated via callback
                        value='All',
                        placeholder='Select a member name',
                        searchable=True,
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
                                    "Questions refer to parliamentary questions in which members direct inquiries specifically to ministries. Cabinet ministers do not raise questions. Please refer to the methodology for more info."
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
                        id='questions-asked-graph',
                        config={"responsive": True},
                        style={'minHeight': '500px'}
                    )
                ], xs=12, md=6, className="mb-4"),

                dbc.Col([
                    dcc.Graph(
                        id='questions-ministry-graph',
                        config={"responsive": True},
                        style={'minHeight': '500px'}
                    )
                ], xs=12, md=6, className="mb-4")
            ]),
        ],
        className='content'
    )

def questions_callbacks(app, data):
    # Callback to control visibility of the Constituency dropdown
    @app.callback(
        Output('constituency-dropdown-container-questions', 'style'),
        Input('parliament-dropdown-questions', 'value')
    )
    def toggle_constituency_dropdown(selected_parliament):
        if selected_parliament != 'All':
            return {'display': 'block'}
        else:
            return {'display': 'none'}

    # Callback to update Constituency options based on selected session
    @app.callback(
        [Output('constituency-dropdown-questions', 'options'),
        Output('constituency-dropdown-questions', 'value')],
        Input('parliament-dropdown-questions', 'value')
    )
    def update_constituency_options(selected_parliament):
        if selected_parliament == 'All':
            # If 'All' is selected, reset options to include only 'All'
            return [{'label': 'All', 'value': 'All'}], 'All'
        questions_df = data['questions']
        
        # Filter the dataframe based on the selected parliament session
        questions_df = questions_df[questions_df['parliament'] == parliaments[selected_parliament]]
        # Get unique constituencies
        constituencies = sorted(questions_df['member_constituency'].unique())
        # Add 'All' option
        options = [{'label': 'All', 'value': 'All'}] + [{'label': const, 'value': const} for const in constituencies]
        return options, 'All'

    # Callback to update Member Name options based on selected session and constituency
    @app.callback(
        [Output('member-dropdown-questions', 'options'),
        Output('member-dropdown-questions', 'value')],
        [Input('parliament-dropdown-questions', 'value'),
        Input('constituency-dropdown-questions', 'value')]
    )
    def update_member_options(selected_parliament, selected_constituency):
        questions_df = data['questions']
        # Start with filtering by parliament session
        questions_df = questions_df[questions_df['parliament'] == parliaments[selected_parliament]]

        # Further filter by constituency if not 'All'
        if selected_constituency and selected_constituency != 'All':
            questions_df = questions_df[questions_df['member_constituency'] == selected_constituency]
        # Get unique member names
        members = sorted(questions_df['member_name'].unique())
        # Add 'All' option
        options = [{'label': 'All', 'value': 'All'}] + [{'label': member, 'value': member} for member in members]
        return options, 'All'

    # Callback to update the questions graph and table on Page 1
    @app.callback(
        [Output('questions-asked-graph', 'figure'),
        Output('questions-ministry-graph', 'figure')],
        [Input('parliament-dropdown-questions', 'value'),
        Input('constituency-dropdown-questions', 'value'),
        Input('member-dropdown-questions', 'value')]
    )
    def update_graph_and_table(selected_parliament, selected_constituency, selected_member):
        questions_ministry_df = data['questions']
        questions_asked_df = data['speech_agg']

        # Filter by parliament
        questions_asked_df_highlighted = questions_asked_df[questions_asked_df['parliament'] == parliaments[selected_parliament]]
        full_questions_asked_df = questions_asked_df_highlighted.copy()

        questions_ministry_df = questions_ministry_df[questions_ministry_df['parliament'] == parliaments[selected_parliament]]
        
        # Further filter based on selected_constituency
        if selected_constituency != 'All' and selected_constituency:
            questions_asked_df_highlighted = questions_asked_df_highlighted[questions_asked_df_highlighted['member_constituency'] == selected_constituency]

            questions_ministry_df = questions_ministry_df[questions_ministry_df['member_constituency'] == selected_constituency]
        
        # Further filter based on selected_member
        if selected_member != 'All' and selected_member:
            questions_asked_df_highlighted = questions_asked_df_highlighted[questions_asked_df_highlighted['member_name'] == selected_member]

            questions_ministry_df = questions_ministry_df[questions_ministry_df['member_name'] == selected_member]

        questions_asked_df_non_highlighted = full_questions_asked_df.drop(questions_asked_df_highlighted.index)

        # grouping and aggregation here instead of SQL to retain member name information for filtering first

        questions_ministry_df = questions_ministry_df.groupby(['member_party', 'ministry_addressed']).agg({'count_questions': 'sum'}).reset_index()

        questions_ministry_df['perc_questions'] = questions_ministry_df['count_questions']*100 / questions_ministry_df.groupby('member_party')['count_questions'].transform('sum')

        # wrap text for later
        questions_ministry_df['ministry_addressed'] = questions_ministry_df['ministry_addressed'].apply(lambda x: '<br>'.join(textwrap.wrap(x, 30)))

        # start with boxplot + scatterplot
        unique_parties = sorted(full_questions_asked_df['member_party'].unique())
        party_to_num = {party: idx for idx, party in enumerate(unique_parties)}

        fig_scatter = go.Figure()

        # plot boxplot across all datapoints for each party

        for party in unique_parties:
            plot_df = questions_asked_df[questions_asked_df['member_party'] == party]
            fig_scatter.add_trace(
                go.Box(
                    x=plot_df['member_party'].map(party_to_num),  # Set numerical x position
                    y=plot_df['questions_per_sitting'],
                    name='', 
                    marker_color=PARTY_COLOURS[party],  
                    boxpoints=False, 
                    line=dict(color=PARTY_COLOURS[party]),
                    showlegend=False 
                )
            )

        # now add points for non highlighted points; scatter preferred to strip because of customizability

        for party in questions_asked_df_non_highlighted['member_party'].unique():
            # Filter data for the current non-highlighted party
            plot_df = questions_asked_df_non_highlighted[questions_asked_df_non_highlighted['member_party'] == party]
            
            # Numerical position for the current party
            party_num = party_to_num[party]
            
            # Add Scatter Trace for Individual Points of the Non-Highlighted Party (Grey Points) with Jitter
            jitter = np.random.uniform(-0.1, 0.1, size=len(plot_df)) 
            scatter_x = [party_num + j for j in jitter]
            
            fig_scatter.add_trace(
                go.Scatter(
                    x=scatter_x,  # Apply jitter to numerical x positions
                    y=plot_df['questions_per_sitting'],
                    mode='markers',
                    marker=dict(
                        color='grey',        # Grey color for non-highlighted points
                        opacity=0.2
                    ),
                    hoverinfo='skip',      # Disable hover
                    name='',                
                    showlegend=False 
                )
            )

        # add highlighted points last

        for party in questions_asked_df_highlighted['member_party'].unique():
            # Filter data for the current highlighted party
            plot_df = questions_asked_df_highlighted[questions_asked_df_highlighted['member_party'] == party]
            
            # Numerical position for the current party
            party_num = party_to_num[party]
            
            # Add Scatter Trace for Individual Points of the Highlighted Party with Jitter
            jitter = np.random.uniform(-0.1, 0.1, size=len(plot_df))  # Adjust jitter range as needed
            scatter_x = [party_num + j for j in jitter]
            
            fig_scatter.add_trace(
                go.Scatter(
                    x=scatter_x,  # Apply jitter to numerical x positions
                    y=plot_df['questions_per_sitting'],
                    mode='markers',
                    marker=dict(
                        color=plot_df['member_party'].map(PARTY_COLOURS),
                        opacity=0.6
                    ),
                    hovertext=(
                        "Member: " + plot_df['member_name'] + "<br>" +
                        "Party: " + plot_df['member_party'] + "<br>" +
                        "Questions: " + plot_df['questions_per_sitting'].astype(str)
                    ),
                    hoverinfo='text',
                    customdata=plot_df[['member_name']],  # Pass member names for hover
                    name=party, 
                    showlegend=True 
                )
            )


        # customize layout

        fig_scatter.update_layout(
            height=600,
            legend=dict(title=dict(text='Party'),
                        yanchor="top",
                        orientation='h',
                        y=1.1,
                        xanchor="left",
                        x=0),
            margin=dict(l=0, r=0),
            title='Questions per Sitting by Party',
            xaxis_title='Party',
            yaxis_title='Questions per Sitting',
            template='plotly_white',
            boxmode='overlay',  # Overlay boxes; consistent with your adjustment
            xaxis=dict(
                tickmode='array',
                tickvals=list(party_to_num.values()),  # Numerical positions
                ticktext=list(party_to_num.keys())    # Party names as labels
            )
        )

        # ministry addressed graph

        # create orders manually

        orders = []
        for i in ['count_questions', 'perc_questions']:
            orders.append(questions_ministry_df.groupby('ministry_addressed').sum().sort_values(i).index)

        count_order, prop_order = orders

        # Create the initial figure with count_questions
        fig_count = px.bar(
            questions_ministry_df,
            x='count_questions',
            y='ministry_addressed',
            color='member_party',
            barmode='relative',
            color_discrete_map=PARTY_COLOURS,
            custom_data="member_party"
        )

        fig_count.update_traces(
            hovertemplate=
                '<b>%{y}</b><br>' +
                'Party: %{customdata[0]}<br>' +
                'Total Questions: %{x}<extra></extra>'  # Removes the secondary box with trace name
        )

        # Create a separate figure for perc_questions
        fig_prop = px.bar(
            questions_ministry_df,
            x='perc_questions',
            y='ministry_addressed',
            color='member_party',
            barmode='relative',
            color_discrete_map=PARTY_COLOURS,
            custom_data='member_party'
        )

        fig_prop.update_traces(
            hovertemplate=
                '<b>%{y}</b><br>' +
                'Party: %{customdata[0]}<br>' +
                'Percentage Questions: %{x:.1f}<extra></extra>'  # Removes the secondary box with trace name
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
                    {"title": "Questions addressed to Ministries",
                    "xaxis": {"title": "Questions",
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
                    {"title": "Questions addressed to Ministries",
                    "xaxis": {"title": "Percentage of Questions",
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
                text="Questions addressed to Ministries",
            ),
            xaxis_title="Questions",
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
        
        return fig_scatter, fig_count