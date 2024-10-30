from dash import html, dcc, Input, Output
import dash_bootstrap_components as dbc
import plotly.graph_objects as go

from utils import PARTY_COLOURS, parliaments, parliament_sessions

# participation layout with dropdowns, graph
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
                        "'All' takes the average across all parliamentary sittings from the 12th parliament to current",  # Tooltip text
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
                                "Attendance is measured by the number of sessions the member attended (or was present in) out of the total number of sessions which occurred while they were sitting as a member. For example, WP's Lee Li Lian won the Punggol East SMC by-election in January 2013 as the 12th parliament was underway. Her attendance is calculated as the proportion of the remaining 80 sittings she was qualified to attend instead of the total 89.",
                                html.Br(),
                                html.Br(),
                                "Participation is measured by the number of sessions in which the member spoke at least once as a proportion of the number of sessions the member attended. For example, in the 13th parliament Walter Theseira (NMP) had a participation rate of 94.2%, , meaning that he spoke in 94.2% of the of 98.1% of sessions he attended. Please refer to the methodology for more info."
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

    # Callback to update the participation graph
    @app.callback(
        Output('participation-graph', 'figure'),
        [Input('parliament-dropdown-participation', 'value'),
        Input('constituency-dropdown-participation', 'value'),
        Input('member-dropdown-participation', 'value')]
    )
    def update_graph(selected_parliament, selected_constituency, selected_member):
        participation_df = data['participation']

        # Filter by parliament
        participation_df_highlighted = participation_df[participation_df['parliament'] == parliaments[selected_parliament]]
        full_df = participation_df_highlighted.copy()
        
        # Further filter based on selected_constituency
        if selected_constituency != 'All' and selected_constituency:
            participation_df_highlighted = participation_df_highlighted[participation_df_highlighted['member_constituency'] == selected_constituency]
        
        # Further filter based on selected_member
        if selected_member != 'All' and selected_member:
            participation_df_highlighted = participation_df_highlighted[participation_df_highlighted['member_name'] == selected_member]

        participation_df_non_highlighted = full_df.drop(participation_df_highlighted.index)      

        # Create the scatter plot
        fig = go.Figure()

        for party in participation_df_highlighted.member_party.unique():

            plot_df = participation_df_highlighted.query(f"member_party=='{party}'")
            fig.add_trace(go.Scatter(
                x=plot_df['attendance'],
                y=plot_df['participation'],
                mode='markers',
                marker=dict(
                    color=plot_df['member_party'].map(PARTY_COLOURS)
                ),
                hovertext="Member: " + plot_df['member_name'] + "<br>" +
                            "Party: " + plot_df['member_party'] + "<br>" +
                            "Attendance: " + plot_df['attendance'].astype(str) + "<br>" +
                            "Participation: " + plot_df['participation'].astype(str),
                hoverinfo='text',
                name=party,
                showlegend=True  # Only the highlighted trace shows in legend
            ))

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
        
        return fig