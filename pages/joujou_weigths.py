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
st.markdown("# Joujou weigths ")
st.sidebar.markdown("#  Joujou weigths ")

# --------------------------------------------------------------------------------- # 
# --------------------------Data production---------------------------------------- # 
# --------------------------------------------------------------------------------- # 

df = pd.read_csv(r'https://raw.githubusercontent.com/theomdvn/portal/master/database/df_currency_10y22v4.csv', parse_dates=True)
df = df.drop(columns=['Unnamed: 0'])
df.set_index('date', inplace=True)
df['USDTAL'] = (1/df['USDCHF'])*100 + (1/df['USDEUR'])*250 + (1/df['USDGBP'])*50 + (1/df['USDJPY'])*18000 + (1/df['USDCNY'])*1600 + (1/df['USDSGD']*80) + ((df['USDGOLD'])*0.2)
df['USDTAL'] = df['USDTAL']*0.001 
df['USDTAL'] = 1/df['USDTAL']

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

st.markdown("<h1 style='font-size:18px;'>Historic weights: </h1>", unsafe_allow_html=True)
w_date = st.date_input('Select a date:',
                                 dt.date(2018, 3, 15))
w_date = w_date.strftime('%d/%m/%Y %H:%M')
specific_row = weights_daily.loc[w_date]
repartition = pd.DataFrame({'Currency': ['CHF', 'EUR', 'GBP', 'JPY', 'CNY', 'SGD', 'Gold'],
                            'Weights': [specific_row['CHF'], specific_row['EUR'], specific_row['GBP'], specific_row['JPY'], specific_row['CNY'], specific_row['SGD'], specific_row['GOLD']]})

fig_weights = px.pie(repartition, values='Weights', names='Currency', title='Currency Repartition')#'Amount in {currency}'

st.plotly_chart(fig_weights)

# st.dataframe(weights_daily.sum(axis=1))

fig_w = go.Figure()
fig_w.add_trace(go.Scatter(x=pd.to_datetime(weights_daily.index, format='%d/%m/%Y %H:%M'),y=weights_daily['CHF'], name='CHF'))
fig_w.add_trace(go.Scatter(x=pd.to_datetime(weights_daily.index, format='%d/%m/%Y %H:%M'),y=weights_daily['EUR'], name='EUR'))
fig_w.add_trace(go.Scatter(x=pd.to_datetime(weights_daily.index, format='%d/%m/%Y %H:%M'),y=weights_daily['GBP'], name='GBP'))
fig_w.add_trace(go.Scatter(x=pd.to_datetime(weights_daily.index, format='%d/%m/%Y %H:%M'),y=weights_daily['JPY'], name='JPY'))
fig_w.add_trace(go.Scatter(x=pd.to_datetime(weights_daily.index, format='%d/%m/%Y %H:%M'),y=weights_daily['CNY'], name='CNY'))
fig_w.add_trace(go.Scatter(x=pd.to_datetime(weights_daily.index, format='%d/%m/%Y %H:%M'),y=weights_daily['SGD'], name='SGD'))
fig_w.add_trace(go.Scatter(x=pd.to_datetime(weights_daily.index, format='%d/%m/%Y %H:%M'),y=weights_daily['GOLD'], name='GOLD'))
fig_w.update_layout(title='Currency Weights')
st.plotly_chart(fig_w)