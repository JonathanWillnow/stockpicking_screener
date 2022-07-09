import pandas as pd
import numpy as np
from multiprocessing.dummy import Pool
from datetime import datetime
import numpy as np
import pandas as pd
from scipy import stats  # The SciPy stats module
from pandas_datareader.famafrench import get_available_datasets
import pandas_datareader.data as web



#rename industries to english
industry_dict = {'Finanzdienstleistungen':'Financial Services', 'Logistik/Transport':"Logistics/Transportation", 'Versorger':'Utilities',
       'Nahrungsmittel/Agrar':'Food/Agriculture', 'Industrie/Mischkonzerne':"Industry", 'Elektrotechnologie':"Electrical Technology", 'Bau/Infrastruktur':'Construction/Infrastructure', 
       'Hotels/Tourismus':'Hotels/Tourism',
       'Dienstleistungen':'Services', 'Freizeitprodukte':'Leisure Products', 'Immobilien':'Real Estate',
       'Chemie': 'Chemicals', 'Luftfahrt/Rüstung':'Aerospace/Armaments', 'Öl/Gas':'Oil/Gas', 'Gesundheitswesen': 'Healthcare',
       'Pharma':'Pharmaceuticals',  'Handel/E-Commerce':'Retail/E-commerce',  'IT-Dienstleistungen':'IT Services',
       'Sonstige Technologie': 'Other Technology', 'Halbleiter':'Semiconductors', 'Maschinenbau':'Mechanical Engineering',  'Rohstoffe':'Raw Materials',
       'Getränke/Tabak': 'Beverages/Tobacco', 'Eisen/Stahl':'Iron/Steel',  'Biotechnologie':'Biotechnology', 'Software':'Software',
       'Fahrzeuge': 'Vehicles', 'Kosmetik': 'Cosmetics', 'Holz/Papier': 'Wood/Paper', 'Telekom':'Telecom',
       'Bekleidung/Textil': 'Apparel/Textiles', 'Konsumgüter':'Consumer Goods', 'Kunststoffe/Verpackungen':'Plastics/Packaging',
       'Unterhaltung':'Entertainment', 'Erneuerbare Energien':'Renewable Energies',  'Medien':'Media', 'Hardware':'Hardware'}









def get_european_weights_ken_french():
    """
    Function to obtain the historic European 5 Fama French Factors from the official webiste.
    These will then be used for the weighting od the factors to build the final score.
    Inputs:
        - None

    Returns:
        - pd.DataFrame with the historic average monthly performance of the factors over the market return.

    """

    START_DATE = "2000-05-01"
    END_DATE = "2022-02-22"

    ff_dict = web.DataReader(
        "Europe_5_Factors", "famafrench", start=START_DATE, end=END_DATE
    )  # default is monthly  #ff_dict.keys()  #print(ff_dict["DESCR"])
    factor_df = ff_dict[0]  # monthly factors. 1 for annual
    factor_df.rename(
        columns={
            "Mkt-RF": "mkt_rf",
            "SMB": "smb",
            "HML": "hml",
            "RMW": "rmw",
            "CMA": "cma",
            "RF": "rf",
        },
        inplace=True,
    )
    factor_df["mkt"] = factor_df.mkt_rf + factor_df.rf
    factor_df = factor_df.apply(pd.to_numeric, errors="coerce").div(100)
    # meandf = factor_df[["smb", "hml", "rmw", "cma"]].mean()*100
    adjust_weights = factor_df[["smb", "hml", "rmw", "cma"]].mean() * 100
    return adjust_weights.values


def calculate_precentiles_score(rv_dataframe, metric_dict):
    """
    Function to calculate the percentiles of the calculated and obtained metrics. This gives the user and intuition about an particular stock compared to other stocks.

    Inputs:
        - rv_dataframe(pd.DataFrame): A pd.DataFrame with the stockinformation.
        - metric_dict(dict): A python dicionary with the pairs ondicating for which metrics the percentiles should be calculated.

    Returns:
        - A pd.DataFrame with the calculated percentiles and the initial info.


    """

    FF_metrics = metric_dict

    ff_weights = get_european_weights_ken_french()
    print(ff_weights)
    for row in rv_dataframe.index:
        value_percentiles = []
        for i, metric in enumerate(FF_metrics.keys()):
            value_percentiles.append(
                rv_dataframe.loc[row, FF_metrics[metric]] * ff_weights[i]
            )
        rv_dataframe.loc[row, "RV Score"] = sum(value_percentiles) / sum(ff_weights)

    return rv_dataframe




#rename industries to english
industry_dict = {'Finanzdienstleistungen':'Financial Services', 'Logistik/Transport':"Logistics/Transportation", 'Versorger':'Utilities',
       'Nahrungsmittel/Agrar':'Food/Agriculture', 'Industrie/Mischkonzerne':"Industry", 'Elektrotechnologie':"Electrical Technology", 'Bau/Infrastruktur':'Construction/Infrastructure', 
       'Hotels/Tourismus':'Hotels/Tourism', 'Hardware':'Hardware',
       'Dienstleistungen':'Services', 'Freizeitprodukte':'Leisure Products', 'Immobilien':'Real Estate',
       'Chemie': 'Chemicals', 'Luftfahrt/Rüstung':'Aerospace/Armaments', 'Öl/Gas':'Oil/Gas', 'Gesundheitswesen': 'Healthcare',
       'Pharma':'Pharmaceuticals',  'Handel/E-Commerce':'Retail/E-commerce',  'IT-Dienstleistungen':'IT Services',
       'Sonstige Technologie': 'Other Technology', 'Halbleiter':'Semiconductors', 'Maschinenbau':'Mechanical Engineering',  'Rohstoffe':'Raw Materials',
       'Getränke/Tabak': 'Beverages/Tobacco', 'Eisen/Stahl':'Iron/Steel',  'Biotechnologie':'Biotechnology', 'Software':'Software',
       'Fahrzeuge': 'Vehicles', 'Kosmetik': 'Cosmetics', 'Holz/Papier': 'Wood/Paper', 'Telekom':'Telecom',
       'Bekleidung/Textil': 'Apparel/Textiles', 'Konsumgüter':'Consumer Goods', 'Kunststoffe/Verpackungen':'Plastics/Packaging',
       'Unterhaltung':'Entertainment', 'Erneuerbare Energien':'Renewable Energies',  'Medien':'Media', 'Hardware':'Hardware'}



def reorder_naming(frame):
    """
    Function reorder and rename the dataset for the Dash-App before loading it into a Dashtable.

    Inputs:
        frame(pd.DataFrame): Dataset of stocks.

    Returns:
        A pd.DataFrame that has a different ordering / naming, according to the function.
    """
    frame_i =frame.replace(industry_dict)
    frame_dd = frame_i[
        [   
            "Name",
            "Ticker",
            "currentPrice",
            "Industry",
            "Country",
            "priceToBook",
            "trailingPE",
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
            "profitMargins",
            "trailingEps",
            "forwardEps",
            "pegRatio",
            "enterpriseToEbitda",
            "dividendYield",
            "fiveYearAvgDividendYield",
            "payoutRatio",
            "quickRatio",
            "currentRatio",
            "debtToEquity",
            "grossMargins",
            "ebitdaMargins",
            "operatingMargins",
            "RevGrowth",
            "GrossProfitGrowth",
            "OpIncomeGrowth",
            "enterpriseValue",
            "marketCap",
            "SharesOutstandingPercentage",
            "heldPercentInsiders",
        ]
    ].dropna(
        subset=[
            # "MC_percentile",
            # "PB_percentile",
            # "FF_Cons_actual_percentile",
            # "FFQ(inv)_a_percentile",
            #"currentPrice",
            "Ticker",
            "returnOnEquity"
        ]
    )

    frame_d = frame_dd.dropna(axis=1, how="all")

    frame_d.rename(
        columns={
            "priceToBook": "P/B",
            "FF_Assets_Growth_mean": "FFA",
            "FF_Quality_actual": "FFQ",
            "FF_Quality_Growth": "\u0394FFQ",
            "returnOnEquity": "ROE",
            "returnOnAssets": "ROA",
            "priceToSalesTrailing12Months": "P/S TTM",
            "enterpriseToRevenue": "EV/RV",
            "PB_percentile": "PB per",
            "MC_percentile": "MC per",
            "FF_Cons_actual_percentile": "act. FFA per",
            "FFA_m_percentile": "\u2300FFA per",
            "FFQ(inv)_a_percentile": "FFQ(i) per",
            "FFQ(inv)_g_percentile": "\u0394FFQ(i) per",
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
            "dividendYield": "Div\u0025",
            "fiveYearAvgDividendYield":"5y\u2300  Div\u0025",
            "payoutRatio":"Payout\u0025",
            "quickRatio": "QRatio",
            "currentRatio": "CRatio",
            "debtToEquity": "D/Equity",
            "grossMargins": "GMargin \u0025",
            "operatingMargins": "OMargin \u0025",
            "RevGrowth": "\u0394Rev",
            "GrossProfitGrowth": "\u0394GrossP",
            "OpIncomeGrowth": "\u0394OpInc",
            "enterpriseValue": "EV",
            "marketCap": "MC",
            "SharesOutstandingPercentage":"Shares Out \u0025",
            "heldPercentInsiders": "Insider \u0025",
            "currentPrice":"Price",
        },
        inplace=True,
    )
    return round(frame_d.drop(frame_d[(frame_d["Price"] < 1.0) | (frame_d["P/B"]< 0.05)].index),2)
