import ujson as json
import itertools
import urllib.request, json, time
from datetime import datetime
import time
import numpy as np
import pandas as pd
from scipy import stats  # The SciPy stats module
from multiprocessing.pool import ThreadPool
import warnings


warnings.filterwarnings("ignore")


def get_data(stockticker,pkldata):
    """
    Function to obtain a large amounts of mertics from finance.yahoo.com for a specific ticker. This is done by using urllib.requests and exploiting the react frontend of finance.yahoo.com.

    Inputs:
        - stockticker(str): The homeexchange ticker of a specified stock, e.g.: BC8.F for the german Bechtle AG.
    Returns:
        - A pd.DataFrame with metrics. For a list of the metrics that a re currently collected ahve a look at the implementation of the function.


    """
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

    growth_measures_dict = {
        "RevGrowth": "totalRevenue",
        "GrossProfitGrowth": "grossProfit",
        "OpIncomeGrowth": "operatingIncome",
        "FF_Quality_Growth": "FF_Quality",
    }

    check_list = [
        "forwardPE",
        "trailingPE",
        "marketCap",
        "priceToSalesTrailing12Months",
        "dividendYield",
    ]
    
    components = [
    '?modules=defaultKeyStatistics',
    '?modules=financialData',
    '?modules=summaryDetail'
    ]

    links = ["https://query2.finance.yahoo.com/v10/finance/quoteSummary/"+ str(stockticker) + i for i in components]


    data_dict = {"Ticker": stockticker, "date": datetime.today().strftime("%Y-%m-%d")}
    try:
        #the code below is to deal with ticker 2871.T
        target = pkldata[pkldata.ticker==stockticker]
        target = target.replace('not_found', np.nan)
        target = target.dropna()

        data_dict["Name"] = target.loc[:,"name"].item()
        data_dict["Industry"] = target.loc[:,"industry"].item()
        data_dict["de_ticker"] = target.loc[:,"de_ticker"].item()
    except Exception as e:
        data_dict["Name"] = np.nan
        data_dict["Industry"] = np.nan
        data_dict["de_ticker"] = np.nan

    try: 
        with urllib.request.urlopen(links[0]) as url:
            parsed_1 = json.loads(url.read().decode())
    except Exception as e:
        pass

    for metric in metrics_list:
        try:
            data_dict[metric] = parsed_1["quoteSummary"]["result"][0][
                "defaultKeyStatistics"
            ][metric]["raw"]
        except Exception:
            data_dict[metric] = np.nan

    try:

        with urllib.request.urlopen(links[1]) as url:
            parsed_2 = json.loads(url.read().decode())
    except Exception as e:
        pass
        #print(e)
        #print(stockticker)

    for metric in financial_list:
        try:
            data_dict[metric] = parsed_2["quoteSummary"]["result"][0]["financialData"][
                metric
            ]["raw"]
        except Exception as e:
            data_dict[metric] = np.nan

    try:
            with urllib.request.urlopen(links[2]) as url:
                parsed_3 = json.loads(url.read().decode())
    except Exception as e:
        pass


    for metric in check_list:
        
        try:
            data_dict[metric] = parsed_3["quoteSummary"]["result"][0]["summaryDetail"][
                metric
            ]["raw"]
        except Exception as e:
            pass

    FF_Quality_year_frame, parsed_5 = calculate_FF_Quality(stockticker)
    # Calculate Growth rates and report recent and mean FF_Quality Factor
    data_dict["years_available"] = len(FF_Quality_year_frame)
    for measure in growth_measures_dict:
        try:
            data_dict[measure] = (
                FF_Quality_year_frame.sort_values(["year"], ascending=False)[
                    [growth_measures_dict[measure]]
                ]
                .pct_change()
                .mean()[0]
            )
        except Exception as e:
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
    FF_Conservative_year_frame = calculate_FF_CA(stockticker, parsed_5)

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
   
    return pd.DataFrame.from_dict({stockticker: data_dict}, orient="index")

def calculate_FF_Quality(stock):
    """
    @updated
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
        #print(e)
        #print(stock)
        parsed_5 = "not avaliable"


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
            FF_Quality_frame = pd.DataFrame.from_dict(
                {stock: FF_Quality_dict}, orient="index"
            )
            FF_Quality_year_frame = pd.concat([FF_Quality_year_frame, FF_Quality_frame])
        except Exception:
            break

    # pandas is actually super fast from using vectorisation
    # Building FF-Quality Factor
    try:
        FF_Quality_year_frame["FF_Quality"] = (
            FF_Quality_year_frame["totalRevenue"]
            - (
                FF_Quality_year_frame["costOfRevenue"]
                + FF_Quality_year_frame["interestExpense"]
                + FF_Quality_year_frame["sellingGeneralAdministrative"]
            )
        ) / FF_Quality_year_frame["totalStockholderEquity"]
    except Exception:
        # return an empty dataframe in case nothing is presented
        column_name = ["totalRevenue",
        "costOfRevenue",
        "grossProfit",
        "sellingGeneralAdministrative",
        "interestExpense",
        "operatingIncome",
        "netIncomeFromContinuingOps",
        "totalStockholderEquity",
        "year",
        "FF_Quality" 
        ]
        FF_Quality_frame = pd.DataFrame(columns=column_name)

    return FF_Quality_year_frame, parsed_5

def calculate_FF_CA(stock, parsed_5):
    """
    Function to calculate the Fama French Conservative Asset Factor.
    The Conservative Asset Factor is defined as the ratio of total assets of a stock at the fiscal year end of t-1  and the total assets at fiscal year end of t-2.
    For more informations, refer to Fama and French (2015).

    Inputs:
        - stock(str): The ticker smybol used in get_data()
    Returns:
        - A pd.DataFrame containing information about the metrics building up the factor and information about the factor itself. Additional I report growth rates for all emtrics and the factor.


    @ waste time because doing repetitive stuff
    """
    FF_Conservative_dict = {}
    FF_Conservative_year_frame = pd.DataFrame({})
    if parsed_5 == "not avaliable":
        FF_Conservative_year_frame = FF_Conservative_year_frame

    
    else:
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
                FF_Conservative_year_frame = pd.concat([FF_Conservative_year_frame, FF_Conservative_frame])
            except:
                break
    return FF_Conservative_year_frame

def clean_stock_selection(uncleaned_stocks):
    """
    Function to perform some cleaning before using urllib.requests and finance.yahoo.com to obtain all the stockinfo.

    Inputs:
        - uncleaned_stocks(pd.DataFrame): pd.DataFrame containing the stocks (name, wkn, exchange, ticker, ISIN, ...)
    Returns:
        - pd.DataFrame cleaned s.t. every stock has an industry.

    """
    return uncleaned_stocks[uncleaned_stocks.industry != "not_found"]

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

    return round(final_frame, 2)

def fun_process_stocks_new(pklinput, datalist):
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
    stockinfo_pkl = pd.read_csv(f"screener/original_data/csv_files/{str(datalist)}")
    stocklist = clean_stock_selection(pklinput)
    try:
        pklinput.drop("Unnamed: 0", axis=1, inplace=True)
    except Exception:
        pass
    frame = pd.DataFrame({})

    input_ls = [pklinput]*len(stocklist.ticker.to_list())
    input_ls = [(i,j)for i, j in zip(stocklist.ticker.to_list(),input_ls)] 
    #debug purposes
    #f = open("bug.txt", "w")
    #for t in input_ls:
    #    f.write(' '.join(str(s) for s in t) + '\n')
    #f.close()
    #
    with ThreadPool() as p:
    # the output for some reasons is list of lists
        output = p.starmap(get_data, input_ls)
        p.close()

    # make list of lists into dataframe
    count = 0
    for i in range(len(output)):
        if count == 0:
            try:
                frame = pd.DataFrame(output[i])
                count += 1
            except:
                frame = pd.DataFrame({})
                count += 1
        else:
            frame = pd.concat([frame ,pd.DataFrame(output[i])])
    
    # Rescale some units to percentages
    multiply_metrics_list = [
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
        try:
           frame[mmetric] = frame[mmetric] *100
        except:
            pass

    frame.to_pickle(f"screener/screened_data/proc_{datalist}.pkl")
    return
