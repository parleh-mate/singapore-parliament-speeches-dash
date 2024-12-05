from dash import html, dcc, Input, Output
import dash_bootstrap_components as dbc
import plotly_express as px


from utils import PARTY_COLOURS, parliaments, parliament_sessions
from pages.topics_questions.utils import group_and_aggregate, filter_data_by_filters

def topics_questions_layout():
    return html.Div(
        [
            html.H1("Topics and Questions"),
            
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
                                    id="topics-questions-parliament-session-info-icon",  # Unique ID for the tooltip
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
                        target="topics-questions-parliament-session-info-icon",  # Link tooltip to the icon's ID
                        placement="right",                      # Position the tooltip to the right of the icon
                        style={
                            "maxWidth": "300px",
                            "textAlign": "left"  # Ensure text is left-aligned within the tooltip
                        }
                    ),
                    dcc.Dropdown(
                        id='parliament-dropdown-topics-questions',
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
                        id='constituency-dropdown-topics-questions',
                        options=[],  # Will be populated via callback
                        value='All',
                        placeholder='Select a constituency',
                        searchable=True,
                        clearable=False
                    )
                ], md=4, id='constituency-dropdown-container-topics-questions', style={'display': 'none'}),
                dbc.Col([
                    html.Label("Select a Member Name:"),
                    dcc.Dropdown(
                        id='member-dropdown-topics-questions',
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
                        id='topics-assigned-graph',
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

def topics_questions_callbacks(app, data):
    # Callback to control visibility of the Constituency dropdown
    @app.callback(
        Output('constituency-dropdown-container-topics-questions', 'style'),
        Input('parliament-dropdown-topics-questions', 'value')
    )
    def toggle_constituency_dropdown(selected_parliament):
        if selected_parliament != 'All':
            return {'display': 'block'}
        else:
            return {'display': 'none'}

    # Callback to update Constituency options based on selected session
    @app.callback(
        [Output('constituency-dropdown-topics-questions', 'options'),
        Output('constituency-dropdown-topics-questions', 'value')],
        Input('parliament-dropdown-topics-questions', 'value')
    )
    def update_constituency_options(selected_parliament):
        if selected_parliament == 'All':
            # If 'All' is selected, reset options to include only 'All'
            return [{'label': 'All', 'value': 'All'}], 'All'
        options_df = data['member_metrics']
        
        # Filter the dataframe based on the selected parliament session
        options_df = options_df[options_df['parliament'] == parliaments[selected_parliament]]
        # Get unique constituencies
        constituencies = sorted(options_df['member_constituency'].unique())
        # Add 'All' option
        options = [{'label': 'All', 'value': 'All'}] + [{'label': const, 'value': const} for const in constituencies]
        return options, 'All'

    # Callback to update Member Name options based on selected session and constituency
    @app.callback(
        [Output('member-dropdown-topics-questions', 'options'),
        Output('member-dropdown-topics-questions', 'value')],
        [Input('parliament-dropdown-topics-questions', 'value'),
        Input('constituency-dropdown-topics-questions', 'value')]
    )
    def update_member_options(selected_parliament, selected_constituency):
        options_df = data['member_metrics']
        # Start with filtering by parliament session
        options_df = options_df[options_df['parliament'] == parliaments[selected_parliament]]

        # Further filter by constituency if not 'All'
        if selected_constituency and selected_constituency != 'All':
            options_df = options_df[options_df['member_constituency'] == selected_constituency]
        # Get unique member names
        members = sorted(options_df['member_name'].unique())
        # Add 'All' option
        options = [{'label': 'All', 'value': 'All'}] + [{'label': member, 'value': member} for member in members]
        return options, 'All'

    # Callback to update the questions graph and table on Page 1
    @app.callback(
        [Output('topics-assigned-graph', 'figure'),
        Output('questions-ministry-graph', 'figure')],
        [Input('parliament-dropdown-topics-questions', 'value'),
        Input('constituency-dropdown-topics-questions', 'value'),
        Input('member-dropdown-topics-questions', 'value')]
    )
    def update_graph_and_table(selected_parliament, selected_constituency, selected_member):

        # get data
        selected_parliament = parliaments[selected_parliament]

        questions_ministry_df = filter_data_by_filters(data, 'questions', selected_parliament, selected_constituency, selected_member)
        topics_df = filter_data_by_filters(data, 'topics', selected_parliament, selected_constituency, selected_member)

        # grouping and aggregation here instead of SQL to retain member name information for filtering first        
        topics_df = group_and_aggregate(topics_df, 'topic_assigned', 'count_topic_speeches', 'perc_speeches')
        questions_ministry_df = group_and_aggregate(questions_ministry_df, 'ministry_addressed', 'count_questions_ministry', 'perc_questions')

        # speech topics graph
        # create orders manually

        orders = []
        for i in ['perc_speeches', 'count_topic_speeches']:
            orders.append(topics_df.groupby('topic_assigned').sum().sort_values(i).index)

        prop_order, count_order = orders

        fig_topics_prop = px.bar(
            topics_df,
            x='perc_speeches',
            y='topic_assigned',
            color='member_party',
            barmode='relative',
            color_discrete_map=PARTY_COLOURS,
            custom_data='member_party'
        )

        fig_topics_prop.update_traces(
            hovertemplate=
                '<b>%{y}</b><br>' +
                'Party: %{customdata[0]}<br>' +
                'Percentage Speeches: %{x:.1f}<extra></extra>'  # Removes the secondary box with trace name
        )

        fig_topics_count = px.bar(
            topics_df,
            x='count_topic_speeches',
            y='topic_assigned',
            color='member_party',
            barmode='relative',
            color_discrete_map=PARTY_COLOURS,
            custom_data="member_party"
        )

        fig_topics_count.update_traces(
            hovertemplate=
                '<b>%{y}</b><br>' +
                'Party: %{customdata[0]}<br>' +
                'Total Speeches: %{x}<extra></extra>'  # Removes the secondary box with trace name
        )

        # Combine the two figures by adding traces from fig_prop to fig_count
        for trace in fig_topics_count.data:
            fig_topics_prop.add_trace(trace)

        # Total number of traces per view
        num_traces = len(fig_topics_prop.data) // 2

        # Initially, show only count traces and hide proportion traces
        for i, trace in enumerate(fig_topics_prop.data):
            if i >= num_traces:
                trace.visible = False

        # Define the buttons
        buttons = [
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
            ),
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
            )
        ]

        # Update the layout to include the buttons
        fig_topics_prop.update_layout(
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

        fig_topics_prop.update_yaxes(
            categoryorder='array',
            categoryarray=prop_order,
            tickfont=dict(
                size=10)
        )

        fig_topics_prop.update_xaxes(showgrid=True, gridwidth=1, gridcolor='LightGray')

        # ministry addressed graph

        # create orders manually

        orders = []
        for i in ['perc_questions', 'count_questions_ministry']:
            orders.append(questions_ministry_df.groupby('ministry_addressed').sum().sort_values(i).index)

        prop_order, count_order = orders

        fig_questions_prop = px.bar(
            questions_ministry_df,
            x='perc_questions',
            y='ministry_addressed',
            color='member_party',
            barmode='relative',
            color_discrete_map=PARTY_COLOURS,
            custom_data='member_party'
        )

        fig_questions_prop.update_traces(
            hovertemplate=
                '<b>%{y}</b><br>' +
                'Party: %{customdata[0]}<br>' +
                'Percentage Questions: %{x:.1f}<extra></extra>'  # Removes the secondary box with trace name
        )

        fig_questions_count = px.bar(
            questions_ministry_df,
            x='count_questions_ministry',
            y='ministry_addressed',
            color='member_party',
            barmode='relative',
            color_discrete_map=PARTY_COLOURS,
            custom_data="member_party"
        )

        fig_questions_count.update_traces(
            hovertemplate=
                '<b>%{y}</b><br>' +
                'Party: %{customdata[0]}<br>' +
                'Total Questions: %{x}<extra></extra>'  # Removes the secondary box with trace name
        )

        # Combine the two figures by adding traces from fig_prop to fig_count
        for trace in fig_questions_count.data:
            fig_questions_prop.add_trace(trace)

        # Total number of traces per view
        num_traces = len(fig_questions_prop.data) // 2

        # Initially, show only count traces and hide proportion traces
        for i, trace in enumerate(fig_questions_prop.data):
            if i >= num_traces:
                trace.visible = False

        # Define the buttons
        buttons = [
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
            ),
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
            )
        ]

        # Update the layout to include the buttons
        fig_questions_prop.update_layout(
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

        fig_questions_prop.update_yaxes(
            categoryorder='array',
            categoryarray=prop_order,
            tickfont=dict(
                size=10)
        )

        fig_questions_prop.update_xaxes(showgrid=True, gridwidth=1, gridcolor='LightGray')
        
        return fig_topics_prop, fig_questions_prop