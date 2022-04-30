import dash
from dash import dcc, html
import pandas as pd
import json
import numpy as np
import dash_bootstrap_components as dbc
from dash.dependencies import Output, Input, State


import yfinance as yf


from pages.functions import *

data_input_america_1 = pd.read_pickle("processed_data/f_proc_2022-03-05_val2_nyse.pkl"
)
data_input_america_2 = pd.read_pickle("processed_data/f_proc_2022-03-05_val2_nasdaq.pkl"
)
data_input_america_3 = pd.read_pickle("processed_data/f_proc_2022-03-05_val2_amex.pkl"
)

data_american_input = round(
    pd.concat([data_input_america_1, data_input_america_2, data_input_america_3]), 3
)

data_american = reorder_naming(data_american_input)#.sort_values("ticker", inplace=True)

layout = html.Div(
    children=[
        html.H1(children="American Stocks", className="header-title"),
        html.P(
            children="Browse through the american stocks, selected from AMEX, NYSE and NASDAQ",
            className="header-description",
        ),
        html.Div(
            dash.dash_table.DataTable(
                id="table-paging-with-graph-american",
                columns=[{"name": i, "id": i} for i in data_american.columns],
                page_current=0,
                page_size=20,
                page_action="custom",
                filter_action="custom",
                filter_query="",
                sort_action="custom",
                sort_mode="multi",
                sort_by=[],
            ),
            style={"height": 750, "overflowY": "scroll", "overflowX": "scroll"},
            # className='six columns'
        ),
        html.Div(id="click-info-am", style={"whiteSpace": "pre-wrap"}),
        html.Div(id="click-data-am", style={"whiteSpace": "pre-wrap"}),
         html.H3(children="Further Analysis on selected metrics",
        style={'textAlign': 'center', 'margin-top': '50px'}),
        html.Div(
            id="table-paging-with-graph-container-american",
            className="five columns",
            style={"margin-top": "25px"},
        ),
    ]
)


operators = [
    ["ge ", ">="],
    ["le ", "<="],
    ["lt ", "<"],
    ["gt ", ">"],
    ["ne ", "!="],
    ["eq ", "="],
    ["contains "],
    ["datestartswith "],
]


def split_filter_part(filter_part):
    for operator_type in operators:
        for operator in operator_type:
            if operator in filter_part:
                name_part, value_part = filter_part.split(operator, 1)
                name = name_part[name_part.find("{") + 1 : name_part.rfind("}")]

                value_part = value_part.strip()
                v0 = value_part[0]
                if v0 == value_part[-1] and v0 in ("'", '"', "`"):
                    value = value_part[1:-1].replace("\\" + v0, v0)
                else:
                    try:
                        value = float(value_part)
                    except ValueError:
                        value = value_part

                # word operators need spaces after them in the filter string,
                # but we don't want these later
                return name, operator_type[0].strip(), value

    return [None] * 3


@dash.callback(
    Output("table-paging-with-graph-american", "data"),
    Input("table-paging-with-graph-american", "page_current"),
    Input("table-paging-with-graph-american", "page_size"),
    Input("table-paging-with-graph-american", "sort_by"),
    Input("table-paging-with-graph-american", "filter_query"),
)
def update_table(page_current, page_size, sort_by, filter):
    filtering_expressions = filter.split(" && ")
    dff = data_american
    for filter_part in filtering_expressions:
        col_name, operator, filter_value = split_filter_part(filter_part)

        if operator in ("eq", "ne", "lt", "le", "gt", "ge"):
            # these operators match pandas series operator method names
            dff = dff.loc[getattr(dff[col_name], operator)(filter_value)]
        elif operator == "contains":
            dff = dff.loc[dff[col_name].str.contains(filter_value)]
        elif operator == "datestartswith":
            # this is a simplification of the front-end filtering logic,
            # only works with complete fields in standard format
            dff = dff.loc[dff[col_name].str.startswith(filter_value)]

    if len(sort_by):
        dff = dff.sort_values(
            [col["column_id"] for col in sort_by],
            ascending=[col["direction"] == "asc" for col in sort_by],
            inplace=False,
        )

    return dff.iloc[page_current * page_size : (page_current + 1) * page_size].to_dict(
        "records"
    )


@dash.callback(
    Output("table-paging-with-graph-container-american", "children"),
    Input("table-paging-with-graph-american", "data"),
)
def update_graph(rows):
    dff = pd.DataFrame(rows)
    return html.Div(
        [
            dcc.Graph(
                id=column,
                figure={
                    "data": [
                        {
                            "x": dff["ticker"],
                            "y": dff[column] if column in dff else [],
                            "type": "bar",
                            "marker": {"color": "#0074D9"},
                        }
                    ],
                    "layout": {
                        "xaxis": {"automargin": True},
                        "yaxis": {"automargin": True},
                        "height": 350,
                        "title": column,
                        "margin": {"t": 35, "l": 10, "r": 10},
                    },
                },
            )
            for column in [
                "Score",
                "P/B",
                "FFA",
                "FFQ",
                "d FFQ",
                "ROE",
                "ROA",
            ]
        ]
    )


# define callback
@dash.callback(
    Output("click-data-am", "children"),
    [Input("table-paging-with-graph-american", "active_cell")],
    # (A) pass table as data input to get current value from active cell "coordinates"
    [State("table-paging-with-graph-american", "data")],
)
def display_click_data(active_cell, table_data):
    if active_cell:

        row = active_cell["row"]

        value = table_data[row]["ticker"]

    else:
        return html.Div(
       )
    dff = get_data_d(value)
    return html.Div(
        dcc.Graph(
            figure={
                "data": [
                    {
                        "x": dff.index,
                        "y": dff["adj_close"],
                        "type": "lines",
                        "marker": {"color": "#0074D9"},
                    }
                ],
                "layout": {
                    "xaxis": {"automargin": True},
                    "yaxis": {"automargin": True},
                    "height": 400,
                    "title": f"Chart for {value}",
                    "margin": {"t": 35, "l": 10, "r": 10},
                },
            },
        )
    )

@dash.callback(
    Output("click-info-am", "children"),
    [Input("table-paging-with-graph-american", "active_cell")],
    [State("table-paging-with-graph-american", "data")],
)
def display_info_data(active_cell, table_data):
    if active_cell:
        row = active_cell["row"]
        value = table_data[row]["ticker"]
    else:
        return
    info_dict = getBusinessSummary(value)
    return html.Div(
        children=[
        html.H1(children=f"Infos about {value}",
        style={"margin-top": "25px"},
        className="header-title-2"),
        html.P(
            children=info_dict["longBusinessSummary"],
            className="justified",
        ), 
        html.H5(children="Full-time employees", className="header-title-3"),
        html.P(
            children="Number of full-time employees: " +str(info_dict["fullTimeEmployees"]),
            className="justified",
        ),
        html.H5(children="More information", className="header-title-3"),
        html.P(
            html.A(str(info_dict["website"]), href=str(info_dict["website"])),
    
            className="justified",
        )
        ]
    )

