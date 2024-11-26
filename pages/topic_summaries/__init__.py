from dash import html, dcc, Input, Output, State
import dash_bootstrap_components as dbc

from query_vectors import query_vector_embeddings, summarize_policy_positions
from utils import parliaments, parliament_parties, top_k_rag

# Filter out the 'All' parliament session
parliaments = {i: v for i, v in parliaments.items() if i != 'All'}

# Layout for the Topic Summaries Page
def topic_summaries_layout():
    return html.Div(
        [
            html.H1("Topic RAG summaries"),
            
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
                ], md=4),
                
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
                ], md=4, id='party-dropdown-container-rag'),
                
                # Text Input
                dbc.Col([
                    html.Label("Enter Query:"),
                    dbc.Input(
                        id='text-input-rag',
                        type='text',
                        placeholder='Enter your query here',
                    )
                ], md=4),
            ], className="mb-4"),
            
            # Accordion Section
            dbc.Accordion(
                [
                    dbc.AccordionItem(
                        [
                            html.P("Blaa blaa blaa")
                        ],
                        title=html.Span(
                            "How to understand this page?",
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
            
            # Submit Button Row
            dbc.Row([
                dbc.Col([
                    dbc.Button(
                        "Submit",
                        id='submit-button-rag',
                        color='primary',
                        className='mt-2'
                    )
                ], md=4)
            ], className="mb-4"),  # Moved className outside the children list
            
            # Output Paragraph with Loading Icon
            dcc.Loading(
                id="loading-output-rag",
                type="default",  # You can choose other types like 'circle', 'dot', etc.
                children=html.Div(id='output-paragraph-rag', className='mt-4'),
                style={'position': 'relative'}
            )
        ],
        className='content'
    )

def topic_summaries_callbacks(app):

    # Callback to update Party options based on selected session
    @app.callback(
        [Output('party-dropdown-rag', 'options'),
         Output('party-dropdown-rag', 'value')],
        Input('parliament-dropdown-rag', 'value')
    )
    def update_party_options(selected_parliament):
        if selected_parliament:
            # Retrieve parties for the selected parliament session
            parties = parliament_parties.get(parliaments[selected_parliament], [])
            # Format options for the dropdown
            formatted_parties = [{'label': party, 'value': party} for party in parties]
            # Set the default selected party to the first in the list
            default_party = formatted_parties[0]['value'] if formatted_parties else None
            return formatted_parties, default_party
        # If no parliament selected, return empty options and no value
        return [], None

    # Callback to handle submit and display output paragraph
    @app.callback(
        Output('output-paragraph-rag', 'children'),
        Input('submit-button-rag', 'n_clicks'),
        State('parliament-dropdown-rag', 'value'),
        State('party-dropdown-rag', 'value'),
        State('text-input-rag', 'value')
    )
    def update_output(n_clicks, selected_parliament, selected_party, query):
        if n_clicks:
            if not query:
                return html.P("Please enter some text before submitting.")
            try:
                summaries = query_vector_embeddings(query, top_k_rag, int(parliaments[selected_parliament]), selected_party)
                output = summarize_policy_positions(query, summaries)
                # Ensure output has at least one element
                if output and len(output) > 0:
                    # Construct the returned text with Policy Position and Justification
                    returned_text = html.P([
                            html.H3("Policy Position"),
                            output[0],
                            html.Br(),
                            html.Br(),
                            html.H3('Justification'),
                            html.Ul([html.Li(i.replace('- ', '', 1)) for i in output[1].split('\n')])
                        ]),   
                    return returned_text
                else:
                    return html.P("No summary available for the given input.")
            except Exception as e:
                # Handle potential errors gracefully
                return html.P(f"An error occurred: {str(e)}")
        # Return empty string if submit button hasn't been clicked
        return ""