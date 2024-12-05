from dash import html, dcc, Input, Output, State, callback_context
import dash_bootstrap_components as dbc
import dash

from load_data import data
from pages.home import home_page, navbar, sidebar_content, sidebar
from pages.member_metrics import member_metrics_callbacks, member_metrics_layout
from pages.policy_positions import policy_positions_callbacks, policy_positions_layout
from pages.topics import topics_callbacks, topics_layout
from pages.topics_questions import topics_questions_callbacks, topics_questions_layout
from pages.demographics import demographics_callbacks, demographics_layout
from pages.methodology import methodology_layout
from pages.about import about_layout

# Initialize the app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.LUX,
                                                "https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.5/font/bootstrap-icons.css"
], suppress_callback_exceptions=True)

server = app.server  # Expose the Flask app as a variable

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

                html.Div(id='member-metrics-page', children=member_metrics_layout(), style={'display': 'none'}),

                html.Div(id='policy-positions-page', children=policy_positions_layout(), style={'display': 'none'}),

                html.Div(id='topics-page', children=topics_layout(), style={'display': 'none'}),

                html.Div(id='topics-questions-page', children=topics_questions_layout(), style={'display': 'none'}),

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
                "member_metrics": Output('member-metrics-page', 'style'),
                "policy_positions": Output('policy-positions-page', 'style'),
                "topics": Output('topics-page', 'style'),
                "topics_questions": Output('topics-questions-page', 'style'),
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

member_metrics_callbacks(app, data)
policy_positions_callbacks(app, data)
topics_callbacks(app, data)
topics_questions_callbacks(app, data)
demographics_callbacks(app, data)

# Run the app
if __name__ == "__main__":
    app.run_server(debug=True)
