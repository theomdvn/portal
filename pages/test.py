import requests
import pandas as pd
import time
from datetime import datetime
import streamlit as st
# Define the API endpoint and parameters
url = "https://api.binance.com/api/v3/klines"
symbol = "BTCUSDT"    # BTC trading pair symbol
interval = "1d"       # Daily interval (1 day)
limit = 1000          # Maximum number of data points to fetch per request (max: 1000)
start_timestamp = 1262304000000  # Start timestamp in milliseconds (e.g., January 1, 2010)
end_timestamp = int(time.time() * 1000)  # Current timestamp in milliseconds

# Create an empty list to store the data
data_list = []

# Perform pagination to fetch historical data in smaller chunks
current_timestamp = start_timestamp
while current_timestamp <= end_timestamp:
    # Define the parameters for the current request
    params = {
        "symbol": symbol,
        "interval": interval,
        "startTime": current_timestamp,
        "limit": limit
    }

    # Make a GET request to the Binance API
    response = requests.get(url, params=params)

    # Parse the response JSON
    data = response.json()

    # Check if the data is empty (reached the end of available data)
    if not data:
        break

    # Append the data to the list
    data_list.extend(data)

    # Update the current timestamp to the end timestamp of the fetched data
    current_timestamp = data[-1][0] + 1

    # Add a delay to avoid overwhelming the API
    time.sleep(0.5)

# Extract the timestamp and closing price data
timestamps = [entry[0] for entry in data_list]
closing_prices = [float(entry[4]) for entry in data_list]

# Convert the timestamp to datetime format
timestamps = pd.to_datetime(timestamps, unit='ms')

# Create a DataFrame from the extracted data
df = pd.DataFrame({'Timestamp': timestamps, 'Closing Price': closing_prices})

# Set the Timestamp column as the DataFrame index
df.set_index('Timestamp', inplace=True)

# Print the DataFrame
st.dataframe(df)