"""
    Several functions that obtain the info about stocks of a specific exchange / index. 
    Currently this has to be done manually since it uses Selenium and BeautifoulSoup, which tend to be a bit unstable. 
    From time to time it can happen that the scraper runs into a problem and the user then has to fix it by hand (for isntance closing an advertisement window which is randomly triggered and is not detected by Selenium).

"""

import urllib.request, json, time, os, difflib, itertools
import pandas as pd
import numpy as np
from multiprocessing.dummy import Pool
import datetime
import time
import numpy as np
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import random
from pandas import ExcelWriter
from bs4 import BeautifulSoup
from scipy import stats  # The SciPy stats module
import datetime


def get_stock_data(url, index_exchange):
    """
    Function to fetch stock information such as name and wkn from a specified URL of the traderfox.de website with an specified index / exchange. The function relies on Selenium and BeautifulSoup.

    Inputs:
        - url (str): one of the available urls from traderfox.de.
        - index_exchange (str): name of the index / exchnage from which the stocks should be selected
          (e.g.: Nasdaq, Amex, NYSE, ...).

    Returns:
        - A pd.DataFrame containing the name, wkn, and index / exchange of stocks.
    """
    browser = webdriver.Firefox()
    time.sleep(2)
    browser.get(url)
    time.sleep(5)
    soup = BeautifulSoup(browser.page_source, "html")
    time.sleep(5)
    names = []
    Row = soup.find("table", attrs={"id": "insert-stocks"})
    for name in Row.find_all("td", attrs={"class": "name"}):
        try:
            names.append(name.text)
        except:
            names.append("")

    wkns = []
    Row = soup.find("table", attrs={"id": "insert-stocks"})
    for wkn in Row.find_all("td", attrs={"data-id": "wkn"}):
        try:
            wkns.append(wkn.text)
        except:
            wkns.append("")

    FRAME = pd.DataFrame.from_dict(
        {"name": names, "wkn": wkns, "index": index_exchange}
    )
    time.sleep(1)
    browser.quit()
    return FRAME


def get_ticker(initial_frame):
    """
    This function provides usefull information about a stock by its wkn.
    The function provides the stocks ticker, de_ticker, ISIN and the industry in which the comany is operating within.
    The function relies on Selenium and BeautifulSoup. For security reasons, I am using a VPN / Privacy Badger to avid getting blocked while scraping, which might caus issues when you try to run it.
    To run it, you only have to tailor the browser and the extensions used to your specific requirements.

    To get all the information, I am using finanznachrichten.de and finance.yahoo.com as sources.

    Inputs:
        - initial_frame(pd.DataFrame): A pd.DataFrame contating the wkn and name of the stocks

    Returns:
        - A pd.DataFrame with all the collected information.

    """

    url_ticker = "https://www.finanznachrichten.de/"
    url_yf_ticker = "https://finance.yahoo.com/quote/FB?p=FB"
    browser = webdriver.Firefox()
    extension_path = r"C:\Users\Jonathan\AppData\Roaming\Mozilla\Firefox\Profiles\wl4weym2.default-1633941918487\extensions\jid1-MnnxcxisBPnSXQ@jetpack.xpi"
    browser.install_addon(extension_path, temporary=True)
    time.sleep(2)
    browser.get("about:support")
    time.sleep(5)
    browser.get(url_ticker)
    time.sleep(20)
    # clear = WebDriverWait(browser, 5).until(EC.presence_of_element_located((By.XPATH, "/html/body/div/div[2]/div[3]/div[2]/button"))).click()
    time.sleep(1)
    ticker = []
    de_ticker = []
    industry = []
    ISIN = []
    for i, wkn in enumerate(initial_frame.wkn):
        print(len(de_ticker), len(industry), len(ISIN))
        # if wkn not valid
        if wkn == "-":
            de_ticker.append("not_found")
            industry.append("not_found")
            ISIN.append("not_found")
            continue
        try:
            clear = (
                WebDriverWait(browser, 25)
                .until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, "#fnk-suche-eingabe")
                    )
                )
                .clear()
            )
            time.sleep(3)
            search = WebDriverWait(browser, 25).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "#fnk-suche-eingabe"))
            )
            time.sleep(1)
            search.send_keys(str(wkn))
            time.sleep(4)
            browser.find_element_by_css_selector(
                "#suchhilfeListe > tbody:nth-child(2) > tr:nth-child(3) > td:nth-child(2)"
            ).click()
            time.sleep(random.randint(3, 5))
            de_ticker.append(
                str(
                    WebDriverWait(browser, 15)
                    .until(
                        EC.presence_of_element_located(
                            (By.CSS_SELECTOR, "#produkt-ticker")
                        )
                    )
                    .text.replace("Ticker-Symbol: ", "")
                    .lstrip()
                )
            )
            # time.sleep(2)
        except:
            de_ticker.append("not_found")
            industry.append("not_found")
            ISIN.append("not_found")
            continue
        try:
            industry.append(
                str(
                    WebDriverWait(browser, 10)
                    .until(
                        EC.presence_of_element_located(
                            (By.CSS_SELECTOR, ".a > a:nth-child(2)")
                        )
                    )
                    .text
                )
            )
            time.sleep(1)
        except:
            industry.append("not_found")
        try:
            ISIN.append(
                str(
                    WebDriverWait(browser, 10)
                    .until(
                        EC.presence_of_element_located(
                            (By.CSS_SELECTOR, "#produkt-isin")
                        )
                    )
                    .text.replace("ISIN: ", "")
                    .lstrip()
                )
            )
            time.sleep(1)
            # time.sleep(random.randint(2,4))
        except:
            ISIN.append("not_found")

        if i % 4 == 0:
            try:
                browser.refresh()
                time.sleep(4)
            except:
                pass

    # check if lengths are equal
    print(len(industry), len(ISIN), len(de_ticker))
    try:
        browser.get(url_yf_ticker)
        time.sleep(5)
    except:
        browser.get(url_yf_ticker)
        time.sleep(5)
    try:
        browser.find_element_by_css_selector("#scroll-down-btn").click()
        time.sleep(3)
    except:
        pass
    try:
        browser.find_element_by_css_selector("button.btn:nth-child(5)").click()
        time.sleep(4)
    except:
        pass
    for _ISIN in ISIN:
        if _ISIN == "not_found":
            ticker.append("not_found")
            continue
        time.sleep(2)
        # check again for popup and scroll
        try:
            browser.find_element_by_css_selector("#scroll-down-btn").click()
            time.sleep(3)
        except:
            pass
        try:
            browser.find_element_by_css_selector("button.btn:nth-child(5)").click()
            time.sleep(4)
        except:
            pass

        clear = (
            WebDriverWait(browser, 25)
            .until(EC.presence_of_element_located((By.CSS_SELECTOR, "#yfin-usr-qry")))
            .clear()
        )
        # time.sleep(1)
        try:
            search = WebDriverWait(browser, 25).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "#yfin-usr-qry"))
            )
            # time.sleep(1)
            search.send_keys(str(_ISIN))
            time.sleep(2)
            ticker.append(
                str(
                    WebDriverWait(browser, 25)
                    .until(
                        EC.presence_of_element_located(
                            (
                                By.CSS_SELECTOR,
                                "#result-quotes-0 > div.modules_quoteLeftCol__gkCSv.modules_Ell__77DLP.modules_IbBox__2pmLe > div.modules_quoteSymbol__hpPcM.modules_Ell__77DLP.modules_IbBox__2pmLe",
                            )
                        )
                    )
                    .text
                )
            )
        except:
            ticker.append("not_found")

    print(len(ticker))

    frame = pd.DataFrame.from_dict(
        {
            "name": initial_frame.name,
            "wkn": initial_frame.wkn,
            "index": "NASDAQ",
            "de_ticker": de_ticker,
            "ticker": ticker,
            "industry": industry,
            "ISIN": ISIN,
        }
    )
    time.sleep(1)
    browser.quit()
    return frame


def validate_ticker(path):

    """
    Function to update the stock information for the different exchanges / indicies
    The function closely follows get_ticker() and is also based on Selenium / BS4.
    This function is usefull to:
        - check if info is up to date.
        - after adding new stocks to the {exchange / index}Stocks.csv files.
        - to check that scraping was not corruped by bad internet connection or other issues.
        - to validate the scraping.

    Inputs:
        path (str): path of the file for which to perform the validation.

    Returns:
        None, but saves the validated run of the file.

    """
    url_ticker = "https://www.finanznachrichten.de/"
    url_yf_ticker = "https://finance.yahoo.com/quote/FB?p=FB"
    # browser =  webdriver.Firefox(executable_path='/home/jonathan/Schreibtisch/geckodriver')
    # extension_path = r"/home/jonathan/.mozilla/firefox/5xapxbqn.default-release/extensions/jid1-MnnxcxisBPnSXQ@jetpack.xpi"
    # browser.install_addon(extension_path, temporary=True)

    browser = webdriver.Firefox()
    extension_path = r"C:\Users\Jonathan\AppData\Roaming\Mozilla\Firefox\Profiles\wl4weym2.default-1633941918487\extensions\jid1-MnnxcxisBPnSXQ@jetpack.xpi"
    browser.install_addon(extension_path, temporary=True)
    time.sleep(2)
    # extension_path = r"C:\Users\Jonathan\AppData\Roaming\Mozilla\Firefox\Profiles\wl4weym2.default-1633941918487\extensions\firefox-webext@zenmate.com.xpi"
    # browser.install_addon(extension_path, temporary=True)
    browser.maximize_window()
    browser.get("about:support")
    time.sleep(5)
    browser.get(url_ticker)
    time.sleep(5)
    file = pd.read_csv(path, encoding="utf-8")
    for i, row in file.iterrows():
        if (row.ISIN) == "not_found" and (row.wkn != "-"):
            print(file.loc[i, "name"])
            try:
                time.sleep(1)
                clear = (
                    WebDriverWait(browser, 25)
                    .until(
                        EC.presence_of_element_located(
                            (By.CSS_SELECTOR, "#fnk-suche-eingabe")
                        )
                    )
                    .clear()
                )
                time.sleep(random.randint(3, 4))
                search = WebDriverWait(browser, 25).until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, "#fnk-suche-eingabe")
                    )
                )
                time.sleep(random.randint(2, 3))
                search.send_keys(str(row.wkn))
                time.sleep(3)
                browser.find_element_by_css_selector(
                    "#suchhilfeListe > tbody:nth-child(2) > tr:nth-child(3) > td:nth-child(2)"
                ).click()
                time.sleep(random.randint(2, 3))
                file.at[i, "de_ticker"] = (
                    WebDriverWait(browser, 5)
                    .until(
                        EC.presence_of_element_located(
                            (By.CSS_SELECTOR, "#produkt-ticker")
                        )
                    )
                    .text.replace("Ticker-Symbol: ", "")
                    .lstrip()
                )
                # time.sleep(2)
            except:
                pass
            try:
                if file.at[i, "industry"] == "not_found":
                    file.at[i, "industry"] = (
                        WebDriverWait(browser, 5)
                        .until(
                            EC.presence_of_element_located(
                                (By.CSS_SELECTOR, ".a > a:nth-child(2)")
                            )
                        )
                        .text
                    )
                    time.sleep(3)
            except:
                pass
            try:
                if file.at[i, "ISIN"] == "not_found":
                    file.at[i, "ISIN"] = (
                        WebDriverWait(browser, 5)
                        .until(
                            EC.presence_of_element_located(
                                (By.CSS_SELECTOR, "#produkt-isin")
                            )
                        )
                        .text.replace("ISIN: ", "")
                        .lstrip()
                    )
                    time.sleep(random.randint(2, 3))
            except:
                pass

    time.sleep(3)
    browser.get(url_yf_ticker)
    time.sleep(3)
    try:
        browser.find_element_by_css_selector("#scroll-down-btn").click()
        time.sleep(3)
    except:
        pass
    try:
        browser.find_element_by_css_selector("button.btn:nth-child(5)").click()
        time.sleep(4)
    except:
        pass
    for i, row in file.iterrows():
        if row.ISIN == "not_found":
            continue
        if file.at[i, "ticker"] == "not_found":
            time.sleep(random.randint(1, 2))
            try:
                browser.find_element_by_css_selector("#scroll-down-btn").click()
                time.sleep(3)
            except:
                pass
            try:
                browser.find_element_by_css_selector("button.btn:nth-child(5)").click()
                time.sleep(4)
            except:
                pass

            clear = (
                WebDriverWait(browser, 25)
                .until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "#yfin-usr-qry"))
                )
                .clear()
            )
            time.sleep(random.randint(3, 5))
            try:
                search = WebDriverWait(browser, 25).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "#yfin-usr-qry"))
                )
                time.sleep(1)
                search.send_keys(str(row.ISIN))
                time.sleep(5)
                file.at[i, "ticker"] = (
                    WebDriverWait(browser, 25)
                    .until(
                        EC.presence_of_element_located(
                            (
                                By.CSS_SELECTOR,
                                "#result-quotes-0 > div.modules_quoteLeftCol__gkCSv.modules_Ell__77DLP.modules_IbBox__2pmLe > div.modules_quoteSymbol__hpPcM.modules_Ell__77DLP.modules_IbBox__2pmLe",
                            )
                        )
                    )
                    .text
                )
            except:
                pass
    # exchange = file.index[0]
    file.to_csv("val_" + path)

    browser.quit()
