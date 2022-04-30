from dash import dcc, html, Input, Output, callback

layout = html.Div(
    children=[
        html.H1(children="Documentation", className="header-title"),
        html.P(
            children=[
                html.P(
                    "This is the final project for the course Effective Programming Practices for Economists"
                    + " by Prof. Gaudecker in the winterterm 21/22 of the University of Bonn by Jonathan Willnow. \n"
                ),
                "The project repository is avaialble ",
                html.A(
                    "on Github",
                    href="https://github.com/JonathanWillnow/european_factor_stockpicking_screener",
                ),
            ],
            className="justified",
        ),
        html.P(
            children=[
                html.H5(children="Purpose", className="header-title-2"),
                html.P(
                    children="In recent years, there was a rising interest in investing and personal fincance"
                    + " for indiviudal private investors. While this was especially driven and pronounced in the"
                    + " recovery of the covid-19 crash and fueled by pressumed easy gains, reddit boards,"
                    + " meme stocks and false assumptions, a whole new generation of investors entered the"
                    + " capital markets. While for the majority of private investors it holds true that they"
                    + " should invest in an index fund, this project tries to provide an easy, scientific proofen"
                    + " concept towards stock picking and the managing of our own finances using factor investing.",
                    className="justified",
                ),
                html.H5(children="Idea and Methodology", className="header-title-2"),
                html.P(
                    children=[
                        " Stock market participation increased in the last years. While this is overall a positive development,"
                        + " many investors lack tools to base their investments on or are solely using their"
                        + " gut feeling and intuition. While there are many great tools available (some which are really expensive),"
                        + " I could not find a free tool that allows a comparison of stocks based on the Fama French Asset Pricing Factors - so I "
                        + " decided to build it myself.",
                        html.P(
                            "As this is work in progress, it is not available right now for the broad audience"
                            + " (would require some up scaling of the website), but I shared the results in a developed Dash-App with a big German speaking"
                            + " stock picking community, called Kleine Finanzzeitung. The Dash-App allows users to access my results and my"
                            + " research without having a proper background in programming and git."
                        ),
                        html.P(
                            " The idea appears simple: There exist more than only one risk factor beta that determines the"
                            + " performance of a portfolio (here, portfolio is assumed to be a index / market portfolio)."
                            + " Fama and French came up with the Fama and French three factor model that includes"
                            + " the size of firms, their book-to-market values, and their excess return on the market. In other words,"
                            + " the three factors used are SMB (small minus big), HML (high minus low), and the"
                            + " market return return less the risk-free rate of return. Building up on their work, many other"
                            + " factors have been researched and found like the Fama French Quality Factor and Conservative"
                            + " Asset factor or the Carhardt Momentum Factor. While the Momentum Factor finds strong"
                            + " empirical support like the other factors, this project so far is limited to the factors"
                            + " found by Fama and French. "
                        ),
                        "A selection of individual Stocks is available for Europe, Germany, Japan and North America"
                        + " that was collected using several scrapers and validation methods. To obtain reliable metrics"
                        + " the metrics are collected from ",
                        html.A("Yahoo Finance", href="https://finance.yahoo.com"),
                        " used to compute the introduced factors according "
                        + " to the work of Fama and French. To present the "
                        + " results and allow for easy filtering, I decided to deploy this simple Dash App.",
                    ],
                    className="justified",
                ),
                html.H5(
                    children="Further Development and Outlook",
                    className="header-title-2",
                ),
                html.P(
                    children=[
                        "This project is not finished and work in progress. After I started it for the course Effective Programming Practices for Economists,"
                        + " I became aware of all the possible extensions that I could develop and implement."
                        + " As outlined, I want to make it Open Source and will try to find other coding and finance enthusiasts who want to work with me on this project."
                        + " Some things that are in my mind:",
                        html.P(""),
                        html.P(
                            "- Risk analysis for the stocks using volatility, downside volatility"
                        ),
                        html.P(
                            "- Moving from Dash to a pure Flask App. This would be faster and enables more possibilities"
                        ),
                        html.P(
                            "- Scaling up the website (this would require me to pay fees to Heroku. As for now, the service I am using is free). This also includes using a cloud solution for hosting the data"
                        ),
                        html.P(
                            "- Adding more stocks! I was thinking about every major stock exchange in europe and also including more emerging markets stocks"
                        ),
                        html.P(
                            "- Detecting outliers and anomalies / better filtering of the results"
                        ),
                        html.P(
                            "- Fixing my Score. Right now, the score is subject to outliers. For instance bancrupt companies show great scores since they have a low MC and a low P/B ratio. But I have to find a way to make the score robust to this"
                        ),
                        html.P("- Back-testing my Score"),
                        html.P("- Improving general code quality and speed"),
                    ],
                    className="justified",
                ),
            ]
        ),
    ]
)
