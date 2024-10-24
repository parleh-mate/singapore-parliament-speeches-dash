from dash import html
import dash_bootstrap_components as dbc

def methodology_layout():
    return html.Div(
        [
            html.H1("Methodology/FAQ"),
            html.P(
                "This section describes how our data is sourced and transformed into the graphs and tables you see on the app. Our aim is to be as transparent as possible and provide users with the necessary context to understand what they are looking at."
            ),
            
            # Table of Contents
            html.H4("Methodology"),
            html.Ul([
                html.Li(html.A("Data Sourcing", href="#datasourcing-method")),
                html.Li(html.A("Participation", href="#participation-method")),
                html.Li(html.A("Speeches", href="#speeches-method")),
                html.Li(html.A("Demographics", href="#demographics-method")),
            ]),

            html.H2("Data Sourcing", id="datasourcing-method"),
            html.P(
                "All data comes courtesy of the Singapore Parliament Hansards."
            ),
            
            
            html.H2("Participation", id="participation-method"),
            html.P(
                "Lorem ipsum dolor sit amet, consectetur adipiscing elit. "
                "Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua."
            ),
            
            
            html.H2("Speeches", id="speeches-method"),
            html.P(
                "Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat."
            ),
            
            
            html.H2("Demographics", id="demographics-method"),
            html.P(
                "Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur."
            ),
        ],
        className='content',
        style={'padding': '20px'}
    )
