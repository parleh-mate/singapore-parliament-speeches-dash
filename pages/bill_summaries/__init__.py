from dash import html, dcc, Input, Output, State, callback_context, ALL, MATCH
import dash_bootstrap_components as dbc
import pandas as pd
from pinecone import Pinecone

from query_vectors import query_vector_embeddings
from utils import parliaments_bills, top_k_rag_bill_summaries, bill_summaries_rag_index, bills_page_size

# Pinecone client
pc = Pinecone()
index = pc.Index(bill_summaries_rag_index)

def get_bill_cards(df):
    bill_cards = []
    for ind, row in df.iterrows():
        # Unique identifiers for the buttons and collapse
        read_more_id = {'type': 'read-more-button', 'index': ind}
        read_less_id = {'type': 'read-less-button', 'index': ind}
        collapse_id = {'type': 'collapse-content', 'index': ind}

        # get date passed
        
        if pd.isna(row.date_passed):
            if row.bill_number in ["16/2020", "25/2012"]:
                date_passed = "Date not avail"
            else:
                date_passed = "Not yet passed"
        else:
            date_passed = row.date_passed.strftime('%Y-%m-%d')
        
        card = dbc.Card(
            dbc.CardBody(
                html.Div([
                    # Top Section: Introduction and Dates
                    dbc.Row([
                        # Introduction Paragraph and Title
                        dbc.Col([
                            html.H4(row.title, className="card-title"),
                            html.P(row.bill_introduction, className="card-text"),
                        ],
                            md=9,  # 9 out of 12 columns on medium to large screens
                            xs=12  # Full width on extra small screens
                        ),
                        # Dates Section
                        dbc.Col(
                            html.Div([
                                html.H5(f"Nr: {row.bill_number}"),
                                html.H6("Date Introduced:", className="card-subtitle"),
                                html.P(row.date_introduced.strftime('%Y-%m-%d') if pd.notna(row.date_introduced) else "N/A"),
                                html.H6("Date Passed:", className="card-subtitle"),
                                html.P(date_passed)
                            ]),
                            md=3,  # 3 out of 12 columns on medium to large screens
                            xs=12  # Full width on extra small screens
                        )
                    ], className="align-items-top"),
                    
                    html.Br(),
                    
                    # Read More Button (Visible only when collapsed)
                    dbc.Row(
                        dbc.Col(
                            dbc.Button(
                                "Read More",
                                id=read_more_id,
                                color="link",
                                className="p-2 w-100",  # Full width with padding
                                n_clicks=0,
                                style={
                                    'textAlign': 'center',
                                    'cursor': 'pointer',
                                    'marginTop': '10px'
                                }
                            ),
                            width=12
                        ),
                        style={
                            'backgroundColor': '#ebedf0',
                            'borderTop': '1px solid #dee2e6'  # Optional: add a top border for separation
                        }
                    ),
                    
                    # Collapsible Content
                    dbc.Collapse(
                        html.Div([
                            dbc.Row([
                                dbc.Col(
                                    [
                                        # Key Points
                                        html.H6("Key Points", className="card-subtitle"),
                                        html.Ul(
                                            [html.Li(i.strip()) for i in row.bill_key_points.split("- ") if len(i) != 0],
                                            className="card-text"
                                        ),
                                        
                                        # Impact
                                        html.H6("Impact", className="card-subtitle"),
                                        html.P(row.bill_impact, className="card-text"),
                                    ],
                                    md=8  # 8 out of 12 columns
                                ),
                                dbc.Col(
                                    [
                                        # Placeholder for alignment or additional content
                                    ],
                                    md=4  # 4 out of 12 columns
                                )
                            ]),
                            
                            html.Br(),
                            
                            # Read Less Button (Visible only when expanded)
                            dbc.Row(
                                dbc.Col(
                                    dbc.Button(
                                        "Read Less",
                                        id=read_less_id,
                                        color="link",
                                        className="p-2 w-100",  # Full width with padding
                                        n_clicks=0,
                                        style={
                                            'textAlign': 'center',
                                            'cursor': 'pointer',
                                            'marginTop': '10px'
                                        }
                                    ),
                                    width=12
                                ),
                                style={
                                    'backgroundColor': '#ebedf0',
                                    'borderTop': '1px solid #dee2e6'  # Optional: add a top border for separation
                                }
                            )
                        ]),
                        id=collapse_id,
                        is_open=False
                    )
                ])
            ),
            className="mb-4"
        )
        # Wrap the card in a div with a unique id
        wrapped_card = html.Div(card, id=f"bill-card-{ind}")
        bill_cards.append(wrapped_card)
    
    return bill_cards


# Function to generate pagination controls with dynamic window
def generate_pagination(total_pages, current_page):
    pagination_items = []

    # Previous Button
    if current_page > 1:
        pagination_items.append(
            dbc.Button(
                "Previous",
                id={'type': 'pagination-button', 'index': 'prev'},
                color="secondary",
                className="me-2",
                n_clicks=0
            )
        )
    else:
        pagination_items.append(
            dbc.Button(
                "Previous",
                id={'type': 'pagination-button', 'index': 'prev'},
                color="secondary",
                className="me-2",
                n_clicks=0,
                disabled=True
            )
        )

    # Define window parameters
    visible_before = 5  # Number of pages before the current page
    visible_after = 4   # Number of pages after the current page

    # Calculate window start and end
    window_start = current_page - visible_before
    window_end = current_page + visible_after

    # Adjust if window_start is less than 1
    if window_start < 1:
        window_end += 1 - window_start
        window_start = 1

    # Adjust if window_end exceeds total_pages
    if window_end > total_pages:
        window_start -= window_end - total_pages
        window_end = total_pages
        if window_start < 1:
            window_start = 1

    # Append page buttons within the window
    for page in range(window_start, window_end + 1):
        pagination_items.append(
            dbc.Button(
                str(page),
                id={'type': 'pagination-button', 'index': page},
                color="primary" if page == current_page else "light",
                className="me-1",
                n_clicks=0
            )
        )

    # Add ellipsis if there are more pages after the window
    if window_end < total_pages:
        pagination_items.append(
            dbc.Button(
                "...",
                disabled=True,
                color="light",
                className="me-1",
                style={"cursor": "default"}
            )
        )

    # Next Button
    if current_page < total_pages:
        pagination_items.append(
            dbc.Button(
                "Next",
                id={'type': 'pagination-button', 'index': 'next'},
                color="secondary",
                className="ms-2",
                n_clicks=0
            )
        )
    else:
        pagination_items.append(
            dbc.Button(
                "Next",
                id={'type': 'pagination-button', 'index': 'next'},
                color="secondary",
                className="ms-2",
                n_clicks=0,
                disabled=True
            )
        )

    return dbc.Nav(pagination_items, className="justify-content-center")

# Layout for the Bill Summaries Page with Pagination
def bill_summaries_layout():
    return html.Div(
        [
            html.H1("Bill Summaries"),
            html.P("Summaries of legislation introduced or passed in parliament."),
            
            # Dropdowns Section
            dbc.Row([
                # Parliament Session Dropdown
                dbc.Col([
                    html.Label("Select a Parliament Session:"),
                    dcc.Dropdown(
                        id='parliament-dropdown-bills',
                        options=[{'label': session, 'value': session} for session in reversed(parliaments_bills.keys())],
                        value='All',  # Set default to 'All'
                        placeholder='Select a parliament session',
                        searchable=False,
                        clearable=False
                    ),
                ], md=4),
                # Search Input and Button
                dbc.Col([
                    dbc.InputGroup([
                        dbc.Input(
                            id='text-input-bills',
                            type='text',
                            placeholder='Enter query here e.g. "climate change"',
                        ),
                        dbc.Button(
                            "Search",
                            id='search-button-bills',
                            color='primary',
                            className='ms-2'
                        )
                    ]),
                ], md=7),
                # Info Icon and Tooltip
                dbc.Col([
                    html.Span(
                        # Info Icon (Bootstrap Icons)
                        html.I(
                            className="bi bi-info-circle",  # Bootstrap Icon classes
                            id="bills-search-info-icon",  # Unique ID for the tooltip
                            style={
                                "margin-left": "5px",          # Space between label and icon
                                "cursor": "pointer",           # Pointer cursor on hover
                                "color": "#17a2b8",            # Bootstrap's info color
                                "fontSize": "2rem"             # Icon size
                            }
                        )
                    ),
                    dbc.Tooltip(
                        "Leaving the search bar empty retrieves all bills (in the database) for the given parliament. Entering a search query returns the top 50 most relevant bills to the query, ordered from most to least relevant.",
                        target="bills-search-info-icon",  # Link tooltip to the icon's ID
                        placement="right",                # Position the tooltip to the right of the icon
                        style={
                            "maxWidth": "300px",
                            "textAlign": "left"  # Ensure text is left-aligned within the tooltip
                        }
                    )
                ], md=1)
            ], className="mb-4 align-items-end"),
            # Accordion Section
            dbc.Accordion(
                [
                    dbc.AccordionItem(
                        [
                            html.P(f"""
                                   Bill summaries are generated using GPT and retrieved using vector embeddings. We cap maximum retrievals at {top_k_rag_bill_summaries} to increase speed and reduce cost. Please refer to the methodology section for more info.""")
                        ],
                        title=html.Span(
                            "How are bill summaries generated and retrieved?",
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
            # Output Sections
            dbc.Row([
                dbc.Col([
                    # Container for bill cards
                    html.Div(id="bills-container")
                ], width=12)
            ]),
            dbc.Row([
                dbc.Col([
                    # Pagination controls
                    html.Div(id="pagination-controls", className="mt-4")
                ], width=12, className="d-flex justify-content-center")
            ]),
            # Hidden Store to hold filtered data
            dcc.Store(id='filtered-data-store'),
            # Hidden Store to keep track of the current page
            dcc.Store(id='current-page-store', data=1),
            # Hidden Div to trigger scroll to top (for pagination)
            html.Div(id='scroll-trigger', style={'display': 'none'}),            
            # Hidden Div to handle scroll action after pagination
            html.Div(id='scroll-action', style={'display': 'none'}),
            # Removed 'scroll-store-collapse' and related Div
        ],
        className='content'
    )

def bill_summaries_callbacks(app, data):
    # Callback to toggle the collapse for "Read More" and "Read Less" buttons
    @app.callback(
        Output({'type': 'collapse-content', 'index': MATCH}, 'is_open'),
        [
            Input({'type': 'read-more-button', 'index': MATCH}, 'n_clicks'),
            Input({'type': 'read-less-button', 'index': MATCH}, 'n_clicks'),
        ],
        State({'type': 'collapse-content', 'index': MATCH}, 'is_open'),
    )
    def toggle_collapse(n_clicks_more, n_clicks_less, is_open):
        if n_clicks_more or n_clicks_less:
            return not is_open
        return is_open

    # Callback to toggle "Read More" button visibility based on 'is_open' state
    @app.callback(
        Output({'type': 'read-more-button', 'index': MATCH}, 'style'),
        Input({'type': 'collapse-content', 'index': MATCH}, 'is_open')
    )
    def toggle_read_more_button(is_open):
        if is_open:
            return {'display': 'none'}
        else:
            return {'display': 'block'}

    # Removed the problematic callback that outputs to 'scroll-store-collapse.data'

    # Callback to filter data based on search button click
    @app.callback(
        Output('filtered-data-store', 'data'),
        Input('search-button-bills', 'n_clicks'),
        State('parliament-dropdown-bills', 'value'),
        State('text-input-bills', 'value')
    )
    def filter_bills(n_clicks, selected_parliament, search_query):
        bills_df = data['bill_summaries']
        bills_df[['number', 'year']] = bills_df['bill_number'].str.split(r'/', expand=True).astype(int)
        bills_df = bills_df.sort_values(['year', 'number'], ascending = [False, False])        

        if n_clicks is None:
            # Initial load or "All" selected: show all bills
            filtered_df = bills_df.copy()
        else:
            if selected_parliament == "All":
                filtered_df = bills_df.copy()
            else:
                filtered_df = bills_df[bills_df['parliament'] == int(parliaments_bills[selected_parliament])]
        
        # Now filter again if query was made
        if search_query:
            parliament = None if selected_parliament == "All" else int(parliaments_bills[selected_parliament])
            responses = query_vector_embeddings(search_query, top_k_rag_bill_summaries, index, parliament=parliament, include_metadata=False)
            bill_numbers = [i['id'] for i in responses]
            filtered_df = filtered_df[filtered_df.bill_number.isin(bill_numbers)] 

            # Now sort order by relevance
            filtered_df['bill_number'] = pd.Categorical(filtered_df['bill_number'], categories=bill_numbers, ordered=True)
            filtered_df = filtered_df.sort_values('bill_number').reset_index(drop=True)               

        # Convert filtered_df to list of dicts
        return filtered_df.to_dict('records')

    # Callback to handle pagination and trigger scroll to top
    @app.callback(
        [
            Output("bills-container", "children"),
            Output("pagination-controls", "children"),
            Output("scroll-trigger", "children"),
            Output("current-page-store", "data")
        ],
        [
            Input({'type': 'pagination-button', 'index': ALL}, 'n_clicks'),
            Input('filtered-data-store', 'data')
        ],
        [
            State({'type': 'pagination-button', 'index': ALL}, 'id'),
            State('current-page-store', 'data')
        ]
    )
    def update_page(page_n_clicks, filtered_data, ids, current_page):
        ctx = callback_context

        if not ctx.triggered:
            # No trigger yet, display the first page
            current_page = 1
            scroll_trigger = 'scroll'  # Trigger scroll on initial load if desired
        else:
            triggered = ctx.triggered[0]['prop_id'].split('.')[0]
            if triggered == 'filtered-data-store':
                # When filtered data is updated (search performed), reset to page 1
                current_page = 1
                scroll_trigger = None  # Do NOT trigger scroll
            else:
                # Handle pagination button clicks
                # Find which button was clicked
                for n_click, id_dict in zip(page_n_clicks, ids):
                    if n_click and n_click > 0:
                        if id_dict['index'] == 'prev':
                            current_page = max(1, current_page - 1)
                        elif id_dict['index'] == 'next':
                            total_pages = (len(filtered_data) + bills_page_size - 1) // bills_page_size
                            current_page = min(total_pages, current_page + 1)
                        else:
                            # Assume it's a page number
                            current_page = id_dict['index']
                        break
                else:
                    # If no button was clicked, retain current_page
                    pass

                # Trigger scroll to top by setting 'scroll_trigger' to 'scroll'
                scroll_trigger = 'scroll'

        # Convert filtered_data back to DataFrame
        if filtered_data:
            filtered_df = pd.DataFrame(filtered_data)
            # Convert date columns to datetime
            filtered_df['date_passed'] = pd.to_datetime(filtered_df['date_passed'], errors='coerce')
            filtered_df['date_introduced'] = pd.to_datetime(filtered_df['date_introduced'], errors='coerce')
        else:
            # If no data is filtered, return an empty DataFrame
            filtered_df = pd.DataFrame()

        total_pages = (len(filtered_df) + bills_page_size - 1) // bills_page_size
        total_pages = max(1, total_pages)  # Ensure at least one page

        # Ensure current_page is within bounds
        current_page = max(1, min(current_page, total_pages))

        if len(filtered_df) == 0:
            # If no bills found, display a message
            bill_cards = html.P("No bills found matching your criteria.")
            pagination = ""
            scroll_trigger = None  # No need to trigger scroll
        else:
            start = (current_page - 1) * bills_page_size
            end = start + bills_page_size
            current_bills = filtered_df.iloc[start:end]

            # Generate bill cards
            bill_cards = get_bill_cards(current_bills)

            # Generate pagination controls with dynamic window
            pagination = generate_pagination(total_pages, current_page)

            # Only set scroll_trigger if triggered by pagination
            if triggered != 'filtered-data-store':
                scroll_trigger = 'scroll'
            else:
                scroll_trigger = None

        # Update the current page store
        updated_current_page = current_page

        return bill_cards, pagination, scroll_trigger, updated_current_page

    # Clientsided callback to scroll to top after pagination
    app.clientside_callback(
        """
        function(scroll_value) {
            if(scroll_value === 'scroll') {
                window.scrollTo({ top: 0, behavior: 'smooth' });
            }
            return '';
        }
        """,
        Output('scroll-action', 'children'),
        Input('scroll-trigger', 'children'),
        prevent_initial_call=True
    )

    # Clientsided callback to scroll to the specific card after collapsing
    app.clientside_callback(
        """
        function(card_id) {
            if(card_id) {
                var element = document.getElementById(card_id);
                if(element) {
                    element.scrollIntoView({ behavior: 'smooth', block: 'start' });
                }
            }
            return '';
        }
        """,
        Output('scroll-action-collapse', 'children'),
        Input('scroll-store-collapse', 'data'),
        prevent_initial_call=True
    )
