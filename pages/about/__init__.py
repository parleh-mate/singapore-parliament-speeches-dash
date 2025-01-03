from dash import html
import dash_bootstrap_components as dbc

def about_layout():
    return dbc.Container(
        [
            dbc.Row(
                dbc.Col(
                    [
                        html.H1("About"),
                        html.P([
                            "Parleh-mate is a non partisan, independent project with no affiliation to the Singapore Parliament or government whatsoever. It was created with the intention of shedding light on the goings-on in the Singapore Parliament. Our goal is to make more accessible information that is already out there and allow users to draw their own conclusions.",
                            html.Br(),    
                            html.Br(),                            
                            "The project is wholly maintained by a group of volunteers. If you find this resource useful, consider ",
                            html.A(
                                "buying us a coffee",
                                href="https://buymeacoffee.com/parlehmate", 
                                target="_blank",  # Opens the link in a new tab
                                style={'color': '#007bff', 'textDecoration': 'underline'}
                            ),
                            " to help keep it going."
                    ]),
                        html.Br(),
                        html.P([
                            "Please send email inquiries to singapore.parliament.speeches@gmail.com. For more information visit the ",
                            html.A(
                                "Github repository",
                                href="https://github.com/parleh-mate",
                                target="_blank",  # Opens the link in a new tab
                                style={'color': '#007bff', 'textDecoration': 'underline'}
                            ),
                            "."
                            ])
                    ],
                    width=10  # Occupy 10 out of 12 columns (~83.33% width)
                ),
                justify="center"  # Center the column within the row
            ),
        ],
        fluid=True,  # Ensures the container spans the full width of the viewport
        style={'padding': '20px'}
    )




            