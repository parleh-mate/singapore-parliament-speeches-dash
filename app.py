# app.py
from dash import html, dcc, Input, Output, State, callback_context
import dash_bootstrap_components as dbc

from load_data import app
from pages.home import home_page, navbar, sidebar_content, sidebar
from pages.speeches import speeches_callbacks, speeches_layout
from pages.participation import participation_callbacks, participation_layout
from pages.demographics import demographics_callbacks, demographics_layout

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

participation_callbacks(app)
speeches_callbacks(app)
demographics_callbacks(app)

# Run the app
if __name__ == "__main__":
    app.run_server(debug=True)
