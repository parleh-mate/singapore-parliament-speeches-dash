from dash import html, dcc, Input, Output, State, callback_context
import dash_bootstrap_components as dbc
import dash
import os
from flask import send_from_directory, Response

from load_data import data
from pages.home import home_page, navbar, sidebar_content, sidebar
from pages.member_metrics import member_metrics_callbacks, member_metrics_layout
from pages.policy_positions import policy_positions_callbacks, policy_positions_layout
from pages.bill_summaries import bill_summaries_callbacks, bill_summaries_layout
from pages.topics_questions import topics_questions_callbacks, topics_questions_layout
from pages.demographics import demographics_callbacks, demographics_layout
from pages.methodology import methodology_layout
from pages.about import about_layout
from utils import generate_sitemap

# Initialize the app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.LUX,
                                                "https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.5/font/bootstrap-icons.css"
], suppress_callback_exceptions=True)

app.title = "Parleh-mate!"

server = app.server  # Expose the Flask app as a variable

# Route for robots.txt
@server.route('/robots.txt')
def robots():
    return send_from_directory('', 'robots.txt')

# Offcanvas for mobile
offcanvas = dbc.Offcanvas(
    sidebar_content, 
    id="offcanvas", 
    is_open=False, 
    title="Menu", 
    placement="start"
)

# Define the custom index string with the meta tag

page_description = "Parleh-mate is an independent project that sheds light on goings-on in the Singapore Parliament. Discover policy positions, bill summaries, and more."

app.index_string = f'''
<!DOCTYPE html>
<html>
    <head>
        {{%metas%}}
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">

        <!-- Google Search Console Verification Meta Tag -->
        <meta name="google-site-verification" content="0ofUVUTfiVHRVq_jhAtc74FUXixVJ9h2RVXtxURlXHM" />

        <!-- Standard Meta Description -->
        <meta name="description" content="{page_description}" />

        <!-- Open Graph Meta Tags for Facebook, LinkedIn, etc. -->
        <meta property="og:title" content="{{%title%}}" />
        <meta property="og:description" content="{page_description}" />
        <meta property="og:image" content="https://parlehmate.onrender.com/assets/parlehmate_logo_cropped.jpg" />
        <meta property="og:url" content="https://parlehmate.onrender.com/" />
        <meta property="og:type" content="website" />
        <meta property="og:site_name" content="Parleh-mate!" />

        <!-- Twitter Card Meta Tags -->
        <meta name="twitter:card" content="summary_large_image" />
        <meta name="twitter:title" content="{{%title%}}" />
        <meta name="twitter:description" content="{page_description}" />
        <meta name="twitter:image" content="https://parlehmate.onrender.com/assets/parlehmate_logo_cropped.jpg" />
        <meta name="twitter:url" content="https://parlehmate.onrender.com/" />

        <title>{{%title%}}</title>
        {{%favicon%}}
        {{%css%}}
    </head>
    <body>
        {{%app_entry%}}
        <footer>
            {{%config%}}
            {{%scripts%}}
            {{%renderer%}}
        </footer>
    </body>
</html>
'''


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

                html.Div(id='bill-summaries-page', children=bill_summaries_layout(), style={'display': 'none'}),

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
                "bill_summaries": Output('bill-summaries-page', 'style'),
                "topics_questions": Output('topics-questions-page', 'style'),
                "demographics": Output('demographics-page', 'style'),
                "methodology": Output('methodology-page', 'style'),
                "about": Output('about-page', 'style'),
                "404": Output('404-page', 'style')}

# Flask route to serve sitemap.xml
@server.route('/sitemap.xml', methods=['GET'])
def sitemap():
    sitemap_xml = generate_sitemap()
    return Response(sitemap_xml, mimetype='application/xml')

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

policy_positions_callbacks(app, data)
bill_summaries_callbacks(app, data)
member_metrics_callbacks(app, data)
topics_questions_callbacks(app, data)
demographics_callbacks(app, data)

# Run the app
if __name__ == "__main__" and os.environ.get('ENVIRONMENT') == 'development':
    app.run_server(debug=True)
