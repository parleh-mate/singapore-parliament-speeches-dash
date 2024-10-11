import plotly.express as px
from dash import html, dcc, Input, Output, dash_table
import dash_bootstrap_components as dbc
import plotly.express as px

from utils import PARTY_COLOURS, parliaments, parliament_sessions
from load_data import get_data

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
                    html.H2("Speech Summaries"),
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


def speeches_callbacks(app):
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
        speech_agg_df = get_data()['speech_agg']
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
        speech_agg_df = get_data()['speech_agg']
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
        speech_agg_df = get_data()['speech_agg']
        speech_summary_df = get_data()['speech_summaries']

        # Filter by parliament        
        speech_agg_df = speech_agg_df[speech_agg_df['parliament'] == parliaments[selected_parliament]]

        if selected_parliament != 'All' and selected_parliament:
            speech_summary_df = speech_summary_df[speech_summary_df['parliament'] == int(parliaments[selected_parliament])]
        
        # Further filter based on selected_constituency
        if selected_constituency != 'All' and selected_constituency:
            speech_agg_df = speech_agg_df[speech_agg_df['member_constituency'] == selected_constituency]
            speech_summary_df = speech_summary_df[speech_summary_df['member_constituency'] == selected_constituency]
        
        # Further filter based on selected_member
        if selected_member != 'All' and selected_member:
            speech_agg_df = speech_agg_df[speech_agg_df['member_name'] == selected_member]
            speech_summary_df = speech_summary_df[speech_summary_df['member_name'] == selected_member]
        
        # Create the scatter plot
        fig = px.scatter(
            speech_agg_df,
            x='speeches_per_sitting',
            y='questions_per_sitting',
            color='member_party',
            size='words_per_speech',  # Dynamically size based on words_per_speech
            hover_data={
                'member_name': True,
                'member_party': True,
                'speeches_per_sitting': ':.2f',
                'questions_per_sitting': ':.2f',
                'words_per_speech': True
            },
            title=f'Speeches vs. Questions per Sitting - Parliament {selected_parliament}',
            color_discrete_map=PARTY_COLOURS
        )
        fig.update_layout(transition_duration=500)
        
        # Prepare table data
        table_data = speech_summary_df.to_dict('records')
        
        return fig, table_data