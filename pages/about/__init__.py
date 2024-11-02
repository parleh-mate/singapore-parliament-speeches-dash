from dash import html
import dash_bootstrap_components as dbc

def about_layout():
    return dbc.Container(
        [
            dbc.Row(
                dbc.Col(
                    [
                        html.H1("About"),
                        html.P(
                            "Par-leh-mate was created with the intention of shedding light on the goings-on in the Singapore Parliament. It is intended as a tool for citizens to understand better how their MPs represent their interests and is not intended to be political in nature."
                            ),
                        html.Br(),
                        html.Br(),
                        html.P("Please send email inquiries to xx. For more information visit the Github page: xx")
                    ],
                    width=10  # Occupy 10 out of 12 columns (~83.33% width)
                ),
                justify="center"  # Center the column within the row
            ),
        ],
        fluid=True,  # Ensures the container spans the full width of the viewport
        style={'padding': '20px'}
    )




            