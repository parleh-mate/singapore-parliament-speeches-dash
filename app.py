from dash import html, dcc, Input, Output, State, callback_context
import dash_bootstrap_components as dbc
import dash
from flask_caching import Cache
import logging
import pytz
from datetime import datetime, timedelta

from pages.home import home_page, navbar, sidebar_content, sidebar
from pages.speeches import speeches_callbacks, speeches_layout
from pages.summaries import summaries_callbacks, summaries_layout
from pages.policy_positions import policy_positions_callbacks, policy_positions_layout
from pages.topics import topics_callbacks, topics_layout
from pages.participation import participation_callbacks, participation_layout
from pages.questions import questions_callbacks, questions_layout
from pages.demographics import demographics_callbacks, demographics_layout
from pages.methodology import methodology_layout
from pages.about import about_layout

from load_data import load_participation, load_speech_agg, load_speech_summary, load_demographics, load_questions, load_topics

# Initialize the app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.LUX,
                                                "https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.5/font/bootstrap-icons.css"
], suppress_callback_exceptions=True)
server = app.server  # Expose the Flask app as a variable

# Initialize logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# set time
gmt_plus_8 = pytz.timezone('Asia/Singapore')

cache = Cache(server, config={
    'CACHE_TYPE': 'filesystem',
    'CACHE_DIR': '/tmp/cache-directory'
})

# Data fetching function
def get_data():
    data = cache.get('all_data')

    if data is not None:
        logger.debug(f"{datetime.now()} - Data fetched from cache")
        return data
    else:
        logger.debug(f"{datetime.now()} - Data fetched from BigQuery")
        data = {
            'participation': load_participation(),
            'speech_agg': load_speech_agg(),
            'topics': load_topics(),
            'speech_summaries': load_speech_summary(),
            'demographics': load_demographics(),
            'questions': load_questions()
        }

        current_time = datetime.now(gmt_plus_8)
        # Create a datetime object for next 1:00 AM
        today_1am = current_time.replace(hour=1, minute=0, second=0, microsecond=0)
        if current_time < today_1am and current_time >= (today_1am - timedelta(hours=1)):
            next_1am = today_1am
        else:
            next_1am = today_1am + timedelta(days=1)

        # set cached data to expire at next 1am
        cache.set('all_data', data, timeout = (next_1am - current_time).seconds)
        cache.set('time_loaded', datetime.now(gmt_plus_8))
        return data

data = get_data()

# Offcanvas for mobile
offcanvas = dbc.Offcanvas(
    sidebar_content, 
    id="offcanvas", 
    is_open=False, 
    title="Menu", 
    placement="start"
)

# App layout
app.layout = html.Div([
    dcc.Location(id='url'),  # Tracks the URL
    navbar,                   # Navbar component
    offcanvas,                # Offcanvas component for mobile
    dbc.Container([
        dbc.Row([
            dbc.Col(sidebar, xs=12, md=2, className="d-none d-md-block"),  # Sidebar column
            dbc.Col([
                html.Div(id='home-page', children=home_page, style={'display': 'block'}),
                
                html.Div(id='speeches-page', children=speeches_layout(), style={'display': 'none'}),

                html.Div(id='summaries-page', children=summaries_layout(), style={'display': 'none'}),

                html.Div(id='policy-positions-page', children=policy_positions_layout(), style={'display': 'none'}),

                html.Div(id='topics-page', children=topics_layout(), style={'display': 'none'}),
                
                html.Div(id='participation-page', children=participation_layout(), style={'display': 'none'}),

                html.Div(id='questions-page', children=questions_layout(), style={'display': 'none'}),

                html.Div(id='demographics-page', children=demographics_layout(), style={'display': 'none'}),

                html.Div(id='methodology-page', children=methodology_layout(), style={'display': 'none'}),

                html.Div(id='about-page', children=about_layout(), style={'display': 'none'}),

                # 404 Page Div
                html.Div(
                    id='404-page',
                    children=html.Div([
                        html.H1("404: Not Found", className="text-danger"),
                        html.Hr(),
                        html.P("The page you are looking for does not exist."),
                    ], className='content'),
                    style={'display': 'none'}
                ),
            ], xs=12, md=10),
        ], className="gx-0"),
    ], fluid=True),
])

# generate page outputs, make it easier to toggle display later on
page_outputs = {"home": Output('home-page', 'style'),
                "participation": Output('participation-page', 'style'),
                "speeches": Output('speeches-page', 'style'),
                "summaries": Output('summaries-page', 'style'),
                "policy_positions": Output('policy-positions-page', 'style'),
                "topics": Output('topics-page', 'style'),
                "questions": Output('questions-page', 'style'),
                "demographics": Output('demographics-page', 'style'),
                "methodology": Output('methodology-page', 'style'),
                "about": Output('about-page', 'style'),
                "404": Output('404-page', 'style')}

# Callback to control page visibility
@app.callback(
    [i for i in page_outputs.values()], 
    [Input('url', 'pathname')]
)
def display_page(pathname):
    if pathname=="/":
        page = "home"
    else: 
        page = pathname.removeprefix('/')
    if page not in page_outputs.keys():
        page = "404"
    return tuple(({'display': 'block'} if i==page else {'display': 'none'} for i in page_outputs.keys()))

# Callback to toggle the offcanvas sidebar
@app.callback(
    Output("offcanvas", "is_open"),
    [Input("sidebar-toggle", "n_clicks"), Input("url", "pathname")],
    State("offcanvas", "is_open"),
)
def toggle_offcanvas(n_clicks, pathname, is_open):
    ctx = callback_context
    if not ctx.triggered:
        return is_open
    else:
        trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
        if trigger_id == 'sidebar-toggle':
            return not is_open
        elif trigger_id == 'url' and is_open:
            return False
    return is_open

# Register callbacks; must be in correct order!

participation_callbacks(app, data)
speeches_callbacks(app, data)
summaries_callbacks(app, data)
policy_positions_callbacks(app, data)
topics_callbacks(app, data)
questions_callbacks(app, data)
demographics_callbacks(app, data)

# Run the app
if __name__ == "__main__":
    app.run_server(debug=True)
