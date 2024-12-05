from dash import html
import dash_bootstrap_components as dbc
from dash_iconify import DashIconify

# Home page layout
home_page = html.Div(
    [
        html.H2("Find out what's going on in the SG Parliament!"),
        html.P("Note that this is still a work in progress!"),
    ]
)

# Navbar
import dash_bootstrap_components as dbc
from dash import html

navbar = dbc.Navbar(
    [
        dbc.Button(
            DashIconify(icon="mdi:menu", width=24, height=24),  # Set desired icon size
            color="primary",
            className="me-2 d-md-none",
            id="sidebar-toggle",
            n_clicks=0,
            style={
                "border": "none",                               # Remove border
                "padding": "0",                                 # Remove padding
                "width": "40px",                                # Set fixed width
                "height": "40px",                               # Set fixed height
                "display": "flex",                              # Use flex to center the icon
                "alignItems": "center",                         # Vertically center
                "justifyContent": "center",                     # Horizontally center
            }
        ),
        dbc.NavbarBrand("Parleh-mate!", className="ms-2"),
    ],
    color="light",
    dark=False,
    sticky="top",
    className="custom-navbar"  # Apply the custom CSS class
)


# Sidebar content
sidebar_content = [
    dbc.Nav(
        [
            dbc.NavLink("Parleh-mate", href="/", active="exact"),
            dbc.NavLink("Member metrics", href="/member_metrics", active="exact"),
            dbc.NavLink("Policy Positions", href="/policy_positions", active="exact"), 
            #dbc.NavLink("Bills", href="/bills", active="exact"),
            dbc.NavLink("Topics", href="/topics", active="exact"), 
            dbc.NavLink("Topics and Questions", href="/topics_questions", active="exact"),
            dbc.NavLink("Demographics", href="/demographics", active="exact"),
            dbc.NavLink("Methodology", href="/methodology", active="exact"),  
            dbc.NavLink("About", href="/about", active="exact"),          
        ],
        vertical=True,
        pills=True,
    ),
]

# Sidebar
sidebar = html.Div(sidebar_content, id="sidebar", className="sidebar d-none d-md-block")