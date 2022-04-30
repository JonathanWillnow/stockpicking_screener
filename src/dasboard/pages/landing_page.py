from dash import dcc, html, Input, Output, callback

layout = html.Div(
    children=[
        html.H1(children="Factor Stockscreener", className="header-title"),
        html.P(
            children="Analyze your favorite stocks with different Asset-Pricing-Factors and compare them to their peers",
            className="header-description",
        ),
        html.P(""),
        html.P(""),
        html.H1(children="A simple guide", className="header-title-2"),
        html.P(
            children=[
                html.P(
                    "Ever wondered which is the best stock out of the EuroStoxx600 based on the Fama French Quality Score but you were to lazy to calculate it yourself?"
                    + " This is just one thing that you can easily look up using this App."
                ),
                html.P(
                    "For a start, select one of the four different regions for which there is currently data available."
                    + " As you will see, you can easily browse through all different columns and change their ordering. In addition to this, you can search for different criteria"
                    + " simply by using a set of operators ( >=, <=, <, >, !=,  = , contains). Moreover, when you click on any abitrarly choosen field in the table, a long term"
                    + " (max dated back to the 01.01.2000) stockchart will appear as well as a selection of important information about the company, provided via the"
                    + " finance.yahoo.com API in real time."
                ),
            ],
            className="justified",
        ),
    ]
)
