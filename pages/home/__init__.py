from dash import html
import dash_bootstrap_components as dbc

# Home page layout
home_page = html.Div(
    [
        html.H1("Welcome to the Parliamentary Analysis App"),
        html.P("Explore parliamentary speeches and topics."),
    ]
)

# Navbar
navbar = dbc.Navbar(
    [
        dbc.Button(html.Span(className="navbar-toggler-icon"), color="primary", className="me-2 d-md-none",
                   id="sidebar-toggle", n_clicks=0),
        dbc.NavbarBrand("Parliamentary Analysis", className="ms-2"),
    ],
    color="light",
    dark=False,
    sticky="top",
)

# Sidebar content
sidebar_content = [
    dbc.Nav(
        [
            dbc.NavLink("Parleh-mate", href="/", active="exact"),
            dbc.NavLink("Speeches", href="/speeches", active="exact"),
            # Removed Page 2 Link
        ],
        vertical=True,
        pills=True,
    ),
]

# Sidebar
sidebar = html.Div(sidebar_content, id="sidebar", className="sidebar d-none d-md-block")