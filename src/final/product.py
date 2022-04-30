import pandas as pd
import numpy as np
from multiprocessing.dummy import Pool
from datetime import datetime
import numpy as np
import pandas as pd
from pandas import ExcelWriter
from bs4 import BeautifulSoup
from scipy import stats  # The SciPy stats module
from pandas_datareader.famafrench import get_available_datasets
import pandas_datareader.data as web


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


def calculate_precentiles(rv_dataframe, metric_dict):
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
