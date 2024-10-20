from dash import html, dcc, Input, Output, dash_table
import dash_bootstrap_components as dbc
import plotly.graph_objects as go

from utils import PARTY_COLOURS, parliaments, parliament_sessions

# speeches layout with dropdowns, graph, and table
def speeches_layout():
    return html.Div(
        [
            html.H1("Parliamentary Speeches Analysis"),            
            # Dropdowns Section
            dbc.Row([
                dbc.Col([
                    html.Label("Select a Parliament Session:"),
                    dcc.Dropdown(
                        id='parliament-dropdown',
                        options=[{'label': session, 'value': session} for session in parliament_sessions],
                        value='All',  # Set default to 'All'
                        placeholder='Select a parliament session',
                        searchable=False,
                        clearable=False
                    ),
                ], md=4),
                
                dbc.Col([
                    html.Label("Select a Constituency:"),
                    dcc.Dropdown(
                        id='constituency-dropdown',
                        options=[],  # Will be populated via callback
                        value='All',
                        placeholder='Select a constituency',
                        searchable=False,
                        clearable=False
                    )
                ], md=4, id='constituency-dropdown-container', style={'display': 'none'}),
                
                dbc.Col([
                    html.Label("Select a Member Name:"),
                    dcc.Dropdown(
                        id='member-dropdown',
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
                    [html.P("Speeches refers to any time a member speaks (substantial or procedural) with the exception of parliamentary questions. Questions refer to parliamentary questions in which members direct inquiries specifically to ministries. Cabinet ministers do not raise questions. Please refer to the methodology for more info.")],
                    title=html.Span(
                        "How is a speech or question defined?",
                        style={
                            "fontWeight": "bold",
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
                        id='speeches-graph',
                        config={"responsive": True},
                        style={'minHeight': '500px'}
                    )
                ], width=12)
            ]),
            
            # Table Section with Scroll
            dbc.Row([
                dbc.Col([
                    html.H2(["Speech Summaries",
                             html.Span(
                                 html.I(
                                     className="bi bi-info-circle",
                                        id="summary-info-icon",
                                        style={
                                            "margin-left": "10px",
                                            "cursor": "pointer",
                                            "color": "#17a2b8"  # Optional: Bootstrap info color
                                        }
                                    )
                                )
                            ],
                            style={"display": "flex", "alignItems": "center"}
                        ),                            
                            # Tooltip Component
                            dbc.Tooltip(
                                html.Div("Speech summaries and topics generated using GPT. Only a subset of speeches are summarised and labelled. Please refer to the methodology for more info.",
                                         style={"textAlign": "left"}),
                                target="summary-info-icon",
                                placement="right",
                                style={"maxWidth": "300px"}  # Optional: Adjust tooltip width
                            ),
                    dash_table.DataTable(
                        id='speech-summary-table',
                        columns=[
                            {"name": "Parl.no", "id": "parliament"},
                            {"name": "Date", "id": "date"},
                            {"name": "Party", "id": "member_party"},
                            {"name": "Constituency", "id": "member_constituency"},
                            {"name": "Member Name", "id": "member_name"},
                            {"name": "Topic Assigned", "id": "topic_assigned"},
                            {"name": "Speech Summary", "id": "speech_summary"},
                        ],
                        data=[],  # Will be populated via callback
                        page_size=10,
                        style_table={'overflowX': 'auto', 'maxHeight': '400px', 'overflowY': 'auto'},
                        style_cell={
                            'textAlign': 'left',
                            'whiteSpace': 'normal',
                            'overflow': 'hidden',
                            'textOverflow': 'ellipsis',
                            'fontSize': '12px',
                            'fontFamily': 'Roboto, sans-serif'
                        },
                        style_cell_conditional=[
                            {
                                'if': {'column_id': 'speech_summary'},
                                'width': '77%',
                            },
                            {
                                'if': {'column_id': 'parliament'},
                                'width': '5%',
                                'minWidth': '75px',
                                'maxWidth': '100px',
                            },
                            {
                                'if': {'column_id': 'date'},
                                'width': '5%',
                                'minWidth': '75px',
                                'maxWidth': '100px',
                            },
                            {
                                'if': {'column_id': 'member_party'},
                                'width': '3%',
                                'minWidth': '30px',
                                'maxWidth': '100px',
                            },
                            {
                                'if': {'column_id': 'member_constituency'},
                                'width': '5%',
                                'minWidth': '75px',
                                'maxWidth': '110px',
                            },
                            {
                                'if': {'column_id': 'member_name'},
                                'width': '5%',
                                'minWidth': '75px',
                                'maxWidth': '100px',
                            },
                            {
                                'if': {'column_id': 'topic_assigned'},
                                'width': '5%',
                                'minWidth': '75px',
                                'maxWidth': '100px',
                            },
                        ],
                        style_data={'height': 'auto'},
                    )
                ], width=12)
            ], className="mt-4"),
        ],
        className='content'
    )


def speeches_callbacks(app, data):
    # Callback to control visibility of the Constituency dropdown
    @app.callback(
        Output('constituency-dropdown-container', 'style'),
        Input('parliament-dropdown', 'value')
    )
    def toggle_constituency_dropdown(selected_parliament):
        if selected_parliament != 'All':
            return {'display': 'block'}
        else:
            return {'display': 'none'}

    # Callback to update Constituency options based on selected session
    @app.callback(
        [Output('constituency-dropdown', 'options'),
        Output('constituency-dropdown', 'value')],
        Input('parliament-dropdown', 'value')
    )
    def update_constituency_options(selected_parliament):
        if selected_parliament == 'All':
            # If 'All' is selected, reset options to include only 'All'
            return [{'label': 'All', 'value': 'All'}], 'All'
        speech_agg_df = data['speech_agg']
        # Filter the dataframe based on the selected parliament session
        speech_agg_df = speech_agg_df[speech_agg_df['parliament'] == parliaments[selected_parliament]]
        # Get unique constituencies
        constituencies = sorted(speech_agg_df['member_constituency'].unique())
        # Add 'All' option
        options = [{'label': 'All', 'value': 'All'}] + [{'label': const, 'value': const} for const in constituencies]
        return options, 'All'

    # Callback to update Member Name options based on selected session and constituency
    @app.callback(
        [Output('member-dropdown', 'options'),
        Output('member-dropdown', 'value')],
        [Input('parliament-dropdown', 'value'),
        Input('constituency-dropdown', 'value')]
    )
    def update_member_options(selected_parliament, selected_constituency):
        speech_agg_df = data['speech_agg']
        # Start with filtering by parliament session
        speech_agg_df = speech_agg_df[speech_agg_df['parliament'] == parliaments[selected_parliament]]
        # Further filter by constituency if not 'All'
        if selected_constituency and selected_constituency != 'All':
            speech_agg_df = speech_agg_df[speech_agg_df['member_constituency'] == selected_constituency]
        # Get unique member names
        members = sorted(speech_agg_df['member_name'].unique())
        # Add 'All' option
        options = [{'label': 'All', 'value': 'All'}] + [{'label': member, 'value': member} for member in members]
        return options, 'All'

    # Callback to update the speeches graph and table on Page 1
    @app.callback(
        [Output('speeches-graph', 'figure'),
        Output('speech-summary-table', 'data')],
        [Input('parliament-dropdown', 'value'),
        Input('constituency-dropdown', 'value'),
        Input('member-dropdown', 'value')]
    )
    def update_graph_and_table(selected_parliament, selected_constituency, selected_member):
        speech_agg_df = data['speech_agg']
        speech_summary_df = data['speech_summaries']

        # Define minimum and maximum marker sizes in pixels
        SIZE_MIN = 5
        SIZE_MAX = 40

        # Calculate the global minimum and maximum of 'words_per_speech'
        global_min = speech_agg_df['words_per_speech'].min()
        global_max = speech_agg_df['words_per_speech'].max()

        # Define a scaling function
        def scale_marker_size(x, min_val, max_val, size_min, size_max):
            if max_val == min_val:
                return (size_min + size_max) / 2
            else:
                return size_min + (x - min_val) / (max_val - min_val) * (size_max - size_min)

        speech_agg_df['marker_size'] = speech_agg_df['words_per_speech'].apply(
            lambda x: scale_marker_size(x, global_min, global_max, SIZE_MIN, SIZE_MAX)
        )

        # Filter by parliament        
        speech_agg_df = speech_agg_df[speech_agg_df['parliament'] == parliaments[selected_parliament]]

        if selected_parliament != 'All' and selected_parliament:
            speech_summary_df = speech_summary_df[speech_summary_df['parliament'] == int(parliaments[selected_parliament])]
        
        # Further filter based on selected_constituency
        if selected_constituency != 'All' and selected_constituency:
            speech_agg_df_highlighted = speech_agg_df[speech_agg_df['member_constituency'] == selected_constituency]
            speech_summary_df = speech_summary_df[speech_summary_df['member_constituency'] == selected_constituency]
        
        # Further filter based on selected_member
        if selected_member != 'All' and selected_member:
            speech_agg_df_highlighted = speech_agg_df_highlighted[speech_agg_df_highlighted['member_name'] == selected_member]
            speech_summary_df = speech_summary_df[speech_summary_df['member_name'] == selected_member]

        if selected_constituency=='All' and selected_member=='All':
            speech_agg_df_highlighted = speech_agg_df

        speech_agg_df_non_highlighted = speech_agg_df.drop(speech_agg_df_highlighted.index)        
        
        # Create the scatter plot
        fig = go.Figure()

        for party in speech_agg_df_highlighted.member_party.unique():

            plot_df = speech_agg_df_highlighted.query(f"member_party=='{party}'")
            fig.add_trace(go.Scatter(
                x=plot_df['speeches_per_sitting'],
                y=plot_df['questions_per_sitting'],
                mode='markers',
                marker=dict(
                    color=[PARTY_COLOURS[i] for i in plot_df.member_party],
                    size=plot_df['marker_size'],
                    opacity=0.6
                ),
                hovertext="Member: " + plot_df['member_name'] + "<br>" +
                            "Party: " + plot_df['member_party'] + "<br>" +
                            "Speeches: " + plot_df['speeches_per_sitting'].astype(str) + "<br>" +
                            "Questions: " + plot_df['questions_per_sitting'].astype(str) + "<br>" +
                            "Words per Speech: " + plot_df['words_per_speech'].astype(str),
                hoverinfo='text',
                name=party,
                showlegend=True  # Only the highlighted trace shows in legend
            ))
            
        fig.add_trace(go.Scatter(
            x=speech_agg_df_non_highlighted['speeches_per_sitting'],
            y=speech_agg_df_non_highlighted['questions_per_sitting'],
            mode='markers',
            marker=dict(
                color='grey',
                size=speech_agg_df_non_highlighted['marker_size'],
                opacity=0.2
            ),
            hoverinfo='skip',  # Disable hover for non-highlighted points
            showlegend=False  # Non-highlighted trace doesn't show in legend
        ))


        fig.update_layout(
            title=f'Questions vs. Speeches per Sitting - Parliament {selected_parliament}' + '<br>' + '<span style="font-size:12px; color:grey">Point size corresponds to average no. of words per speech</span>',
            xaxis_title="Speeches per Sitting",
            yaxis_title="Questions per Sitting",
            legend=dict(
                title=dict(text='Party'),
                yanchor="top",
                y=0.99,
                xanchor="right",
                x=0.99
            ),
            template='plotly_white'
        )
        
        # Prepare table data
        table_data = speech_summary_df.to_dict('records')
        
        return fig, table_data