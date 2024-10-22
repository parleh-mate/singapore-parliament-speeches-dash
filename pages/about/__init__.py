from dash import html

def about_layout():
    return html.Div(
        [
            html.H1("About"),
            html.P(
                "Some about stuff."
            )
        ],
        className='content',
        style={'padding': '20px'}
    )
