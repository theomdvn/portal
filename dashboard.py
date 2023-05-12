import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
import requests    
import pandas as pd 
import io
import datetime as dt
import datapungi_fed as dpf
import yfinance as yf
from pages.database import database


st.title('JOUJOU TAL')
#st.markdown("JOUJOU TAL")
st.sidebar.markdown("# Main page ")

# st.write('Welcome to my first Streamlit app!')

# Create a dropdown menu to select a currency
start_date = st.sidebar.date_input('Select start date:',
                                    dt.date(2018, 7, 17))
start_date = start_date.strftime('%Y-%m-%d')
start_date = pd.Timestamp(start_date)
end_date = st.sidebar.date_input('Select end date:')
end_date = end_date.strftime('%Y-%m-%d')
end_date = pd.Timestamp(end_date)

currency = st.sidebar.selectbox('Choose a currency to plot:', database.columns)
currency_to_compare = st.sidebar.selectbox('Choose a currency to compare:', database.columns)

# Plot the selected currency rate using Plotly
# Filter the DataFrame based on the selected date range
filtered_df = database.loc[start_date:end_date]



# Define colors for the currencies
color_currency = 'lightblue'
color_currency_to_compare = 'cornflowerblue'

# # Create the figure
# fig = go.Figure()

# # Add the first currency trace with the primary Y-axis
# fig.add_trace(go.Scatter(x=filtered_df.index, y=filtered_df[currency], name=currency, yaxis='y1', line=dict(color=color_currency)))

# # Add the second currency trace with the secondary Y-axis
# fig.add_trace(go.Scatter(x=filtered_df.index, y=filtered_df[currency_to_compare], name=currency_to_compare, yaxis='y2', line=dict(color=color_currency_to_compare)))

# # Update the layout
# fig.update_layout(
#     title='Currency Comparison',
#     xaxis_title='Date',
#     yaxis=dict(
#         title=f'{currency} Rate',
#         titlefont=dict(color=color_currency),
#         tickfont=dict(color=color_currency)
#     ),
#     yaxis2=dict(
#         title=f'{currency_to_compare} Rate',
#         titlefont=dict(color=color_currency_to_compare),
#         tickfont=dict(color=color_currency_to_compare),
#         anchor='x',
#         overlaying='y',
#         side='right'
#     ),
#     width=1200,
#     height=800
# )
fig = go.Figure()

# Add the first currency trace with the primary Y-axis
fig.add_trace(go.Scatter(x=filtered_df.index, y=filtered_df[currency], name=currency, yaxis='y1', line=dict(color=color_currency)))

# Add the second currency trace with the secondary Y-axis
fig.add_trace(go.Scatter(x=filtered_df.index, y=filtered_df[currency_to_compare], name=currency_to_compare, yaxis='y2', line=dict(color=color_currency_to_compare)))

# Update the layout
fig.update_layout(
    title='Currency Comparison',
    xaxis_title='Date',
    yaxis=dict(
        title=f'{currency} Rate',
        titlefont=dict(color=color_currency),
        tickfont=dict(color=color_currency)
    ),
    yaxis2=dict(
        title=f'{currency_to_compare} Rate',
        titlefont=dict(color=color_currency_to_compare),
        tickfont=dict(color=color_currency_to_compare),
        anchor='x',
        overlaying='y',
        side='right'
    ),
     width=1200,
     height=800
)

# Display the plot using Streamlit
st.plotly_chart(fig)

#st.write(type(filtered_df.index))
if st.checkbox('Show variation'):   
    database = database.pct_change()
    filtered_df = database.loc[start_date:end_date]
        # Create two columns using Streamlit
    col1, col2 = st.columns(2)

    # Create the first figure
    fig1 = go.Figure()
    fig1.add_trace(go.Scatter(x=filtered_df.index, y=filtered_df[currency], name=currency))
    fig1.update_layout(title='Currency Comparison',
                    xaxis_title='Date',
                    yaxis_title='Rate')

    # Create the second figure
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(x=filtered_df.index, y=filtered_df[currency_to_compare], name=currency_to_compare))
    fig2.update_layout(title='Currency Comparison',
                    xaxis_title='Date',
                    yaxis_title='Rate')

    # Display the plots using Streamlit within the columns
    col1.plotly_chart(fig1)
    col2.plotly_chart(fig2)