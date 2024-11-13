from dash import html, dcc, Input, Output, dash_table
import dash_bootstrap_components as dbc

from utils import parliaments, parliament_sessions


def summaries_layout():
    return html.Div(
        [
            html.H1("Parliamentary Speeches Analysis"),            
            
            # Dropdowns Section
            dbc.Row([
                # Updated Column with Info Tooltip
                dbc.Col([
                    # Container for the Label and Info Icon
                    html.Div(
                        [
                            html.Label("Select a Parliament Session:"),
                            html.Span(
                                # Info Icon (Bootstrap Icons)
                                html.I(
                                    className="bi bi-info-circle",  # Bootstrap Icon classes
                                    id="summaries-parliament-session-info-icon",  # Unique ID for the tooltip
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
                    
                    # Dropdown Component
                    dcc.Dropdown(
                        id='parliament-dropdown-summaries',
                        options=[{'label': session, 'value': session} for session in parliament_sessions],
                        value='All',  # Set default to 'All'
                        placeholder='Select a parliament session',
                        searchable=False,
                        clearable=False
                    ),
                    
                    # Tooltip Component
                    dbc.Tooltip(
                        "'All' takes the average across all parliamentary sittings from the 12th parliament to current",
                        target="summaries-parliament-session-info-icon",  # Link tooltip to the icon's ID
                        placement="right",                      # Position the tooltip to the right of the icon
                        style={
                            "maxWidth": "300px",
                            "textAlign": "left"  # Ensure text is left-aligned within the tooltip
                        }
                    )
                ], md=4),
                
                # Second Dropdown Column
                dbc.Col([
                    html.Label("Select a Constituency:"),
                    dcc.Dropdown(
                        id='constituency-dropdown-summaries',
                        options=[],  # Will be populated via callback
                        value='All',
                        placeholder='Select a constituency',
                        searchable=True,
                        clearable=False
                    )
                ], md=4, id='constituency-dropdown-container-summaries', style={'display': 'none'}),
                
                # Third Dropdown Column
                dbc.Col([
                    html.Label("Select a Member Name:"),
                    dcc.Dropdown(
                        id='member-dropdown-summaries',
                        options=[],  # Will be populated via callback
                        value='All',
                        placeholder='Select a member name',
                        searchable=True,
                        clearable=False
                    )
                ], md=4),
            ], className="mb-4"),
            
            # Accordion Section
            dbc.Accordion(
                [
                    dbc.AccordionItem(
                        [
                            html.P(
                                [
                                    "Speeches refers to any time a member speaks to address the chamber as recorded in the parliamentary Hansard. This includes substantial and procedural points but does not include written answers, parliamentary questions, or the President's address. Members who made no speeches do not appear on the graph.",
                                    html.Br(),
                                    html.Br(),
                                    "To assess how readable a speech is, we use the Flesch-Kincaid score, a well-known index for measuring how difficult a text is to understand in English. The index scales from 0 to 100, with 0 indicating extremely difficult and 100 very easy. Generally, a score of between 30-50 is a college level text, while 10-30 is college-graduate level. The full formula and interpretation guide can be found in the methodology section. Members who did not speak do not have a readability score and will not appear on the graph. Vernacular speeches are also not given a readability score since the index only works for English. Please refer to the methodology for more info."
                                ]
                            )
                        ],
                        title=html.Span(
                            "How are speech and readability score defined?",
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
            
            # Table Section with Scroll
            dbc.Row([
                dbc.Col([
                    html.H2([
                        "Speech Summaries",
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
                    style={"display": "flex", "alignItems": "center"}),
                    
                    # Tooltip Component
                    dbc.Tooltip(
                        "Speech summaries and topics generated using GPT. Only a subset of speeches are summarised and labelled. Please refer to the methodology for more info.",
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
                        filter_action='native',
                    )
                ], width=12)
            ], className="mt-4"),
        ],
        className='content'
    )


def summaries_callbacks(app, data):
    # Callback to control visibility of the Constituency dropdown
    @app.callback(
        Output('constituency-dropdown-container-summaries', 'style'),
        Input('parliament-dropdown-summaries', 'value')
    )
    def toggle_constituency_dropdown(selected_parliament):
        if selected_parliament != 'All':
            return {'display': 'block'}
        else:
            return {'display': 'none'}

    # Callback to update Constituency options based on selected session
    @app.callback(
        [Output('constituency-dropdown-summaries', 'options'),
        Output('constituency-dropdown-summaries', 'value')],
        Input('parliament-dropdown-summaries', 'value')
    )
    def update_constituency_options(selected_parliament):
        if selected_parliament == 'All':
            # If 'All' is selected, reset options to include only 'All'
            return [{'label': 'All', 'value': 'All'}], 'All'
        speech_summary_df = data['speech_summaries']
        # Filter the dataframe based on the selected parliament session
        speech_summary_df= speech_summary_df[speech_summary_df['parliament'] == parliaments[selected_parliament]]
        # Get unique constituencies
        constituencies = sorted(speech_summary_df['member_constituency'].unique())
        # Add 'All' option
        options = [{'label': 'All', 'value': 'All'}] + [{'label': const, 'value': const} for const in constituencies]
        return options, 'All'

    # Callback to update Member Name options based on selected session and constituency
    @app.callback(
        [Output('member-dropdown-summaries', 'options'),
        Output('member-dropdown-summaries', 'value')],
        [Input('parliament-dropdown-summaries', 'value'),
        Input('constituency-dropdown-summaries', 'value')]
    )
    def update_member_options(selected_parliament, selected_constituency):
        speech_summary_df = data['speech_agg']
        # Start with filtering by parliament session
        speech_summary_df = speech_summary_df[speech_summary_df['parliament'] == parliaments[selected_parliament]]
        # Further filter by constituency if not 'All'
        if selected_constituency and selected_constituency != 'All':
            speech_summary_df = speech_summary_df[speech_summary_df['member_constituency'] == selected_constituency]
        # Get unique member names
        members = sorted(speech_summary_df['member_name'].unique())
        # Add 'All' option
        options = [{'label': 'All', 'value': 'All'}] + [{'label': member, 'value': member} for member in members]
        return options, 'All'

    # Callback to update the summaries graph and table on Page 1
    @app.callback(
        Output('speech-summary-table', 'data'),
        [Input('parliament-dropdown-summaries', 'value'),
        Input('constituency-dropdown-summaries', 'value'),
        Input('member-dropdown-summaries', 'value')]
    )
    def update_graph_and_table(selected_parliament, selected_constituency, selected_member):
        speech_summary_df = data['speech_summaries']

        if selected_parliament != 'All' and selected_parliament:
            speech_summary_df = speech_summary_df[speech_summary_df['parliament'] == int(parliaments[selected_parliament])]
        
        # Further filter based on selected_constituency
        if selected_constituency != 'All' and selected_constituency:
            speech_summary_df = speech_summary_df[speech_summary_df['member_constituency'] == selected_constituency]
        
        # Further filter based on selected_member
        if selected_member != 'All' and selected_member:
            speech_summary_df = speech_summary_df[speech_summary_df['member_name'] == selected_member]
        
        # Prepare table data
        table_data = speech_summary_df.to_dict('records')
        
        return table_data