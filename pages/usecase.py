import streamlit as st
import pandas as pd
import datetime as dt
import requests
import plotly.graph_objects as go
import plotly_express as px
import json
import numpy as np
from pages.database import database

st.markdown("# Use Case TAL ❄️")
st.sidebar.markdown("# Use Case TAL ❄️")

import requests

# Paramètres de la requête
symbol = 'BTCUSDT'  # Symbole du trading pair (BTC/USDT)
interval = '1d'    # Intervalle de temps (1 jour)

# URL de l'API Binance pour les données historiques
url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}"

# Effectuer la requête GET
response = requests.get(url)

# Vérifier si la requête a réussi
if response.status_code == 200:
    # Récupérer les données
    historical_data = response.json()

    # Créer un DataFrame à partir des données
    df_btc = pd.DataFrame(historical_data, columns=['Open time', 'Open', 'High', 'Low', 'Close', 'Volume', 'Close time', 'Quote asset volume', 'Number of trades', 'Taker buy base asset volume', 'Taker buy quote asset volume', 'Ignore'])

    # Convertir les colonnes pertinentes en types appropriés
    df_btc['Open time'] = pd.to_datetime(df['Open time'], unit='ms')
    df_btc['Close time'] = pd.to_datetime(df['Close time'], unit='ms')
    df_btc[['Open', 'High', 'Low', 'Close', 'Volume']] = df[['Open', 'High', 'Low', 'Close', 'Volume']].astype(float)
    df_btc = df_btc[['Close time', 'Close']]
    # Afficher le DataFrame
    st.dataframe(df_btc)

else:
    print("La requête a échoué avec le code d'état :", response.status_code)



df = pd.read_csv(r'C:\Users\theom\Desktop\INFRATAL\MonteCarlo TAL\Database\df_currency_10y22v4.csv', parse_dates=True)
df = df.drop(columns=['Unnamed: 0'])
df.set_index('date', inplace=True)
df['USDTAL'] = (1/df['USDCHF'])*100 + (1/df['USDEUR'])*250 + (1/df['USDGBP'])*50 + (1/df['USDJPY'])*18000 + (1/df['USDCNY'])*1600 + (1/df['USDSGD']*80) + ((df['USDGOLD'])*0.2)

df['USDTAL'] = df['USDTAL']*0.001

df['USDTAL'] = 1/df['USDTAL']

df = database.copy()

data_rdm = pd.read_csv(r'C:\Users\theom\Desktop\INFRATAL\tal_pricer\rdm_depots.csv')
data_rdm.columns = data_rdm.iloc[0]
data_rdm = data_rdm.drop(data_rdm.index[0])
# data from https://donnees.banquemondiale.org/indicateur/FR.INR.DPST?end=2017&locations=FR&start=1966&view=chart

# Identify columns containing "EUR" and with length greater than 3

df.columns = df.columns.str.replace('USD', '')

cols_to_drop = [col for col in df.columns if 'EUR' in col and len(col) > 3]
# Drop the identified columns from the DataFrame
df = df.drop(columns=cols_to_drop)

start_date = st.sidebar.date_input('Select start date:',
                                   dt.date(2018, 7, 17))
start_date = start_date.strftime('%Y-%m-%d')
start_date = pd.Timestamp(start_date)

end_date = st.sidebar.date_input('Select end date:')
end_date = end_date.strftime('%Y-%m-%d')
end_date = pd.Timestamp(end_date)

def anyrate(df,from_currency,to_currency):
    x = (1/df[from_currency])*df[to_currency]
    return x


qty = st.sidebar.number_input('Select quantity:', min_value=0, max_value=1000000000, value=0, step=1000)

# Create a dropdown menu to select a currency

currency = st.sidebar.selectbox('Choose a currency to invest at date :', df.columns)


filtered_df = df.loc[start_date:end_date]

talqty = qty*anyrate(filtered_df.loc[start_date],currency,'TAL')


if st.checkbox('Show dataframe'):
    st.write(filtered_df)

fig = go.Figure()

fig.add_trace(go.Scatter(x=filtered_df.index,y=np.full_like(filtered_df.index, qty), name=currency))
fig.add_trace(go.Scatter(x=filtered_df.index, y=talqty*anyrate(filtered_df,'TAL',currency), name=f'TAL{currency}'))

fig.update_layout(title='Currency Comparison',
                  xaxis_title='Date',
                  yaxis_title='Rate')
# Display the plot using Streamlit
st.plotly_chart(fig)


