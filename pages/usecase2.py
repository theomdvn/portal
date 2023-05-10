import streamlit as st
import pandas as pd
import datetime as dt
import requests
import plotly.graph_objects as go
import plotly_express as px
import json
import time
import numpy as np
import requests
st.markdown("# Use Case 2 TAL ❄️")
st.sidebar.markdown("# Use Case TAL ❄️")

# --------------------------------------------------------------------------------- # 
# --------------------------Data production---------------------------------------- # 
# --------------------------------------------------------------------------------- # 

df = pd.read_csv(r'C:\Users\theom\Desktop\INFRATAL\Streamlit\database\df_currency_10y22v4.csv', parse_dates=True)
df = df.drop(columns=['Unnamed: 0'])
df.set_index('date', inplace=True)
df['USDTAL'] = (1/df['USDCHF'])*100 + (1/df['USDEUR'])*250 + (1/df['USDGBP'])*50 + (1/df['USDJPY'])*18000 + (1/df['USDCNY'])*1600 + (1/df['USDSGD']*80) + ((df['USDGOLD'])*0.2)
df['USDTAL'] = df['USDTAL']*0.001 
df['USDTAL'] = 1/df['USDTAL']

# --------------------------------------------------------------------------------- # 
# ---------------------------------Data Weights------------------------------------ #
# --------------------------------------------------------------------------------- # 

weights_m = pd.DataFrame([(1/df['USDCHF'])*100,(1/df['USDEUR'])*250,(1/df['USDGBP'])*50,(1/df['USDJPY'])*18000,(1/df['USDCNY'])*1600,(1/df['USDSGD'])*80,((df['USDGOLD'])*0.2)])
weights_m = weights_m.T
w_chf = weights_m['USDCHF'] / (1/df['USDTAL']*1000)
w_eur = weights_m['USDEUR'] / (1/df['USDTAL']*1000)
w_gbp = weights_m['USDGBP'] / (1/df['USDTAL']*1000)
w_jpy = weights_m['USDJPY'] / (1/df['USDTAL']*1000)
w_cny = weights_m['USDCNY'] / (1/df['USDTAL']*1000)
w_sgd = weights_m['USDSGD'] / (1/df['USDTAL']*1000)
w_gold = weights_m['USDGOLD'] / (1/df['USDTAL']*1000)
weights_daily = pd.DataFrame([w_chf,w_eur,w_gbp,w_jpy,w_cny,w_sgd,w_gold])
weights_daily = weights_daily.T
weights_daily.columns = ['CHF','EUR','GBP','JPY','CNY','SGD','GOLD']

# --------------------------------------------------------------------------------- # 
data_rdm = pd.read_csv(r'C:\Users\theom\Desktop\INFRATAL\tal_pricer\rdm_depots.csv')
data_rdm.columns = data_rdm.iloc[0]
data_rdm = data_rdm.drop(data_rdm.index[0])
def anyrate(df,from_currency,to_currency):
    x = (1/df[from_currency])*df[to_currency]
    return x

def to_usd(df,from_currency):
    x = (1/df[from_currency])
    return x

def from_usd(df, to_currency):
    x = df[to_currency]
    return x
df.columns = df.columns.str.replace('USD','')
# data from https://donnees.banquemondiale.org/indicateur/FR.INR.DPST?end=2017&locations=FR&start=1966&view=chart

# --------------------------------------------------------------------------------- # 
# ---------------------------------Data BTC---------------------------------------- #
# --------------------------------------------------------------------------------- # 

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
df_btc = pd.DataFrame({'Timestamp': timestamps, 'BTC': closing_prices})

# Set the Timestamp column as the DataFrame index
df_btc.set_index('Timestamp', inplace=True)
df_btc.index.names = ['date']


# --------------------------------------------------------------------------------- # 


start_date = st.sidebar.date_input('Select start date:',
                                   dt.date(2018, 7, 17))
start_date = start_date.strftime('%d/%m/%Y %H:%M')

end_date = st.sidebar.date_input('Select end date:',
                                 dt.date(2023, 3, 17))
end_date = end_date.strftime('%d/%m/%Y %H:%M')

currencies = ['GOLD'] + ['BTC'] + list(df.columns)

filtered_df = df.loc[start_date:end_date]
filtered_df_btc = df_btc.loc[start_date:end_date]


# filtered_df = filtered_df.join(df_btc)
# filtered_df['Closing Price'] = filtered_df['Closing Price'].fillna(method='ffill')
# filtered_df = filtered_df.rename(columns={'Closing Price': 'BTC'})



qty = st.sidebar.number_input('Select quantity:', min_value=0, max_value=1000000000, value=0, step=1000)


# Create a dropdown menu to select a currency
currency = st.sidebar.selectbox('Choose a currency to invest at date :', df.columns)
currency2 = st.sidebar.selectbox('Choose a currency into invest at date :', currencies)
# --------------------------------------------------------------------------------- # 


fig = go.Figure()

talqty = qty*anyrate(filtered_df.loc[start_date],currency,'TAL')

fig.add_trace(go.Scatter(x=filtered_df.index,y=np.full_like(filtered_df.index, qty), name=currency))
tal_cur = talqty*anyrate(filtered_df,'TAL',currency)
fig.add_trace(go.Scatter(x=filtered_df.index, y=tal_cur, name=f'TAL{currency}'))

if currency2 == 'BTC':
    usd_qty = qty*to_usd(filtered_df.loc[start_date],from_currency=currency)
    btcqty = usd_qty*(1/df_btc.loc[start_date].values)
    btcqty_in_usd = (btcqty*filtered_df_btc['BTC'])
    #btc_cur = btcqty_in_usd*from_usd(filtered_df,currency)
    #st.write(btcqty)
    fig.add_trace(go.Scatter(x=filtered_df.index, y=btcqty_in_usd, name=f'BTC{currency}'))

    #compare = btc_cur.pct_change()
    compare = btcqty_in_usd.pct_change()

elif currency2 == 'GOLD':
    usd_qty = qty*to_usd(filtered_df.loc[start_date],from_currency=currency)

    gldqty = usd_qty*(1/filtered_df.loc[start_date]['GOLD'])
    gld_cur = (gldqty*filtered_df['GOLD'])*from_usd(filtered_df,currency)

    fig.add_trace(go.Scatter(x=filtered_df.index, y=gld_cur, name=f'GLD{currency}'))
    compare = gld_cur.pct_change()

else:
    currency_qty = qty*anyrate(filtered_df.loc[start_date],currency,currency2)
    cur2_cur = currency_qty*anyrate(filtered_df,currency2,currency) 
    fig.add_trace(go.Scatter(x=filtered_df.index, y=cur2_cur, name=f'{currency2}{currency}'))
    compare = cur2_cur.pct_change()


fig.update_layout(title='Currency Comparison',
                  xaxis_title='Date',
                  yaxis_title='Rate',
      width=1000,
      height=800
    )

col1, col2 = st.columns([2,1])

col1.plotly_chart(fig)


col2.markdown("<h1 style='font-size:18px;'>Historic weights: </h1>", unsafe_allow_html=True)
w_date = col2.date_input('Select a date:',
                                 dt.date(2018, 3, 15))
w_date = w_date.strftime('%d/%m/%Y %H:%M')
specific_row = weights_daily.loc[w_date]
repartition = pd.DataFrame({'Currency': ['CHF', 'EUR', 'GBP', 'JPY', 'CNY', 'SGD', 'Gold'],
                            'Weights': [specific_row['CHF'], specific_row['EUR'], specific_row['GBP'], specific_row['JPY'], specific_row['CNY'], specific_row['SGD'], specific_row['GOLD']]})

fig_weights = px.pie(repartition, values='Weights', names='Currency', title='Currency Repartition')#'Amount in {currency}'

col2.plotly_chart(fig_weights)
# Write text or annotations in the second column

# st.dataframe(weights_daily.sum(axis=1))

fig_w = go.Figure()
fig_w.add_trace(go.Scatter(x=weights_daily.index,y=weights_daily['CHF'], name='CHF'))
fig_w.add_trace(go.Scatter(x=weights_daily.index,y=weights_daily['EUR'], name='EUR'))
fig_w.add_trace(go.Scatter(x=weights_daily.index,y=weights_daily['GBP'], name='GBP'))
fig_w.add_trace(go.Scatter(x=weights_daily.index,y=weights_daily['JPY'], name='JPY'))
fig_w.add_trace(go.Scatter(x=weights_daily.index,y=weights_daily['CNY'], name='CNY'))
fig_w.add_trace(go.Scatter(x=weights_daily.index,y=weights_daily['SGD'], name='SGD'))
fig_w.add_trace(go.Scatter(x=weights_daily.index,y=weights_daily['GOLD'], name='GOLD'))
fig_w.update_layout(title='Currency Weights')
col2.plotly_chart(fig_w)


tal_cur = tal_cur.pct_change()


statistics_tal_cur = pd.DataFrame({
    'Currency': [f'TAL{currency}'],
    'Mean Return': [tal_cur.mean()],
    'Standard Deviation': [tal_cur.std()],
    'VaR': [tal_cur.quantile(0.05)],
    'ES': [tal_cur[tal_cur <= tal_cur.quantile(0.05)].mean()],
    'Max Drawdown': [tal_cur.min()],
})
statistics_tal_cur.set_index('Currency', inplace=True)

statistics_compare = pd.DataFrame({
    'Currency': [f'{currency2}{currency}'],
    'Mean Return': [compare.mean()],
    'Standard Deviation': [compare.std()],
    'VaR': [compare.quantile(0.05)],
    'ES': [compare[compare <= compare.quantile(0.05)].mean()],
    'Max Drawdown': [compare.min()],
})
statistics_compare.set_index('Currency', inplace=True)


col1.markdown("<h1 style='font-size:18px;'>Statistics : </h1>", unsafe_allow_html=True)

col1.dataframe(statistics_tal_cur)
col1.markdown('---')
col1.dataframe(statistics_compare)