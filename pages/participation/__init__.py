import plotly.express as px
from dash import html, dcc, Input, Output, dash_table
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go

from utils import PARTY_COLOURS, parliaments, parliament_sessions

# participation layout with dropdowns, graph, and table
def participation_layout():
    return html.Div(
        [
            html.H1("Parliamentary Participation Analysis"),
            
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
                                    id="participation_parliament-session-info-icon",  # Unique ID for the tooltip
                                    style={
                                        "margin-left": "5px",          # Space between label and icon
                                        "cursor": "pointer",           # Pointer cursor on hover
                                        "color": "#17a2b8",            # Bootstrap's info color
                                        "fontSize": "1rem"             # Icon size
                                    }
                                )
                            )
                        ],
                        style={"display": "flex", "alignItems": "center"}  # Align label and icon vertically
                    ),
                    
                    # Dropdown Component
                    dcc.Dropdown(
                        id='parliament-dropdown-participation',
                        options=[{'label': session, 'value': session} for session in parliament_sessions],
                        value='All',  # Set default to 'All'
                        placeholder='Select a parliament session',
                        searchable=False,
                        clearable=False
                    ),
                    
                    # Tooltip Component
                    dbc.Tooltip(
                        "'All' takes the average across all parliamentary sessions",  # Tooltip text
                        target="participation_parliament-session-info-icon",  # Link tooltip to the icon's ID
                        placement="right",                      # Position the tooltip to the right of the icon
                        style={
                            "maxWidth": "300px",
                            "textAlign": "left" 
                        }
                    )
                ], md=4),
                
                # Second Dropdown Column
                dbc.Col([
                    html.Label("Select a Constituency:"),
                    dcc.Dropdown(
                        id='constituency-dropdown-participation',
                        options=[],  # Will be populated via callback
                        value='All',
                        placeholder='Select a constituency',
                        searchable=False,
                        clearable=False
                    )
                ], md=4, id='constituency-dropdown-container-participation', style={'display': 'none'}),
                
                # Third Dropdown Column
                dbc.Col([
                    html.Label("Select a Member Name:"),
                    dcc.Dropdown(
                        id='member-dropdown-participation',
                        options=[],  # Will be populated via callback
                        value='All',
                        placeholder='Select a member name',
                        searchable=False,
                        clearable=False
                    )
                ], md=4),
            ], className="mb-4"),
            
            # Accordion Section
            dbc.Accordion(
                [
                    dbc.AccordionItem(
                        [
                            html.P([
                                "Attendance is measured by the number of sessions the member attended (or was present in) out of the total number of sessions which occurred while they were sitting as a member.",
                                html.Br(),
                                html.Br(),
                                "Participation is measured by the number of sessions the member spoke in as a proportion of the number of sessions the member attended. Please refer to the methodology for more info."
                            ])
                        ],
                        title=html.Span(
                            "How is participation or attendance defined?",
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
                        id='participation-graph',
                        config={"responsive": True},
                        style={'minHeight': '500px'}
                    )
                ], width=12)
            ]),
            
            # Table Section with Scroll
            dbc.Row([
                dbc.Col([
                    html.H2("Participation and Attendance"),
                    dash_table.DataTable(
                        id='participation-summary-table',
                        columns=[
                            {"name": "Parl.no", "id": "parliament"},
                            {"name": "Party", "id": "member_party"},
                            {"name": "Constituency", "id": "member_constituency"},
                            {"name": "Member Name", "id": "member_name"},
                            {"name": "Attendance", "id": "attendance"},
                            {"name": "Participation", "id": "participation"},
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
                                'if': {'column_id': 'parliament'},
                                'width': '16%',
                                'minWidth': '100px',
                                'maxWidth': '150px',
                            },
                            {
                                'if': {'column_id': 'member_party'},
                                'width': '16%',
                                'minWidth': '100px',
                                'maxWidth': '150px',
                            },
                            {
                                'if': {'column_id': 'member_constituency'},
                                'width': '16%',
                                'minWidth': '100px',
                                'maxWidth': '150px',
                            },
                            {
                                'if': {'column_id': 'member_name'},
                                'width': '16%',
                                'minWidth': '100px',
                                'maxWidth': '150px',
                            },
                            {
                                'if': {'column_id': 'attendance'},
                                'width': '16%',
                                'minWidth': '100px',
                                'maxWidth': '150px',
                            },
                            {
                                'if': {'column_id': 'participation'},
                                'width': '16%',
                                'minWidth': '100px',
                                'maxWidth': '150px',
                            },
                        ],
                        style_data={'height': 'auto'},
                    )
                ], width=12)
            ], className="mt-4"),
        ],
        className='content'
    )

def participation_callbacks(app, data):
    # Callback to control visibility of the Constituency dropdown
    @app.callback(
        Output('constituency-dropdown-container-participation', 'style'),
        Input('parliament-dropdown-participation', 'value')
    )
    def toggle_constituency_dropdown(selected_parliament):
        if selected_parliament != 'All':
            return {'display': 'block'}
        else:
            return {'display': 'none'}

    # Callback to update Constituency options based on selected session
    @app.callback(
        [Output('constituency-dropdown-participation', 'options'),
        Output('constituency-dropdown-participation', 'value')],
        Input('parliament-dropdown-participation', 'value')
    )
    def update_constituency_options(selected_parliament):
        if selected_parliament == 'All':
            # If 'All' is selected, reset options to include only 'All'
            return [{'label': 'All', 'value': 'All'}], 'All'
        participation_df = data['participation']
        
        # Filter the dataframe based on the selected parliament session
        participation_df = participation_df[participation_df['parliament'] == parliaments[selected_parliament]]
        # Get unique constituencies
        constituencies = sorted(participation_df['member_constituency'].unique())
        # Add 'All' option
        options = [{'label': 'All', 'value': 'All'}] + [{'label': const, 'value': const} for const in constituencies]
        return options, 'All'

    # Callback to update Member Name options based on selected session and constituency
    @app.callback(
        [Output('member-dropdown-participation', 'options'),
        Output('member-dropdown-participation', 'value')],
        [Input('parliament-dropdown-participation', 'value'),
        Input('constituency-dropdown-participation', 'value')]
    )
    def update_member_options(selected_parliament, selected_constituency):
        participation_df = data['participation']
        # Start with filtering by parliament session
        participation_df = participation_df[participation_df['parliament'] == parliaments[selected_parliament]]

        # Further filter by constituency if not 'All'
        if selected_constituency and selected_constituency != 'All':
            participation_df = participation_df[participation_df['member_constituency'] == selected_constituency]
        # Get unique member names
        members = sorted(participation_df['member_name'].unique())
        # Add 'All' option
        options = [{'label': 'All', 'value': 'All'}] + [{'label': member, 'value': member} for member in members]
        return options, 'All'

    # Callback to update the participation graph and table on Page 1
    @app.callback(
        [Output('participation-graph', 'figure'),
        Output('participation-summary-table', 'data')],
        [Input('parliament-dropdown-participation', 'value'),
        Input('constituency-dropdown-participation', 'value'),
        Input('member-dropdown-participation', 'value')]
    )
    def update_graph_and_table(selected_parliament, selected_constituency, selected_member):
        participation_df = data['participation']

        # Filter by parliament
        participation_df = participation_df[participation_df['parliament'] == parliaments[selected_parliament]]
        
        # Further filter based on selected_constituency
        if selected_constituency != 'All' and selected_constituency:
            participation_df_highlighted = participation_df[participation_df['member_constituency'] == selected_constituency]
        
        # Further filter based on selected_member
        if selected_member != 'All' and selected_member:
            participation_df_highlighted = participation_df_highlighted[participation_df_highlighted['member_name'] == selected_member]

        if selected_constituency=='All' and selected_member=='All':
            participation_df_highlighted = participation_df

        participation_df_non_highlighted = participation_df.drop(participation_df_highlighted.index)      

        # Create the scatter plot
        fig = px.scatter(
            participation_df_highlighted,
            x='attendance',
            y='participation',
            color='member_party',
            hover_data={
                'member_name': True,
                'member_party': True
            },
            title=f'Participation vs Attendance by member - Parliament {selected_parliament}',
            color_discrete_map=PARTY_COLOURS
        )

        fig.add_trace(go.Scatter(
            x=participation_df_non_highlighted['attendance'],
            y=participation_df_non_highlighted['participation'],
            mode='markers',
            marker=dict(
                color='grey',
                opacity=0.2
            ),
            hoverinfo='skip',  # Disable hover for non-highlighted points
            showlegend=False  # Non-highlighted trace doesn't show in legend
        ))

        fig.update_layout(legend=dict(
                              title=dict(text='Party'),
                              yanchor="top",
                              y=0.99,
                              xanchor="left",
                              x=0.01
                              ),
                              xaxis_title="Attendance (%)",
                              yaxis_title="Participation (%)",
                              template='plotly_white'
        )
                              
        fig.update_traces(hovertemplate='Member: %{customdata[0]}<br>' +
                          'Party: %{customdata[1]}<br>' +
                          'Attendance: %{x}<br>' + 
                          'Participation: %{y}')
        
        # Prepare table data
        table_data = participation_df_highlighted.to_dict('records')
        
        return fig, table_data