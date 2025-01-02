from dash import html, dcc, Input, Output, State, callback_context, ALL
import dash_bootstrap_components as dbc
import pandas as pd
from pinecone import Pinecone
import json

from query_vectors import query_vector_embeddings
from utils import parliaments_bills, top_k_rag_bill_summaries, bill_summaries_rag_index

# pinecone client
pc = Pinecone()
index = pc.Index(bill_summaries_rag_index)


# Constants for pagination
PAGE_SIZE = 5

def get_bill_cards(df):
    bill_cards = []
    for ind, row in df.iterrows():
        card = dbc.Card(
            dbc.CardBody(
                dbc.Row([
                    dbc.Col(
                        [
                            html.H4(row.title, className="card-title"),
                            html.Br(),
                            html.H6("Introduction", className="card-subtitle"),
                            html.P(row.bill_introduction, className="card-text"),
                            html.H6("Key Points", className="card-subtitle"),
                            html.Ul([html.Li(i.strip()) for i in row.bill_key_points.split("-") if len(i)!=0], className="card-text"),
                            html.H6("Impact", className="card-subtitle"),
                            html.P(row.bill_impact, className="card-text"),
                        ],
                        md=8  # 8 out of 12 columns
                    ),
                    dbc.Col(
                        [
                            html.H6("Date Introduced"),
                            html.P(row.date_introduced),
                            html.H6("Date Passed"),
                            html.P("Not yet passed" if pd.isna(row.date_passed) else row.date_passed),
                        ],
                        md=4,  # 4 out of 12 columns
                        style={"borderLeft": "1px solid #ddd", "paddingLeft": "20px"}
                    )
                ])
            ),
            className="mb-4"
        )
        bill_cards.append(card)
    
    return bill_cards

# Updated Function to generate pagination controls with dynamic window
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

# Layout for the Topic Summaries Page with Pagination
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
                ], md=3),
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
                ], md=8),
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
                        placement="right",                      # Position the tooltip to the right of the icon
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
                                   Summaries are generated by querying the {top_k_rag_bill_summaries} most relevant pre-summarized speeches to the user's query and summarizing again using GPT. Please refer to the methodology section for more info.""")
                        ],
                        title=html.Span(
                            "How are summaries generated?",
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
            # Hidden Div to trigger scroll to top
            html.Div(id='scroll-trigger', style={'display': 'none'}),            
            # Hidden Div to handle scroll action
            html.Div(id='scroll-action', style={'display': 'none'})
        ],
        className='content'
    )

def bill_summaries_callbacks(app, data):   

    # Callback to filter data based on search button click
    @app.callback(
        Output('filtered-data-store', 'data'),
        Input('search-button-bills', 'n_clicks'),
        State('parliament-dropdown-bills', 'value'),
        State('text-input-bills', 'value')
    )
    def filter_bills(n_clicks, selected_parliament, search_query):

        bills_df = data['bill_summaries'].sort_values("date_introduced", ascending = False)

        if n_clicks is None:
            # Initial load or "All" selected: show all bills
            filtered_df = bills_df.copy()
        else:
            if selected_parliament=='All':
                filtered_df = bills_df.copy()
            else:
                filtered_df = bills_df[bills_df['parliament'] == int(parliaments_bills[selected_parliament])]
        # now filter again if query was made
        if search_query:
            parliament = None if selected_parliament=="All" else int(parliaments_bills[selected_parliament])
            responses = query_vector_embeddings(search_query, top_k_rag_bill_summaries, index, parliament=parliament, include_metadata=False)
            bill_numbers = [i['id'] for i in responses]
            filtered_df = filtered_df[filtered_df.bill_number.isin(bill_numbers)] 

            # now sort order by relevance
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
        else:
            triggered = ctx.triggered[0]['prop_id'].split('.')[0]
            if triggered == 'filtered-data-store':
                # When filtered data is updated, reset to page 1
                current_page = 1
            else:
                # Handle pagination button clicks
                # Find which button was clicked
                for n_click, id_dict in zip(page_n_clicks, ids):
                    if n_click and n_click > 0:
                        if id_dict['index'] == 'prev':
                            current_page = max(1, current_page - 1)
                        elif id_dict['index'] == 'next':
                            total_pages = (len(filtered_data) + PAGE_SIZE - 1) // PAGE_SIZE
                            current_page = min(total_pages, current_page + 1)
                        else:
                            # Assume it's a page number
                            current_page = id_dict['index']
                        break
                else:
                    # If no button was clicked, retain current_page
                    pass

        # Convert filtered_data back to DataFrame
        if filtered_data:
            filtered_df = pd.DataFrame(filtered_data)
            # Convert date columns to datetime
            filtered_df['date_passed'] = pd.to_datetime(filtered_df['date_passed'], errors='coerce')
            filtered_df['date_introduced'] = pd.to_datetime(filtered_df['date_introduced'], errors='coerce')
        else:
            # If no data is filtered, return an empty DataFrame
            filtered_df = pd.DataFrame()

        total_pages = (len(filtered_df) + PAGE_SIZE - 1) // PAGE_SIZE
        total_pages = max(1, total_pages)  # Ensure at least one page

        # Ensure current_page is within bounds
        current_page = max(1, min(current_page, total_pages))

        if len(filtered_df) == 0:
            # If no bills found, display a message
            bill_cards = html.P("No bills found matching your criteria.")
            pagination = ""
            scroll_trigger = None  # No need to trigger scroll
        else:
            start = (current_page - 1) * PAGE_SIZE
            end = start + PAGE_SIZE
            current_bills = filtered_df.iloc[start:end]

            # Generate bill cards
            bill_cards = get_bill_cards(current_bills)

            # Generate pagination controls with dynamic window
            pagination = generate_pagination(total_pages, current_page)

            # Trigger scroll to top by updating 'scroll-trigger.children'
            scroll_trigger = current_page

        # Update the current page store
        updated_current_page = current_page

        return bill_cards, pagination, scroll_trigger, updated_current_page


    # Clientside callback to scroll to top
    app.clientside_callback(
        """
        function(scroll_value) {
            if(scroll_value) {
                window.scrollTo(0, 0);
            }
            return '';
        }
        """,
        Output('scroll-action', 'children'),
        Input('scroll-trigger', 'children'),
        prevent_initial_call=True
    )
