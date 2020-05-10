#!/usr/bin/env python
# coding: utf-8

from alpha_vantage.timeseries import TimeSeries
import numpy as np
import pandas as pd
import os
import time
import mysql.connector
import sqlalchemy as sqa


# Add an environment variable ALPHA_VANTAGE_KEY on your machine and set your key obtained from Alpha_vantage
key = os.environ['ALPHA_VANTAGE_KEY']

# Chose your output format, or default to JSON (python dict)
ts = TimeSeries(key, output_format='pandas')

user = os.environ['mysql_user']
pwd = os.environ['mysql_user_password']
sqlEngine = sqa.create_engine('mysql+mysqlconnector://' + user + ':' + pwd + '@127.0.0.1/TradingDB', pool_recycle=3600)

def load_tickers():
    tickers = []
    import csv
    with open('./tickers.csv') as csvfile:
        readCSV = csv.reader(csvfile, delimiter=',')
        for row in readCSV:
            tickers.append(row[0])
    return tickers

def symbol_to_path(symbol, base_dir="data"):
    """Return CSV file path given ticker symbol."""
    return os.path.join(base_dir, "{}.csv".format(str(symbol)))

def fetch_data(ticker, freq = 'D', outsize='compact'):
    '''
    Fetch data from Alpha Vantage
    '''
    try:
        if freq == 'D':
            t1, t2 = ts.get_daily(symbol=ticker, outputsize=outsize)
        elif freq == 'W':
            t1, t2 = ts.get_weekly(symbol=ticker, outputsize=outsize)
        else:
            t1, t2 = ts.get_monthly(symbol=ticker, outputsize=outsize)        
    
        return True, t1, t2
    except Exception as ex:   
        print('Failed to fetch data for ticker:', ticker, ' >> ', ex)
        return False, _, _ 

def save_ticker_data(df, ticker, timeType = '_D'):
    dbCon = sqlEngine.connect()
    try:
        tbl_name = ticker + timeType
        frame = df.to_sql(con=dbCon, schema='TradingDB', index=True, index_label='date', name=tbl_name, if_exists='append')

    except Exception as ex:   
        print(ex)

    finally:
        dbCon.close()    
    
def fetch_new_ticker_data(df_ticker):
    # Fetch data. Pause after every 5 tickers since the site allows limited stocks at a time
    count = 0
    for x in range(df_ticker.shape[0]):
        ticker = df_ticker.iloc[x, 0]
        count += 1 
        print("Fetching data for ticker", ticker)
        result, ticker_data, ticker_meta_data = fetch_data(ticker, outsize='full')
        if result:
            ticker_data.columns = ["open", "high", "low", "close", "volume"]
            save_ticker_data(ticker_data, ticker)
        if count % 5 == 0:
            time.sleep(70)    

def fetch_existing_ticker_data(df_ticker):
    # Fetch data. Pause after every 5 tickers since the site allows limited stocks at a time
    count = 0
    for x in range(df_ticker.shape[0]):
        ticker = df_ticker.iloc[x, 0]
        count += 1 
        print("Fetching data for ticker", ticker)
        result, ticker_data, ticker_meta_data = fetch_data(ticker, outsize='compact')
        if result:
            ticker_data.columns = ["open", "high", "low", "close", "volume"]
            ticker_data = ticker_data.loc[ticker_data.index > df_ticker.iloc[x,1]]
            if len(ticker_data) > 0:
                save_ticker_data(ticker_data, ticker)
        if count % 5 == 0:
            time.sleep(70) 
            
def get_latest_ticker_date(df, timeType = '_D'):
    dbCon = sqlEngine.connect()

    try:

        for x in range(df.shape[0]):
            tbl_name = df.iloc[x, 0] + timeType
            query = "select count(*) as cnt from information_schema.tables where table_name = '" + tbl_name + "'"
            results = dbCon.execute(query)
            cnt = results.fetchall()[0][0]
            if cnt != 0:
                query = "select max(date) as date from " + tbl_name
                results = dbCon.execute(query)
                df.iloc[x, 1] = results.fetchall()[0][0]

    except Exception as ex:   
        print(ex)

    finally:
        dbCon.close()

def create_ticker_tables(df, timeType = '_D'):
    dbCon = sqlEngine.raw_connection()
    cur = dbCon.cursor()

    try:
        for x in range(df.shape[0]):
            if df.iloc[x, 1] != None:
                continue
            tbl_name = df.iloc[x, 0] + timeType
            args = [tbl_name]
            cur.callproc('sp_createTable', args)
            print("Created table: ", tbl_name)

    except Exception as ex:   
        print(ex)

    finally:
        cur.close()
        dbCon.close()



def run_program():

    # Load ticker file
    tickers = load_tickers()
    if 'SPY' not in tickers:  # add SPY for reference, if absent
        tickers = ['SPY'] + tickers

    df_tickers = pd.DataFrame(tickers, columns=['ticker'])
    df_tickers['date'] = None

    # get latest dates for each ticker
    get_latest_ticker_date(df_tickers)

    # create tables for new tickers
    create_ticker_tables(df_tickers)

    # change datatype for date
    df_tickers['date'] = pd.to_datetime(df_tickers['date'])

    # Fetch data for new tickers
    df_new_tickers = df_tickers.loc[pd.isna(df_tickers['date']) == True]
    fetch_new_ticker_data(df_new_tickers)

    # Fetch data for existing tickers
    df_old_tickers = df_tickers.loc[pd.isna(df_tickers['date']) == False]
    fetch_existing_ticker_data(df_old_tickers)
    

if __name__ == "__main__":
    run_program()
