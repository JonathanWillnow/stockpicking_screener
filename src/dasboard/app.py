import dash
import dash_bootstrap_components as dbc
from dash import dcc, html
import plotly.express as px
from dash.dependencies import Input, Output
import pandas as pd
from pages import (
    landing_page,
    european,
    german,
    american,
    japanese,
    documentation,
    impressum,
)

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.LUX])
server = app.server


# styling the sidebar
SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "16rem",
    "padding": "2rem 1rem",
    "background-color": "#f8f9fa",
}

# padding for the page content
CONTENT_STYLE = {
    "margin-left": "18rem",
    "margin-right": "2rem",
    "padding": "2rem 1rem",
}

sidebar = html.Div(
    [
        html.H3("Navigator", className="display-6"),
        html.Hr(),
        html.P("Navigate through our content", className="lead"),
        dbc.Nav(
            [
                dbc.NavLink("Home", href="/", active="exact"),
                dbc.NavLink("EU Factors", href="/european", active="exact"),
                dbc.NavLink("DE Factors", href="/german", active="exact"),
                dbc.NavLink("USA Factors", href="/american", active="exact"),
                dbc.NavLink("Japan Factors", href="/japanese", active="exact"),
                dbc.NavLink("Documentation", href="/documentation", active="exact"),
                dbc.NavLink("Impressum", href="/impressum", active="exact"),
            ],
            vertical=True,
            pills=True,
        ),
    ],
    style=SIDEBAR_STYLE,
)

content = html.Div(id="page-content", children=[], style=CONTENT_STYLE)

app.layout = html.Div([dcc.Location(id="url"), sidebar, content])


@app.callback(Output("page-content", "children"), [Input("url", "pathname")])
def render_page_content(pathname):
    if pathname == "/":
        return landing_page.layout
    elif pathname == "/european":
        return european.layout
    elif pathname == "/american":
        return american.layout
    elif pathname == "/japanese":
        return japanese.layout
    elif pathname == "/documentation":
        return documentation.layout
    elif pathname == "/impressum":
        return impressum.layout
    elif pathname == "/german":
        return german.layout


if __name__ == "__main__":
    app.run_server(debug=True)
