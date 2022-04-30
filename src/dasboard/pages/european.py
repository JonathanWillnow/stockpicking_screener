import dash
from dash import dcc, html
import pandas as pd
import json
import numpy as np
import dash_bootstrap_components as dbc
from dash.dependencies import Output, Input, State

import yfinance as yf

from pages.functions import *

data_input_eu = round(
    pd.read_pickle("processed_data/f_proc_2022-03-05_val2_euro600.pkl"), 3
)
data = reorder_naming(data_input_eu)  # .sort_values("ticker", inplace=True)


layout = html.Div(
    children=[
        html.H1(children="European Stocks", className="header-title"),
        html.P(
            children="Browse through the european Stocks",
            className="header-description",
        ),
        html.Div(
            dash.dash_table.DataTable(
                id="table-paging-with-graph-eu",
                columns=[{"name": i, "id": i} for i in data.columns],
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
        html.Div(id="click-info-eu", style={"whiteSpace": "pre-wrap"}),
        html.Div(id="click-data-eu", style={"whiteSpace": "pre-wrap"}),
        html.H3(
            children="Further Analysis on selected metrics",
            style={"textAlign": "center", "margin-top": "50px"},
        ),
        html.Div(
            id="table-paging-with-graph-container-eu",
            className="five columns",
            # style={"margin-top": "25px"},
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
    """
    This is the function that provides the filtering for the datatable in the form of de3cending / ascending ordering.
    """
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
    Output("table-paging-with-graph-eu", "data"),
    Input("table-paging-with-graph-eu", "page_current"),
    Input("table-paging-with-graph-eu", "page_size"),
    Input("table-paging-with-graph-eu", "sort_by"),
    Input("table-paging-with-graph-eu", "filter_query"),
)
def update_table(page_current, page_size, sort_by, filter):
    """
    This is the function that provides the precise filtering based on a subset of operators.
    """
    filtering_expressions = filter.split(" && ")
    dff = data
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
    Output("table-paging-with-graph-container-eu", "children"),
    Input("table-paging-with-graph-eu", "data"),
)
def update_graph(rows):
    """
    This is the function that provides further graphs with metrics for the current stocks in the Datatable.
    """
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
    Output("click-data-eu", "children"),
    [Input("table-paging-with-graph-eu", "active_cell")],
    # (A) pass table as data input to get current value from active cell "coordinates"
    [State("table-paging-with-graph-eu", "data")],
)
def display_click_data(active_cell, table_data):
    """
    This is the function that gets the closing prices of the stock that is cklicked on and provides a stockchart powered by finance.yahoo.com.
    """
    if active_cell:
        cell = json.dumps(active_cell, indent=2)
        row = active_cell["row"]
        col = active_cell["column_id"]
        value = table_data[row]["ticker"]
        # out = '%s\n%s' % (cell, value)
    else:
        return html.Div()
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
    Output("click-info-eu", "children"),
    [Input("table-paging-with-graph-eu", "active_cell")],
    [State("table-paging-with-graph-eu", "data")],
)
def display_info_data(active_cell, table_data):
    """
    This is the function that obtains the information about the company based on its descriptive information provided by finance.yahoo.com.
    """
    if active_cell:
        row = active_cell["row"]
        value = table_data[row]["ticker"]
    else:
        return html.Div()
    info_dict = getBusinessSummary(value)
    return html.Div(
        children=[
            html.H1(
                children=f"Infos about {value}",
                style={"margin-top": "25px"},
                className="header-title-2",
            ),
            html.P(
                children=info_dict["longBusinessSummary"],
                className="justified",
            ),
            html.H5(children="Full-time employees", className="header-title-3"),
            html.P(
                children="Number of full-time employees: "
                + str(info_dict["fullTimeEmployees"]),
                className="justified",
            ),
            html.H5(children="More information", className="header-title-3"),
            html.P(
                html.A(str(info_dict["website"]), href=str(info_dict["website"])),
                className="justified",
            ),
        ]
    )
