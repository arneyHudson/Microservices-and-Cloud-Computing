import sys
from argparse import ArgumentParser, FileType
from configparser import ConfigParser
from confluent_kafka import Consumer, OFFSET_BEGINNING
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
from datetime import datetime
import json


def create_consumer(config_file, reset_flag):
    # Parse the configuration file
    config_parser = ConfigParser()
    config_parser.read_file(config_file)
    config = dict(config_parser['default'])
    config.update(config_parser['consumer'])

    # Create Consumer instance
    consumer = Consumer(config)

    # Set up offset reset
    def reset_offset(consumer, partitions):
        if reset_flag:
            for p in partitions:
                p.offset = OFFSET_BEGINNING
            consumer.assign(partitions)

    return consumer, reset_offset


def process_message(msg):
    try:
        raw_value = msg.value().decode('utf-8')
        print(f"Raw message received: {raw_value}")  # Debug log
        value = json.loads(raw_value)  # Parse JSON
        return {
            "time": value.get("time"),
            "open": value.get("open"),
            "high": value.get("high"),
            "low": value.get("low"),
            "close": value.get("close"),
            "volume": value.get("volume")
        }
    except Exception as e:
        print(f"Failed to process message: {e}")
        return None


def plot_stock_data(df, ticker):
    # Create a figure and axis object using matplotlib for price data (open, high, low, close)
    fig, ax1 = plt.subplots(figsize=(10, 6))

    # Plot the line chart for open, high, low, and close
    ax1.plot(df.index, df['open'], label='Open', color='blue', linestyle='-', linewidth=2)
    ax1.plot(df.index, df['high'], label='High', color='green', linestyle='-', linewidth=2)
    ax1.plot(df.index, df['low'], label='Low', color='red', linestyle='-', linewidth=2)
    ax1.plot(df.index, df['close'], label='Close', color='orange', linestyle='-', linewidth=2)

    ax1.set_xlabel("Time", fontsize=12)  # Set x-axis label
    ax1.set_ylabel("Price (USD)", fontsize=12)  # Set y-axis label for price
    ax1.set_title(f"{ticker} Stock Price Data", fontsize=14)

    # Add legends for each line
    ax1.legend(loc='upper left')

    return fig  # Return the figure to display it later


def plot_volume_data(df, ticker):
    # Create a figure for the volume chart
    fig, ax2 = plt.subplots(figsize=(10, 6))

    # Plot the volume data
    ax2.plot(df.index, df['volume'], label='Volume', linestyle='-', color='pink')

    ax2.set_xlabel("Time", fontsize=12)  # Set x-axis label
    ax2.set_ylabel("Volume", fontsize=12)  # Set y-axis label
    ax2.set_title(f"{ticker} Volume Data", fontsize=14)

    # Add a legend for the volume line
    ax2.legend(loc='upper left')

    return fig  

def render_ticker_dashboard(ticker, data, placeholder):
    with placeholder:
        st.subheader(f"Ticker: {ticker}")
        col1, col2 = st.columns(2)
        with col1:
            stock_fig = plot_stock_data(data, ticker)
            st.pyplot(stock_fig)
            plt.close(stock_fig)
        with col2:
            volume_fig = plot_volume_data(data, ticker)
            st.pyplot(volume_fig)
            plt.close(volume_fig)

if __name__ == '__main__':
    # Parse command line arguments
    parser = ArgumentParser()
    parser.add_argument('config_file', type=FileType('r'), help="Path to Kafka config file")
    parser.add_argument('tickers', nargs='+', help="Stock ticker symbols, e.g., QQQ AAPL")
    parser.add_argument('--reset', action='store_true', help="Reset Kafka offsets to the beginning")
    args = parser.parse_args()

    # Streamlit Setup
    st.set_page_config(page_title="Stock Dashboard", layout="wide")
    st.title("Real-Time Stock Dashboard")
    
    # Initializing data storage for each ticker
    ticker_data = {ticker: pd.DataFrame(columns=["time", "open", "high", "low", "close", "volume"]) for ticker in args.tickers}
    
    ticker_plot_placeholder = {ticker: st.empty() for ticker in args.tickers}
    
    # Initializing Kafka Consumer
    consumer, reset_offset = create_consumer(args.config_file, args.reset)
    consumer.subscribe(args.tickers, on_assign=reset_offset)

    # Poll for messages and update dashboard
    try:
        while True:
            msg = consumer.poll(0.5)
            if msg is None:
                continue
            if msg.error():
                st.error(f"Error: {msg.error()}")
                continue

            ticker = msg.topic()
            data = process_message(msg)
            if data:
                df = ticker_data[ticker]
                new_entry = pd.DataFrame([data])
                
                if not new_entry.empty:
                    new_entry["time"] = pd.to_datetime(new_entry["time"])
                    new_entry.set_index("time", inplace=True)
                    ticker_data[ticker] = pd.concat([df, new_entry]).tail(500)

                render_ticker_dashboard(ticker, ticker_data[ticker], ticker_plot_placeholder[ticker])


    except KeyboardInterrupt:
        st.stop()
    finally:
        # Leave group and commit final offsets
        consumer.close()
