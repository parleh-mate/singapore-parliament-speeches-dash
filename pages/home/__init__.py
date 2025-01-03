from dash import html
import dash_bootstrap_components as dbc
from dash_iconify import DashIconify

home_page = dbc.Container(
    [
        dbc.Row(
            dbc.Col(
                [
                    # Header
                    html.H3(
                        "Find out what's going on in the Singapore Parliament!",
                        style={"margin-bottom": "10px"}  # Optional: Adds space below the header
                    ),
                    
                    # Image Insertion
                    html.Img(
                        src="/assets/singapore_parliament_house.png",
                        alt="Singapore Parliament House",
                        className="img-fluid",  # Makes the image responsive
                        style={"width": "100%", "display": "block", "margin-left": "auto", "margin-right": "auto"}  # Full width, centered
                    ),
                    
                    # Caption for the Image
                    html.Small(
                        "ProjectManhattan., CC BY-SA 3.0, via Wikimedia Commons",
                        className="text-muted",  # Applies muted text color
                        style={"display": "block", "margin-top": "5px"}  # Ensures caption is below the image with a small top margin
                    )
                ],
                width=12,  # Makes the column span the full width of the container
                className="text-center"  # Centers all content within the column
            )
        )
    ],
    fluid=True,  # Makes the container full-width relative to the viewport
    style={
        "padding-left": "50px",    # 50px padding on the left
        "padding-right": "50px",   # 50px padding on the right
        "padding-top": "50px",     # 50px padding at the top
        "padding-bottom": "0px"    # No padding at the bottom
    }
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
            dbc.NavLink("Policy Positions", href="/policy_positions", active="exact"), 
            dbc.NavLink("Bill Summaries", href="/bill_summaries", active="exact"),
            dbc.NavLink("Member Metrics", href="/member_metrics", active="exact"),
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