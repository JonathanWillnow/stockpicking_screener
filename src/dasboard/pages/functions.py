"""
    This file contains several functions that are used on the Dash-App in different pages and for different processes. Therefore, I decided to refactor them into a seperate file.
"""

import dash
from dash import dcc, html
import pandas as pd
import json
import numpy as np
import dash_bootstrap_components as dbc
from dash.dependencies import Output, Input, State
import urllib.request, json

import yfinance as yf

from datetime import datetime

# 'ticker', 'date', 'industry', 'de_ticker', 'enterpriseValue',
#        'marketCap', 'forwardPE', 'trailingPE', 'profitMargins', 'floatShares',
#        'sharesOutstanding', 'priceToBook', 'heldPercentInsiders', 'bookValue',
#        'priceToSalesTrailing12Months', 'trailingEps', 'forwardEps', 'pegRatio',
#        'enterpriseToRevenue', 'enterpriseToEbitda', 'dividendYield',
#        'currentPrice', 'quickRatio', 'currentRatio', 'debtToEquity',
#        'returnOnAssets', 'returnOnEquity', 'revenueGrowth', 'grossMargins',
#        'ebitdaMargins', 'operatingMargins', 'years_available', 'RevGrowth',
#        'GrossProfitGrowth', 'OpIncomeGrowth', 'FF_Quality_Growth',
#        'FF_Quality_actual', 'FF_Quality_mean', 'FF_Assets_Growth_mean',
#        'FF_Assets_Growth_actual', 'PB_percentile', 'EV_percentile',
#        'MC_percentile', 'PS_percentile', 'EToRev_precentile',
#        'EToEbitda_percentile', 'FFA_m_percentile', 'FF_Cons_actual_percentile',
#        'ROE(inv)_percentile', 'FFQ(inv)_g_percentile', 'FFQ(inv)_a_percentile',
#        'FFQ(inv)_m_percentile', 'RV Score']


def getBusinessSummary(ticker):
    """
    Function to get the BusinessSummary, including employees and the official webiste of a company in Real Time.
    This is achieved by using urllib.requests and finance.yahoo.com.

    Inputs:
        ticker(str): The ticker symbol of the listed company for which we want to obtain the information about its business.

    Returns:
        A dictionary containing longBusinessSummary, fullTimeEmployees, and the official website.

    """
    query_url_1 = (
        "https://query2.finance.yahoo.com/v10/finance/quoteSummary/"
        + str(ticker)
        + "?modules=assetProfile"
    )
    info_dict = {}
    info_ls = ["longBusinessSummary", "fullTimeEmployees", "website"]
    with urllib.request.urlopen(query_url_1) as url:
        parsed_1 = json.loads(url.read().decode())
    for metric in info_ls:
        try:
            info_dict[metric] = parsed_1["quoteSummary"]["result"][0]["assetProfile"][
                metric
            ]
        except:
            info_dict[metric] = "-"
    return info_dict


def reorder_naming(frame):
    """
    Function reorder and rename the dataset for the Dash-App before loading it into a Dashtable.

    Inputs:
        frame(pd.DataFrame): Dataset of stocks.

    Returns:
        A pd.DataFrame that has a different ordering / naming, according to the function.
    """
    frame_d = frame[
        [
            "ticker",
            "industry",
            "RV Score",
            "priceToBook",
            "FF_Assets_Growth_mean",
            "FF_Quality_actual",
            "FF_Quality_Growth",
            "returnOnEquity",
            "returnOnAssets",
            "priceToSalesTrailing12Months",
            "enterpriseToRevenue",
            "PB_percentile",
            "MC_percentile",
            "FF_Cons_actual_percentile",
            "FFA_m_percentile",
            "FFQ(inv)_a_percentile",
            "FFQ(inv)_g_percentile",
            "ROE(inv)_percentile",
            "PS_percentile",
            "EToRev_precentile",
            "EToEbitda_percentile",
            "forwardPE",
            "trailingPE",
            "profitMargins",
            "trailingEps",
            "forwardEps",
            "pegRatio",
            "enterpriseToEbitda",
            "dividendYield",
            "currentPrice",
            "quickRatio",
            "currentRatio",
            "debtToEquity",
            # "revenueGrowth",
            "grossMargins",
            "ebitdaMargins",
            "operatingMargins",
            "RevGrowth",
            "GrossProfitGrowth",
            "OpIncomeGrowth",
            "enterpriseValue",
            "marketCap",
            "floatShares",
            "sharesOutstanding",
            "heldPercentInsiders",
        ]
    ].dropna(
        subset=[
            "MC_percentile",
            "PB_percentile",
            "FF_Cons_actual_percentile",
            "FFQ(inv)_a_percentile",
            "industry",
            "ticker",
        ]
    )
    frame_d.rename(
        columns={
            "RV Score": "Score",
            "priceToBook": "P/B",
            "FF_Assets_Growth_mean": "FFA",
            "FF_Quality_actual": "FFQ",
            "FF_Quality_Growth": "d FFQ",
            "returnOnEquity": "ROE",
            "returnOnAssets": "ROA",
            "priceToSalesTrailing12Months": "P/S",
            "enterpriseToRevenue": "EV/RV",
            "PB_percentile": "PB per",
            "MC_percentile": "MC per",
            "FF_Cons_actual_percentile": "act. FFA per",
            "FFA_m_percentile": "mean FFA per",
            "FFQ(inv)_a_percentile": "FFQ(i) per",
            "FFQ(inv)_g_percentile": "dFFQ(i) per",
            "ROE(inv)_percentile": "ROE(i) per",
            "PS_percentile": "P/S per",
            "EToRev_precentile": "EV/RV per",
            "EToEbitda_percentile": "EV/Ebitda per",
            "forwardPE": "P/E",
            "trailingPE": "P/E TTM",
            "profitMargins": "PMargin",
            "trailingEps": "EPS TTM",
            "forwardEps": "EPS forw.",
            "pegRatio": "PEG",
            "enterpriseToEbitda": "EVEbitda",
            "dividendYield": "yield",
            "quickRatio": "QRatio",
            "currentRatio": "CRatio",
            "debtToEquity": "DEquity",
            "grossMargins": "GMargin",
            "operatingMargins": "OMargin",
            "RevGrowth": "dRev",
            "GrossProfitGrowth": "dGrossP",
            "OpIncomeGrowth": "dOpInc",
            "enterpriseValue": "EV",
            "marketCap": "MC",
            "floatShares": "float",
            "sharesOutstanding": "SharesOut",
            "heldPercentInsiders": "Insider",
        },
        inplace=True,
    )
    return frame_d


def realized_volatility(x):
    """
    Function to calculate the realized volatility of a stock. This is not in used yet, but will be implemented in the future for further risk analysis.

    Inputs:
        TBD

    Returns:
        TBD
    """
    return np.sqrt(np.sum(x**2))


def get_data_d(TICKR):
    """
    Function to build the chart of a specific stock on the Dash-App.
    This function uses the finance.yahoo.com API to obtain daily closing prices for the selected ticker to then build up a chart from it.

    Inputs:
        TICKR(str): Ticker of a specific stock.

    Returns:
        A pd.DataFrame that contains the simple return as well as log. return of the specified stock.
    """
    df_yahoo = yf.download(
        TICKR,
        start="2000-01-01",
        end=datetime.today().strftime("%Y-%m-%d"),
        progress=False,
    )
    df = df_yahoo.loc[:, ["Adj Close"]]
    df.rename(columns={"Adj Close": "adj_close"}, inplace=True)
    df["simple_rtn"] = df.adj_close.pct_change()
    df["log_rtn"] = np.log(df.adj_close / df.adj_close.shift(1))
    return df


def get_data_m(TICKR):
    df_yahoo = yf.download(
        TICKR,
        start="2000-01-01",
        end=datetime.today().strftime("%Y-%m-%d"),
        progress=False,
    )
    df = df_yahoo.loc[:, ["Adj Close"]]
    df.rename(columns={"Adj Close": "adj_close"}, inplace=True)
    pd.to_datetime(df.index)
    df_mm = df.resample("1M").mean()
    df_mm["simple_rtn"] = df.adj_close.pct_change()
    df_mm["log_rtn"] = np.log(df.adj_close / df.adj_close.shift(1))
    return df_mm


def indentify_outliers(row, n_sigmas=3):
    x = row["simple_rtn"]
    mu = row["mean"]
    sigma = row["std"]
    if (x > mu + 3 * sigma) | (x < mu - 3 * sigma):
        return 1
    else:
        return 0


START_DATE = "2019-01-01"
END_DATE = "2020-12-31"

from pandas_datareader.famafrench import get_available_datasets
import pandas_datareader.data as web
import pandas as pd

ff_dict = web.DataReader(
    "F-F_Research_Data_Factors", "famafrench", start=START_DATE, end=END_DATE
)  # default is monthly  #ff_dict.keys()  #print(ff_dict["DESCR"])
factor_df = ff_dict[0]  # monthly factors. 1 for annual
factor_df.rename(
    columns={"Mkt-RF": "mkt_rf", "SMB": "smb", "HML": "hml", "RF": "rf"}, inplace=True
)
factor_df["mkt"] = factor_df.mkt_rf + factor_df.rf
factor_df = factor_df.apply(pd.to_numeric, errors="coerce").div(100)

# Some stuff to play arroudn for now
