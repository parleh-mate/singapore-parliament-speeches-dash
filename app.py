
from dash import html, dcc, Input, Output, State, callback_context
import dash_bootstrap_components as dbc

from load_data import app
from pages.home import *
from pages.Speeches import speeches_callbacks, speeches_layout

# Offcanvas for mobile
offcanvas = dbc.Offcanvas(sidebar_content, id="offcanvas", is_open=False, title="Menu", placement="start")

# App layout
app.layout = html.Div([
    dcc.Location(id='url'),
    navbar,
    offcanvas,
    dbc.Container([
        dbc.Row([
            dbc.Col(sidebar, xs=12, md=2, className="d-none d-md-block"),
            dbc.Col([
                html.Div(id='page-content'),
                html.Div(id='speeches', children=speeches_layout(), style={'display': 'none'}),
                # Removed Page 2 Div
            ], xs=12, md=10),
        ], className="gx-0"),
    ], fluid=True),
])


# Callback to control page visibility
@app.callback(
    [Output('speeches', 'style'), Output('page-content', 'children')],
    Input('url', 'pathname'),
)
def display_page(pathname):
    if pathname == '/speeches':
        return {'display': 'block'}, ''
    elif pathname == '/':
        return {'display': 'none'}, home_page
    else:
        return {'display': 'none'}, html.Div([
            html.H1("404: Not found", className="text-danger"),
            html.Hr(),
            html.P(f"The pathname {pathname} was not recognized..."),
        ])

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

speeches_callbacks(app)

# Run the app
if __name__ == "__main__":
    app.run_server(debug=True)
