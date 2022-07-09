import time
from datetime import datetime
import time
import pandas as pd
import os

#warnings.filterwarnings("ignore")

from screener.manage_screened_data import *
from screener.yahoo_screener import *

data_ls = [
   # "amex.csv",
    "nasdaq.csv",
    "nyse.csv",
]

proc_ls = [
    #"proc_nikkei225.csv.pkl",
   # "proc_de.csv.pkl",
    #"proc_eu.csv.pkl",
    "proc_american.csv.pkl",
    #"proc_all.csv.pkl",
]
test = True
if test:
    for datalist in data_ls:

        stockinfo_pkl = pd.read_csv(f"screener/original_data/csv_files/{str(datalist)}")
        fun_process_stocks_new(stockinfo_pkl[1575:1600], datalist)
        time.sleep(1)
else:
      for datalist in data_ls:

        stockinfo_pkl = pd.read_csv(f"screener/original_data/csv_files/{str(datalist)}")
        fun_process_stocks_new(stockinfo_pkl, datalist)
        time.sleep(5)


data_input_jp = pd.read_pickle("screener/screened_data/proc_nikkei225.csv.pkl")
data_input_ger = pd.read_pickle("screener/screened_data/proc_de.csv.pkl")
data_input_eu_euro_notated =  pd.read_pickle("screener/screened_data/proc_eu_euro_notated_ex_germany.csv.pkl")
data_input_eu_not_euro_notated =  pd.read_pickle("screener/screened_data/proc_eu_not_euro_notated.csv.pkl")

data_eu = pd.concat([data_input_eu_euro_notated, data_input_eu_not_euro_notated])

data_input_america_2 = pd.read_pickle( "screener/screened_data/proc_nyse.csv.pkl")
data_input_america_3 = pd.read_pickle("screener/screened_data/proc_nasdaq.csv.pkl")


data_all = pd.concat([data_input_jp, data_input_ger, data_eu, data_input_america_2, data_input_america_3])
data_all.drop_duplicates(subset=["Ticker"], inplace=True)
data_all.to_pickle("screener/screened_data/proc_all.csv.pkl")

data_american = pd.concat([ data_input_america_2, data_input_america_3])
data_american.drop_duplicates(subset=["Ticker"], inplace=True)
data_american.to_pickle("screener/screened_data/proc_american.csv.pkl")


for proc_data in proc_ls:
    if proc_data == "proc_all.csv.pkl":
        frame = pd.read_pickle(f"screener/screened_data/{str(proc_data)}")
        perc_frame = calc_precentiles_all(frame)
        reordered_frame = reorder_naming(perc_frame)
        if test:
            print(reordered_frame)

        reordered_frame.to_pickle(f"flaskblog/processed_data/final_{proc_data}.pkl")
        continue

    frame = pd.read_pickle(f"screener/screened_data/{str(proc_data)}")
    perc_frame = calc_precentiles(frame)
    reordered_frame = reorder_naming(perc_frame)
    if test:
        print(reordered_frame)

    reordered_frame.to_pickle(f"flaskblog/processed_data/final_{proc_data}.pkl")
print(f"{datetime.now()}: American stocks successfully screened")
time.sleep(1)

# os.system('sudo supervisorctl restart flaskapp')
# time.sleep(5)