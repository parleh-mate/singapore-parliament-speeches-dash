from dash import html, dcc, Input, Output, State, callback_context
import dash_bootstrap_components as dbc
import dash
from flask_caching import Cache
import logging
import pytz
from datetime import datetime, timedelta

from pages.home import home_page, navbar, sidebar_content, sidebar
from pages.speeches import speeches_callbacks, speeches_layout
from pages.participation import participation_callbacks, participation_layout
from pages.demographics import demographics_callbacks, demographics_layout

from load_data import load_participation, load_speech_agg, load_speech_summary, load_demographics

# Initialize the app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.LUX], suppress_callback_exceptions=True)
server = app.server  # Expose the Flask app as a variable

# Initialize logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# set time
gmt_plus_8 = pytz.timezone('Asia/Singapore')

# Set up cache
cache = Cache(server, config={
    'CACHE_TYPE': 'filesystem',
    'CACHE_DIR': '/tmp/cache-directory',  # Ensure this directory exists and is writable
    'CACHE_TIME': datetime.now(gmt_plus_8) # Cache today's datetime
})

# Data fetching function
def get_data():
    data = cache.get('all_data')
    time_loaded = cache.get('time_loaded')

    current_time = datetime.now(gmt_plus_8)
    # Create a datetime object for 1:00 AM today
    today_1am = current_time.replace(hour=1, minute=0, second=0, microsecond=0)
    # If current time is before 1:00 AM, go to the previous day's 1:00 AM
    if current_time < today_1am:
        previous_1am = today_1am - timedelta(days=1)
    else:
        previous_1am = today_1am   

    if data is not None and time_loaded>previous_1am:
        logger.debug(f"{datetime.now()} - Data fetched from cache")
        return data
    else:
        logger.debug(f"{datetime.now()} - Data fetched from BigQuery")
        data = {
            'participation': load_participation(),
            'speech_agg': load_speech_agg(),
            'speech_summaries': load_speech_summary(),
            'demographics': load_demographics()
        }
        cache.set('all_data', data)
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
                # Home Page Div
                html.Div(id='home', children=home_page, style={'display': 'block'}),
                
                # Speeches Page Div
                html.Div(id='speeches', children=speeches_layout(), style={'display': 'none'}),
                
                # Participation Page Div
                html.Div(id='participation', children=participation_layout(), style={'display': 'none'}),

                html.Div(id='demographics', children=demographics_layout(), style={'display': 'none'}),

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
page_outputs = {"home": Output('home', 'style'),
                "participation": Output('participation', 'style'),
                "speeches": Output('speeches', 'style'),
                "demographics": Output('demographics', 'style'),
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
demographics_callbacks(app, data)

# Run the app
if __name__ == "__main__":
    app.run_server(debug=True)
