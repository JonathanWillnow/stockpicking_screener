"""
This code is cleaning up the collected data and builds the final dataset which is then used for the stockscreening on https://stockpickingapp.herokuapp.com.
I tried to limit the cleaning in this step as much as possible since there is more filtering possible on https://stockpickingapp.herokuapp.com.

"""

import numpy as np
import pytask
import time

from src.config import BLD
from src.config import SRC
from src.final.product import *
from datetime import datetime


def save_data(sample, path):

    """
    Function to save the data / sample as pickle in a specified location.

    Inputs:
        sample(pd.DataFrame): DataFrame with the data that has to be saved as pickle.
        path (str): path of the file for which to perform the validation.

    """

    sample.to_pickle(path)


today = datetime.today().strftime("%Y-%m-%d")


@pytask.mark.depends_on(SRC / "final" / f"proc_eurostoxx600_{today}.pkl")
@pytask.mark.produces(SRC / "product_data" / f"f_proc_eurostoxx600_{today}.pkl")
def task_create_product(depends_on, produces):
    """
    Pytask function to create the european product. The output can be found in src.product_data.

    """

    rv_dataframe = pd.read_pickle(depends_on)
    try:
        rv_dataframe.drop("Unnamed: 0", axis=1, inplace=True)
    except:
        pass
    metric_dict = {
        "marketCap": "MC_percentile",
        "priceToBook": "PB_percentile",
        "FF_Quality_mean": "FFQ(inv)_m_percentile",
        "FF_Assets_Growth_mean": "FFA_m_percentile",
    }

    rv_dataframe_per = calculate_precentiles(rv_dataframe, metric_dict)
    # rv_dataframe_revGPconstraint = rv_dataframe_per[
    #     (rv_dataframe_per.RevGrowth >= 0.0)
    #     & (rv_dataframe_per.GrossProfitGrowth >= 0.075)
    #     & (rv_dataframe_per.returnOnEquity >= 0)
    #     & (rv_dataframe_per.OpIncomeGrowth >= 0.05)
    # ]
    # len(rv_dataframe_revGPconstraint)

    sorted_rc_frame = rv_dataframe_per.sort_values(by="RV Score").copy()
    sorted_rc_frame = sorted_rc_frame
    sorted_rc_frame.reset_index(drop=True, inplace=True)
    sorted_rc_frame[
        [
            "ticker",
            "industry",
            "RV Score",
            "priceToBook",
            "heldPercentInsiders",
            "returnOnAssets",
            "returnOnEquity",
            "RevGrowth",
            "GrossProfitGrowth",
            "OpIncomeGrowth",
            "PB_percentile",
            "MC_percentile",
            "FFA_m_percentile",
            "FFQ(inv)_a_percentile",
        ]
    ]

    save_data(sorted_rc_frame, produces)


if __name__ == "__main__":

    today = datetime.today().strftime("%Y-%m-%d")
    data_ls = [
        f"proc_{today}_val2_euro600.pkl",
        f"proc_{today}_val2_de.pkl",
        f"proc_{today}_val2_nyse.pkl",
        f"proc_{today}_val2_nasdaq.pkl",
        f"proc_{today}_val2_nikkei225.pkl",
        f"proc_{today}_val2_amex.pkl",
    ]
    for datalist in data_ls:

        rv_dataframe = pd.read_pickle(SRC / "final" / "processed_data" / datalist)
        try:
            rv_dataframe.drop("Unnamed: 0", axis=1, inplace=True)
        except:
            pass

        metric_dict = {
            "marketCap": "MC_percentile",
            "priceToBook": "PB_percentile",
            "FF_Quality_mean": "FFQ(inv)_m_percentile",
            #'FF_Quality_Growth' : 'FFQ(inv)_g_percentile',
            "FF_Assets_Growth_mean": "FFA_m_percentile",
        }
        rv_dataframe_per = calculate_precentiles(rv_dataframe, metric_dict)

        sorted_rc_frame = rv_dataframe_per.sort_values(by="RV Score").copy()
        sorted_rc_frame.reset_index(drop=True, inplace=True)

        sorted_rc_frame.to_pickle(SRC / "final" / "processed_data" / f"f_{datalist}")
        time.sleep(1)
