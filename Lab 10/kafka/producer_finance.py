#!/usr/bin/env python

import sys
from random import choice
from argparse import ArgumentParser, FileType
from configparser import ConfigParser
from confluent_kafka import Producer

import requests
import numpy as np
import pandas as pd
from datetime import datetime
from datetime import date
from datetime import timedelta
import time
import yfinance as yf
import json

def get_today():
    return date.today()

def get_next_day_str(today):
    return today + timedelta(days=1)

def fetch_stock_data(tickers, start_date=None, end_date=None, interval="1m"):
    """
    Fetch stock data for multiple tickers using yfinance.
    """
    try:
        tickers_str = ",".join(tickers)  # Join tickers as a single string
        if start_date and end_date:
            data = yf.download(tickers=tickers_str, start=start_date, end=end_date, interval=interval, group_by="ticker")
        else:
            data = yf.download(tickers=tickers_str, interval=interval, group_by="ticker")
        return data
    except Exception as e:
        print(f"Error fetching data for {tickers}: {e}")
        return None

def generate_weekly_intervals(start_date, end_date):
    """
    Generate weekly intervals between start_date and end_date.
    """
    current = start_date
    while current < end_date:
        next_week = current + timedelta(days=7)
        yield current, min(next_week, end_date)
        current = next_week

if __name__ == '__main__':
    # Parse command-line arguments
    parser = ArgumentParser()
    parser.add_argument('config_file', type=FileType('r'), help="Path to Kafka config file")
    parser.add_argument('tickers', help="Comma-separated stock ticker symbols, e.g., NVDA,AAPL")
    parser.add_argument('--mode', choices=['dev', 'realtime'], default='dev',
                        help="Mode of operation: 'dev' for static dates, 'realtime' for live data")
    args = parser.parse_args()

    # Parse the configuration file
    config_parser = ConfigParser()
    config_parser.read_file(args.config_file)
    config = dict(config_parser['default'])

    # Read tickers and mode
    tickers = args.tickers.split(",")
    mode = args.mode
    print('Tickers:', tickers)
    print('Mode:', mode)

    # Create Kafka Producer
    producer = Producer(config)

    # Define delivery callback
    def delivery_callback(err, msg):
        if err:
            print('ERROR: Message failed delivery: {}'.format(err))
        else:
            print(f"Produced event to topic {msg.topic()}: key={msg.key().decode()} value={msg.value().decode()}")

    # Determine date range for dev mode
    if mode == 'dev':
        start_date = get_today() - timedelta(days=365)  # Start date: 1 year ago
        end_date = get_today()  # End date: today
        interval = "1d"  # Daily data for dev mode
    elif mode == 'realtime':
        start_date = get_today()
        end_date = start_date + timedelta(days=1)
        interval = "1m"  # Minute-by-minute data for realtime mode

    while True:
        for ticker in tickers:
            if mode == 'dev':
                print(f"Fetching historical data for tickers {tickers} in weekly intervals...")
                for start, end in generate_weekly_intervals(start_date, end_date):
                    print(f"Fetching data from {start} to {end}...")
                    df = fetch_stock_data(tickers, start_date=start, end_date=end, interval=interval)
                    if df is None:
                        print(f"No data fetched for tickers {tickers} between {start} and {end}. Skipping...")
                        continue

                    # Process each ticker's data separately
                    for ticker in tickers:
                        ticker_data = df[ticker] if isinstance(df.columns, pd.MultiIndex) else df
                        if ticker_data.empty:
                            print(f"No data available for {ticker} in this interval. Skipping...")
                            continue

                        topic = ticker
                        for index, row in ticker_data.iterrows():
                            try:
                                data = {
                                    "time": index.strftime('%Y-%m-%d %H:%M:%S'),
                                    "open": row["Open"],
                                    "high": row["High"],
                                    "low": row["Low"],
                                    "close": row["Close"],
                                    "volume": row["Volume"]
                                }
                                producer.produce(topic, key=str(index), value=json.dumps(data), callback=delivery_callback)
                                print(f"Produced for {ticker}: {data}")
                                time.sleep(5)
                            except Exception as e:
                                print(f"Error producing message for {ticker}: {e}")

            elif mode == 'realtime':
                print(f"Fetching live data for {ticker}...")
                df = fetch_stock_data(ticker, start_date=start_date, end_date=end_date, interval=interval)
                if df is None or df.empty:
                    print(f"No data fetched for {ticker}. Skipping...")
                    continue

                # Produce messages for each row
                topic = ticker
                for index, row in df.iterrows():
                    try:
                        data = {
                            "time": index.strftime('%Y-%m-%d %H:%M:%S'),
                            "open": row["Open"],
                            "high": row["High"],
                            "low": row["Low"],
                            "close": row["Close"],
                            "volume": row["Volume"]
                        }
                        producer.produce(topic, key=str(index), value=json.dumps(data), callback=delivery_callback)
                        print(f"Produced for {ticker}: {data}")
                        time.sleep(5)
                    except Exception as e:
                        print(f"Error producing message for {ticker}: {e}")

        # Ensure all messages are delivered
        producer.poll(10000)
        producer.flush()

        if mode == 'dev':
            break  # Stop after processing all data in dev mode
        else:
            print("Waiting for the next update...")
            time.sleep(60)  # Fetch live data every minute
