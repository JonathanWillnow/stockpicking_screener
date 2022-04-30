from dash import dcc, html, Input, Output, callback

layout = html.Div(
    children=[
        html.H1(children="Impressum", className="header-title"),
        html.P(
            children=[
                "This is the final project for the course Effective Programming Practices for Economists"
                + " by Prof. Gaudecker in the winterterm 21/22 of the University of Bonn by Jonathan Willnow. \n"
                + "The project repository is avaialble ",
                html.A(
                    "on Github",
                    href="https://github.com/JonathanWillnow/european_factor_stockpicking_screener",
                ),
            ],
            className="justified",
        ),
        html.H5(children="Contatct", className="header-title-2"),
        html.P(
            children=[
                "Feel free to contact me via Github or ",
                html.A(
                    "LinkedIn",
                    href="https://www.linkedin.com/in/jonathan-willnow-1672881ab/",
                ),
            ],
            className="justified",
        ),
    ]
)
