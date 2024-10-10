import plotly.express as px
from dash import html, dcc, Input, Output, dash_table
import dash_bootstrap_components as dbc
import plotly.express as px

from utils import PARTY_COLOURS, parliaments, parliament_sessions
from load_data import get_data

# participation layout with dropdowns, graph, and table
def participation_layout():
    return html.Div(
        [
            html.H1("Parliamentary participation Analysis"),
            
            # Dropdowns Section
            dbc.Row([
                dbc.Col([
                    html.Label("Select a Parliament Session:"),
                    dcc.Dropdown(
                        id='parliament-dropdown-participation',
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
                        id='constituency-dropdown-participation',
                        options=[],  # Will be populated via callback
                        value='All',
                        placeholder='Select a constituency',
                        searchable=False,
                        clearable=False
                    )
                ], md=4, id='constituency-dropdown-container-participation', style={'display': 'none'}),
                
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
                    html.H2("Speech Summaries"),
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

def participation_callbacks(app):
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
        participation_df = get_data()['participation']
        
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
        participation_df = get_data()['participation']
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
        participation_df = get_data()['participation']

        # Filter by parliament
        participation_df = participation_df[participation_df['parliament'] == parliaments[selected_parliament]]
        
        # Further filter based on selected_constituency
        if selected_constituency != 'All' and selected_constituency:
            participation_df = participation_df[participation_df['member_constituency'] == selected_constituency]
        
        # Further filter based on selected_member
        if selected_member != 'All' and selected_member:
            participation_df = participation_df[participation_df['member_name'] == selected_member]
        
        # Create the scatter plot
        fig = px.scatter(
            participation_df,
            x='attendance',
            y='participation',
            color='member_party',
            hover_data={
                'member_name': True,
                'member_party': True,
                'attendance': ':.2f',
                'participation': ':.2f'
            },
            title=f'Attendance vs Participation by member - Parliament {selected_parliament}',
            color_discrete_map=PARTY_COLOURS
        )
        fig.update_layout(transition_duration=500)
        
        # Prepare table data
        table_data = participation_df.to_dict('records')
        
        return fig, table_data