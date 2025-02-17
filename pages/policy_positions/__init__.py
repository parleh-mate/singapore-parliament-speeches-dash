from dash import html, dcc, Input, Output, State, callback_context
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate
from pinecone import Pinecone

from query_vectors import query_vector_embeddings, summarize_policy_positions
from utils import parliaments, try_again_message, top_k_rag_policy_positions, policy_positions_rag_index

# Filter out the 'All' parliament session
parliaments = {i: v for i, v in parliaments.items() if i != 'All'}

# pinecone client
pc = Pinecone()
index = pc.Index(policy_positions_rag_index)

# Layout for the Topic Summaries Page
def policy_positions_layout():
    return html.Div(
        [
            html.H1("Policy positions"),
            html.P("Generate a summary of a party, constituency, or MP's policy position on a given topic."),
            
            # Dropdowns Section
            dbc.Row([
                # Parliament Session Dropdown
                dbc.Col([
                    html.Label("Select a Parliament Session:"),
                    dcc.Dropdown(
                        id='parliament-dropdown-rag',
                        options=[{'label': session, 'value': session} for session in parliaments.keys()],
                        value=list(parliaments.keys())[-1],  # Set default to the last key
                        placeholder='Select a parliament session',
                        searchable=False,
                        clearable=False
                    ),
                ], md=3),
                
                # Party Dropdown
                dbc.Col([
                    html.Label("Select a Party:"),
                    dcc.Dropdown(
                        id='party-dropdown-rag',
                        options=[],  # Will be populated via callback
                        placeholder='Select a Party',
                        searchable=True,
                        clearable=False
                    )
                ], md=3),
                # Constituency Dropdown
                dbc.Col([
                    html.Label("Select a Constituency:"),
                    dcc.Dropdown(
                        id='constituency-dropdown-rag',
                        options=[],  # Will be populated via callback
                        placeholder='Defaults to all',
                        searchable=True,
                        clearable=False
                    )
                ], md=3),
                # Member Dropdown
                dbc.Col([
                    html.Label("Select a Member Name:"),
                    dcc.Dropdown(
                        id='member-dropdown-rag',
                        options=[],  # Will be populated via callback
                        placeholder='Defaults to all',
                        searchable=True,
                        clearable=False
                    )
                ], md=3),
            ], className="mb-4"),
             # Submit Button Row
            dbc.Row([
                dbc.Col([
                    dbc.InputGroup([
                        dbc.Input(
                            id='text-input-rag',
                            type='text',
                            placeholder='Enter query here e.g. "climate change"',
                        ),
                        dbc.Button(
                            "Submit",
                            id='submit-button-rag',
                            color='primary',
                            className='ms-2'
                        )
                    ])
                ], md=8),
                dbc.Col([
                    dbc.InputGroup([
                        dbc.Button(
                            "Reset Filters",
                            id='reset-button-rag',
                            color='secondary',
                            className='ms-2',
                            n_clicks=0
                        )
                    ])
                ], md=3),
            ], className="mb-4"),
            
            # Accordion Section
            dbc.Accordion(
                [
                    dbc.AccordionItem(
                        [
                            html.P(f"""
                                   All parliamentary speeches are first pre-summarized into shorter bullet points via a daily recurring process. When the user submits a query, the app fetches the {top_k_rag_policy_positions} most relevant pre-summarized speeches to the user's query - determined using text embeddings - and summarizes these again using GPT. Please refer to the methodology section for more info.""")
                        ],
                        title=html.Span(
                            "How are policy positions generated?",
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
            
            # Output Paragraph with Loading Icon
            dcc.Loading(
                id="loading-output-rag",
                type="circle",  # You can choose other types like 'circle', 'dot', etc.
                children=html.Div(id='output-paragraph-rag', className='mt-4'),
                style={'position': 'relative'}
            )
        ],
        className='content'
    )

def policy_positions_callbacks(app, data):

    # Callback to update Party options based on selected session
    @app.callback(
        [Output('party-dropdown-rag', 'options'),
         Output('party-dropdown-rag', 'value')],
        Input('parliament-dropdown-rag', 'value')
    )
    def update_party_options(selected_parliament):
        selection_options = data['demographics']
        if selected_parliament:
            parties = selection_options['member_party'][selection_options['parliament']==int(parliaments[selected_parliament])]

            parties = sorted(parties.unique())
            return parties, parties[0]
        # If no parliament selected, return empty options and no value
        return [], None
    
   # Combined callback to update Constituencies and Members
    @app.callback(
        [
            Output('constituency-dropdown-rag', 'options'),
            Output('constituency-dropdown-rag', 'value'),
            Output('member-dropdown-rag', 'options'),
            Output('member-dropdown-rag', 'value')
        ],
        [
            Input('parliament-dropdown-rag', 'value'),
            Input('party-dropdown-rag', 'value'),
            Input('constituency-dropdown-rag', 'value'),
            Input('member-dropdown-rag', 'value'),
            Input('reset-button-rag', 'n_clicks')
        ],
        prevent_initial_call=True
    )
    def update_constituency_and_member(selected_parliament, selected_party, selected_constituency, selected_member, reset_n_clicks):
        ctx = callback_context

        if not ctx.triggered:
            raise PreventUpdate  # Prevent callback from running if no input has triggered it

        trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]

        selection_options = data['demographics']

        # Filter by parliament
        if selected_parliament:
            selection_options = selection_options[
                selection_options['parliament'] == int(parliaments[selected_parliament])
            ]
        else:
            selection_options = selection_options.copy()

        # Filter by party
        if selected_party:
            selection_options = selection_options[
                selection_options['member_party'] == selected_party
            ]

        if trigger_id in ['parliament-dropdown-rag', 'party-dropdown-rag', 'reset-button-rag']:
            # When Parliament or Party is changed
            # Update Constituency options based on Parliament and Party
            constituencies = sorted(selection_options['member_constituency'].unique())
            constituency_options = [{'label': c, 'value': c} for c in constituencies]

            # Update Member options based on Parliament and Party (no constituency filter)
            members = sorted(selection_options['member_name'].unique())
            member_options = [{'label': m, 'value': m} for m in members]

            # Reset Constituency and Member selections to None
            new_selected_constituency = None
            new_selected_member = None

        elif trigger_id == 'constituency-dropdown-rag':
            if selected_constituency:
                # User changed constituency, update members accordingly
                filtered_members = selection_options[
                    selection_options['member_constituency'] == selected_constituency
                ]
                members = sorted(filtered_members['member_name'].unique())
                member_options = [{'label': m, 'value': m} for m in members]
            else:
                # If no Constituency is selected, show all Members based on Parliament and Party
                members = sorted(selection_options['member_name'].unique())
                member_options = [{'label': m, 'value': m} for m in members]

            # Constituency options remain unchanged
            constituencies = sorted(selection_options['member_constituency'].unique())
            constituency_options = [{'label': c, 'value': c} for c in constituencies]

            # Reset Member selection to None
            new_selected_constituency = selected_constituency
            new_selected_member = None

        elif trigger_id == 'member-dropdown-rag':
            if selected_member:
                # User changed member, automatically set constituency
                filtered_member = selection_options[
                    selection_options['member_name'] == selected_member
                ]
                if not filtered_member.empty:
                    new_selected_constituency = filtered_member.iloc[0]['member_constituency']
                    
                    # Update Constituency options based on Parliament and Party
                    constituencies = sorted(selection_options['member_constituency'].unique())
                    constituency_options = [{'label': c, 'value': c} for c in constituencies]

                    # Update Member options based on the new Constituency
                    filtered_members = selection_options[
                        selection_options['member_constituency'] == new_selected_constituency
                    ]
                    members = sorted(filtered_members['member_name'].unique())
                    member_options = [{'label': m, 'value': m} for m in members]

                    # Set Member selection to the selected member
                    new_selected_member = selected_member
                else:
                    # If selected member not found, prevent update
                    raise PreventUpdate
            else:
                # If no Member is selected, show all Members based on Parliament and Party
                members = sorted(selection_options['member_name'].unique())
                member_options = [{'label': m, 'value': m} for m in members]

                # Constituency options remain unchanged
                constituencies = sorted(selection_options['member_constituency'].unique())
                constituency_options = [{'label': c, 'value': c} for c in constituencies]

                # Reset Member selection to None
                new_selected_constituency = None
                new_selected_member = None
        else:
            # Unknown trigger, prevent update
            raise PreventUpdate

        # If no constituencies or members found, prevent updating
        if not constituency_options or not member_options:
            raise PreventUpdate

        return constituency_options, new_selected_constituency, member_options, new_selected_member
    
    @app.callback(
        Output('text-input-rag', 'value'),
        Input('reset-button-rag', 'n_clicks'),
        prevent_initial_call=True
    )
    def reset_text_input(reset_n_clicks):
        if reset_n_clicks:
            return ''
        raise PreventUpdate            

    # Callback to handle submit and display output paragraph
    @app.callback(
        Output('output-paragraph-rag', 'children'),
        Input('submit-button-rag', 'n_clicks'),
        State('parliament-dropdown-rag', 'value'),
        State('party-dropdown-rag', 'value'),
        State('constituency-dropdown-rag', 'value'),
        State('member-dropdown-rag', 'value'),
        State('text-input-rag', 'value')
    )
    def update_output(n_clicks, selected_parliament, selected_party, selected_constituency, selected_member, query):
        if n_clicks:
            if not query:
                return html.P("Please enter some text before submitting.")
            try:
                responses = query_vector_embeddings(query, top_k_rag_policy_positions, index, int(parliaments[selected_parliament]), selected_party, selected_constituency, selected_member)                
                summaries = [i['metadata']['policy_positions'] for i in responses]
                # get unit of analysis
                if selected_member:
                    uoa = 'MP'
                elif selected_constituency:
                    uoa = 'Constituency'
                else:
                    uoa = 'Party'
                output = summarize_policy_positions(query, uoa, summaries)
                # Ensure output has at least one element
                if output and len(output) > 0:
                    # Construct the returned text with Policy Position and Justification
                    if 'Your query did not return any relevant entries' in output[0]:
                        returned_text = html.P(try_again_message)
                    else:
                        returned_text = html.P([
                            html.H3("Policy Position"),
                            output[0],
                            html.Br(),
                            html.Br(),
                            html.H3('Proposed measures'),
                            html.Ul([html.Li(i.replace('- ', '', 1)) for i in output[1].split('\n')])
                            ]
                            )
                    return returned_text
                else:
                    return html.P("No summary available for the given input.")
            except Exception as e:
                # Handle potential errors gracefully
                return html.P(f"An error occurred: {str(e)}")
        # Return empty string if submit button hasn't been clicked
        return ""

