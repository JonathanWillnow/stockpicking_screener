"""
This code is the core of this project. It is used for collecting and calculating all the metrics wich will be used for https://stockpickingapp.herokuapp.com.
It is planned to collect the metrics of the stocks every week, or every 2 weeks. In a future version and once enough weekly or two-weekly period data is collected,
the Dash-App shall also incorporate this historic metrics.

"""

import itertools
import urllib.request, json, time
from datetime import datetime
import time
import numpy as np
import pandas as pd
from scipy import stats  # The SciPy stats module
from multiprocessing.pool import ThreadPool
import pytask
from src.config import SRC

# from src.data_management.stockinfo_scraper import get_stock_data


def get_data(stockticker):
    """
    Function to obtain a large amounts of mertics from finance.yahoo.com for a specific ticker. This is done by using urllib.requests and exploiting the react frontend of finance.yahoo.com.

    Inputs:
        - stockticker(str): The homeexchange ticker of a specified stock, e.g.: BC8.F for the german Bechtle AG.

    Returns:
        - A pd.DataFrame with metrics. For a list of the metrics that a re currently collected ahve a look at the implementation of the function.


    """
    stock = None

    metrics_list = [
        "enterpriseValue",
        "marketCap",
        "forwardPE",
        "trailingPE",
        "profitMargins",
        "floatShares",
        "sharesOutstanding",
        "priceToBook",
        "heldPercentInsiders",
        "bookValue",
        "priceToSalesTrailing12Months",
        "trailingEps",
        "forwardEps",
        "pegRatio",
        "enterpriseToRevenue",
        "enterpriseToEbitda",
        "dividendYield",
    ]

    financial_list = [
        "currentPrice",
        "quickRatio",
        "currentRatio",
        "debtToEquity",
        "returnOnAssets",
        "returnOnEquity",
        "revenueGrowth",
        "grossMargins",
        "ebitdaMargins",
        "operatingMargins",
        "profitMargins",
    ]  # "PB_percentile", "EV_percentile", "PS_percentile"]

    check_list = [
        "forwardPE",
        "trailingPE",
        "marketCap",
        "priceToSalesTrailing12Months",
        "dividendYield",
    ]

    # get exchange
    # countrycode = stockinfo.ISIN[stockinfo.ticker == stockticker].values[0][:2]

    stock = str(stockticker)  # + ".F"
    print(stock)
    data_dict = {"ticker": stock, "date": datetime.today().strftime("%Y-%m-%d")}
    try:
        query_url_1 = (
            "https://query2.finance.yahoo.com/v10/finance/quoteSummary/"
            + str(stock)
            + "?modules=defaultKeyStatistics"
        )

        with urllib.request.urlopen(query_url_1) as url:
            parsed_1 = json.loads(url.read().decode())
        data_dict["name"] = stockinfo_pkl.name[
            stockinfo_pkl.ticker == stockticker
        ].values[0]
        data_dict["industry"] = stockinfo_pkl.industry[
            stockinfo_pkl.ticker == stockticker
        ].values[0]
        data_dict["de_ticker"] = stockinfo_pkl.de_ticker[
            stockinfo_pkl.ticker == stockticker
        ].values[0]
    except Exception as e:
        print(e)
        print(stockticker)
        data_dict["name"] = np.nan
        data_dict["industry"] = np.nan
        data_dict["de_ticker"] = np.nan

    for metric in metrics_list:
        try:
            data_dict[metric] = parsed_1["quoteSummary"]["result"][0][
                "defaultKeyStatistics"
            ][metric]["raw"]
        except Exception:
            data_dict[metric] = np.nan

    try:
        query_url_2 = (
            "https://query2.finance.yahoo.com/v10/finance/quoteSummary/"
            + str(stock)
            + "?modules=financialData"
        )

        with urllib.request.urlopen(query_url_2) as url:
            parsed_2 = json.loads(url.read().decode())
    except Exception as e:
        print(e)
        print(stockticker)

    for metric in financial_list:
        try:
            data_dict[metric] = parsed_2["quoteSummary"]["result"][0]["financialData"][
                metric
            ]["raw"]
        except:
            data_dict[metric] = np.nan

    for metric in check_list:

        try:
            query_url_3 = (
                "https://query2.finance.yahoo.com/v10/finance/quoteSummary/"
                + str(stock)
                + "?modules=summaryDetail"
            )
            with urllib.request.urlopen(query_url_3) as url:
                parsed_3 = json.loads(url.read().decode())
            data_dict[metric] = parsed_3["quoteSummary"]["result"][0]["summaryDetail"][
                metric
            ]["raw"]
        except:
            pass

    ## FF Quality
    FF_Quality_year_frame = calculate_FF_Quality(stock)
    # Calculate Growth rates and report recent and mean FF_Quality Factor
    data_dict["years_available"] = len(FF_Quality_year_frame)
    growth_measures_dict = {
        "RevGrowth": "totalRevenue",
        "GrossProfitGrowth": "grossProfit",
        "OpIncomeGrowth": "operatingIncome",
        "FF_Quality_Growth": "FF_Quality",
    }
    for measure in growth_measures_dict:
        try:
            data_dict[measure] = (
                FF_Quality_year_frame.sort_values(["year"], ascending=False)[
                    [growth_measures_dict[measure]]
                ]
                .pct_change()
                .mean()[0]
            )
        except Exception:
            data_dict[measure] = np.nan

    try:
        data_dict["FF_Quality_actual"] = FF_Quality_year_frame[
            FF_Quality_year_frame.year == 0
        ].FF_Quality[0]
        data_dict["FF_Quality_mean"] = FF_Quality_year_frame.FF_Quality.mean()
    except Exception:
        data_dict["FF_Quality_actual"] = np.nan
        data_dict["FF_Quality_mean"] = np.nan

    # FF_Conservative
    FF_Conservative_year_frame = calculate_FF_CA(stock)
    try:
        data_dict["FF_Assets_Growth_mean"] = (
            FF_Conservative_year_frame.sort_values(["year"], ascending=False)[
                ["totalAssets"]
            ]
            .pct_change()
            .mean()[0]
        )
        data_dict["FF_Assets_Growth_actual"] = (
            FF_Conservative_year_frame.sort_values(["year"], ascending=False)[
                ["totalAssets"]
            ]
            .pct_change()
            .iloc[1, 0]
        )
    except Exception:
        data_dict["FF_Assets_Growth_mean"] = np.nan
        data_dict["FF_Assets_Growth_actual"] = np.nan

    return pd.DataFrame.from_dict({stock: data_dict}, orient="index")


def calculate_FF_Quality(stock):
    """
    Function to calculate the Fama French Quality Factor.
    This factor is calculated using all accounting numbers from the end of the previous fiscal year.
    It is defined by the annual revenues minus the cost of goods sold, interest expenses, selling, general, and administrative expenses divided by the book equity.
    For more informations, refer to Fama and French (2015).

    Inputs:
        - stock(str): The ticker smybol used in get_data()
    Returns:
        - A pd.DataFrame containing information about the metrics building up the factor and information about the factor itself. Additional I report growth rates for all emtrics and the factor. This helps indentify outliers and steady trends.


    """

    Fama_French_Quality = [
        "totalRevenue",
        "costOfRevenue",
        "grossProfit",
        "sellingGeneralAdministrative",
        "interestExpense",
        "operatingIncome",
        "netIncomeFromContinuingOps",
    ]
    FF_Quality_dict = {}
    FF_Quality_year_frame = pd.DataFrame({})
    try:
        query_url_4 = (
            "https://query2.finance.yahoo.com/v10/finance/quoteSummary/"
            + str(stock)
            + "?modules=incomeStatementHistory"
        )
        with urllib.request.urlopen(query_url_4) as url:
            parsed_4 = json.loads(url.read().decode())

        query_url_5 = (
            "https://query2.finance.yahoo.com/v10/finance/quoteSummary/"
            + str(stock)
            + "?modules=balanceSheetHistory"
        )
        with urllib.request.urlopen(query_url_5) as url:
            parsed_5 = json.loads(url.read().decode())
    except Exception as e:
        print(e)
        print(stock)

    for year in range(5):
        try:
            for metric in Fama_French_Quality:
                FF_Quality_dict[metric] = parsed_4["quoteSummary"]["result"][0][
                    "incomeStatementHistory"
                ]["incomeStatementHistory"][year][metric]["raw"]
            FF_Quality_dict["totalStockholderEquity"] = parsed_5["quoteSummary"][
                "result"
            ][0]["balanceSheetHistory"]["balanceSheetStatements"][year][
                "totalStockholderEquity"
            ][
                "raw"
            ]
            FF_Quality_dict["year"] = year
            # Building FF-Quality Factor
            FF_Quality_dict["FF_Quality"] = (
                FF_Quality_dict["totalRevenue"]
                - (
                    FF_Quality_dict["costOfRevenue"]
                    + FF_Quality_dict["interestExpense"]
                    + FF_Quality_dict["sellingGeneralAdministrative"]
                )
            ) / FF_Quality_dict["totalStockholderEquity"]
            FF_Quality_frame = pd.DataFrame.from_dict(
                {stock: FF_Quality_dict}, orient="index"
            )
            FF_Quality_year_frame = FF_Quality_year_frame.append(FF_Quality_frame)
        except Exception:
            break
    return FF_Quality_year_frame


def calculate_FF_CA(stock):
    """
    Function to calculate the Fama French Conservative Asset Factor.
    The Conservative Asset Factor is defined as the ratio of total assets of a stock at the fiscal year end of t-1  and the total assets at fiscal year end of t-2.
    For more informations, refer to Fama and French (2015).

    Inputs:
        - stock(str): The ticker smybol used in get_data()
    Returns:
        - A pd.DataFrame containing information about the metrics building up the factor and information about the factor itself. Additional I report growth rates for all emtrics and the factor.



    """

    FF_Conservative_dict = {}
    FF_Conservative_year_frame = pd.DataFrame({})
    try:
        query_url_5 = (
            "https://query2.finance.yahoo.com/v10/finance/quoteSummary/"
            + str(stock)
            + "?modules=balanceSheetHistory"
        )
        with urllib.request.urlopen(query_url_5) as url:
            parsed_5 = json.loads(url.read().decode())
    except Exception as e:
        print(e)
        print(stock)

    # FF Inv
    for year in range(5):
        try:
            FF_Conservative_dict["totalAssets"] = parsed_5["quoteSummary"]["result"][0][
                "balanceSheetHistory"
            ]["balanceSheetStatements"][year]["totalAssets"]["raw"]
            FF_Conservative_dict["year"] = year
            FF_Conservative_frame = pd.DataFrame.from_dict(
                {stock: FF_Conservative_dict}, orient="index"
            )
            FF_Conservative_year_frame = FF_Conservative_year_frame.append(
                FF_Conservative_frame
            )
        except:
            break
    return FF_Conservative_year_frame


def calc_precentiles(final_frame):
    """
    Function to calculate percentiles of several selected metrics.

    Inputs:
        - final_frame(pd.DataFrame): pd.DataFrame with all the information and the metrics for which percentiles should be calculated.
    Returns:
        - The same pd.DataFrame, but now also with the calculated percentiles.

    """
    metrics = {
        "priceToBook": "PB_percentile",
        "enterpriseValue": "EV_percentile",
        "marketCap": "MC_percentile",
        "priceToSalesTrailing12Months": "PS_percentile",
        "enterpriseToRevenue": "EToRev_precentile",
        "enterpriseToEbitda": "EToEbitda_percentile",
        "FF_Assets_Growth_mean": "FFA_m_percentile",
        "FF_Assets_Growth_actual": "FF_Cons_actual_percentile",
    }
    for row, metric in itertools.product(final_frame.index, metrics):
        try:
            final_frame.loc[row, metrics[metric]] = (
                stats.percentileofscore(
                    final_frame[metric], final_frame.loc[row, metric]
                )
                / 100
            )
        except Exception:
            final_frame.loc[row, metrics[metric]] = np.nan

    # metrics where we have to invert the percentile
    inv_metrics = {
        "returnOnEquity": "ROE(inv)_percentile",
        "FF_Quality_Growth": "FFQ(inv)_g_percentile",
        "FF_Quality_actual": "FFQ(inv)_a_percentile",
        "FF_Quality_mean": "FFQ(inv)_m_percentile",
    }

    for row, metric in itertools.product(final_frame.index, inv_metrics):
        try:
            final_frame.loc[row, inv_metrics[metric]] = 1 - (
                stats.percentileofscore(
                    final_frame[metric], final_frame.loc[row, metric]
                )
                / 100
            )
        except Exception:
            final_frame.loc[row, inv_metrics[metric]] = np.nan

    return final_frame


def clean_stock_selection(uncleaned_stocks):
    """
    Function to perform some cleaning before using urllib.requests and finance.yahoo.com to obtain all the stockinfo.

    Inputs:
        - uncleaned_stocks(pd.DataFrame): pd.DataFrame containing the stocks (name, wkn, exchange, ticker, ISIN, ...)
    Returns:
        - pd.DataFrame cleaned s.t. every stock has an industry.

    """
    return uncleaned_stocks[uncleaned_stocks.industry != "not_found"]


def save_data(sample, path):
    sample.to_pickle(path)


today = datetime.today().strftime("%Y-%m-%d")


@pytask.mark.depends_on(SRC / "original_data" / "val2_euro600.pkl")
@pytask.mark.produces(SRC / "final" / f"proc_eurostoxx600_{today}.pkl")
def task_process_eu_stocks(depends_on, produces):
    """
    Pytask function to collect the metrics for all the atocks of the EuroStoxx600 index.

    Inputs:
        - depends_on(): A pickle file containing all the information that is needed to obtain the metrics.
    Returns:
        - produces(): A pickle file containing all the collected indormations and metrics.

    """

    stocklist = clean_stock_selection(pd.read_pickle(depends_on))
    frame = pd.DataFrame({})
    with ThreadPool() as p:
        frame = frame.append(p.map(get_data, stocklist.ticker[1:5]))
        p.close()
    final_frame = calc_precentiles(frame)
    save_data(final_frame, produces)


def fun_process_stocks(stockinfo_pkl, datalist):
    """
    Function that combines the whole process of obtaining the information. This function in itself calls clean_stock_selection(), get_data() and calc_percentiles().
    To increase the performance, this function uses ThreadPool from multiprocessing.pool. This allows multithreading.
    The number of threads is automatically determined by the default option of ThreadPool.

    Inputs:
        - stockinfo_pkl(pd.DataFrame): A pd.DataFrame that contains the information about stocks. Must contain ticker and industry such that the function works.
        - datalist(str): provides a namethat is incorporated into the naming of the produced file.

    Return:
        - None, but saves a file.

    """

    stocklist = clean_stock_selection(stockinfo_pkl)
    try:
        stocklist.drop("Unnamed: 0", axis=1, inplace=True)
    except Exception:
        pass
    frame = pd.DataFrame({})
    with ThreadPool() as p:
        frame = frame.append(p.map(get_data, stocklist.ticker))
        p.close()
    
    # Rescale some units to percentages
    multiply_metrics_list = [
        "profitMargins",
        "floatShares",
        "sharesOutstanding",
        "heldPercentInsiders",
        "dividendYield",
        "returnOnAssets",
        "returnOnEquity",
        "revenueGrowth",
        "grossMargins",
        "ebitdaMargins",
        "operatingMargins",
        "profitMargins",
        "RevGrowth",
        "GrossProfitGrowth",
        "OpIncomeGrowth",
        "FF_Assets_Growth_mean",
        "FF_Assets_Growth_actual",
    ]
    for mmetric in multiply_metrics_list:
        frame[mmetric] = frame[mmetric] *100



    final_frame = calc_precentiles(frame)
    save_data(
        final_frame, SRC / "final" / "processed_data" / f"proc_{today}_{datalist}"
    )


import warnings

warnings.filterwarnings("ignore")
if __name__ == "__main__":

    today = datetime.today().strftime("%Y-%m-%d")
    data_ls = [
        "val2_nikkei225.pkl",
        "val2_de.pkl",
        "val2_euro600.pkl",
        "val2_nyse.pkl",
        "val2_nasdaq.pkl",
        "val2_amex.pkl",
    ]
    for datalist in data_ls:
        stockinfo_pkl = pd.read_pickle(SRC / "original_data" / datalist)
        fun_process_stocks(stockinfo_pkl, datalist)
        time.sleep(1)
