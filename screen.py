import itertools
import urllib.request, json, time
from datetime import datetime
import time
import numpy as np
import pandas as pd
from scipy import stats  # The SciPy stats module
from multiprocessing.pool import ThreadPool
import warnings

# TODO: play arround and see whether asyncio provides more performance
import asyncio


warnings.filterwarnings("ignore")

from screener.manage_screened_data import *
from screener.yahoo_screener import *

data_ls = [
    "nikkei225.csv",
    "de.csv",
    "euro600.csv",
    "amex.csv",
    "nasdaq.csv",
    "nyse.csv",
    #"val2_de.pkl"
]

proc_ls = [
    "proc_nikkei225.csv.pkl",
    "proc_de.csv.pkl",
    "proc_euro600.csv.pkl",
    "proc_american.csv.pkl",
    "proc_all.csv.pkl",
]
test = True
if test:
    for datalist in data_ls:
        print(f"{datalist} is processed")
        stockinfo_pkl = pd.read_csv(f"screener/original_data/csv_files/{str(datalist)}")
        fun_process_stocks_new(stockinfo_pkl[:4], datalist)
        time.sleep(1)
else:
      for datalist in data_ls:

        stockinfo_pkl = pd.read_csv(f"screener/original_data/csv_files/{str(datalist)}")
        fun_process_stocks_new(stockinfo_pkl, datalist)
        print(f"{datalist} successfully screened")
        time.sleep(1)


data_input_jp = pd.read_pickle("screener/screened_data/proc_nikkei225.csv.pkl")
data_input_ger = pd.read_pickle("screener/screened_data/proc_de.csv.pkl")
data_input_eu =  pd.read_pickle("screener/screened_data/proc_euro600.csv.pkl")
data_input_america_1 = pd.read_pickle("screener/screened_data/proc_amex.csv.pkl")
data_input_america_2 = pd.read_pickle( "screener/screened_data/proc_nyse.csv.pkl")
data_input_america_3 = pd.read_pickle("screener/screened_data/proc_nasdaq.csv.pkl")

data_all = pd.concat([data_input_jp, data_input_ger, data_input_eu, data_input_america_1, data_input_america_2, data_input_america_3])
data_all.to_pickle("screener/screened_data/proc_all.csv.pkl")

data_american = pd.concat([data_input_america_1, data_input_america_2, data_input_america_3])
data_american.to_pickle("screener/screened_data/proc_american.csv.pkl")


for proc_data in proc_ls:

        frame = pd.read_pickle(f"screener/screened_data/{str(proc_data)}")
        perc_frame = calc_precentiles(frame)
        reordered_frame = reorder_naming(perc_frame)
        if test:
            print(reordered_frame)

        reordered_frame.to_pickle(f"flaskblog/processed_data/final_{proc_data}.pkl")
time.sleep(1)
