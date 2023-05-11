import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
import requests    
import pandas as pd 
import io
import datetime
import datapungi_fed as dpf
import yfinance as yf

st.markdown("# Database TAL ❄️")
st.sidebar.markdown("# Database TAL ❄️")

fred = dpf.data("4836c0505f939fde997bcff5d008211d")
XXUS = ['CH','MX','JP','KO','CA','VZ','IN','BZ','SZ','SF','HK','NO','SD','SI']
USXX = ['UK','NZ','AL']
    #JP = Japan / CH = China /UK = United Kingdom / MX = Mexico
    #KO = South Korea / BZ = Brazil / SZ = Switzerland / AL = Australia
    #SF = South Africa / HK = Hong Kong / NZ = New Zealand / SD = Sweden
    #VZ = Venezuela / IN = India / NO = Norway /SI = Singapore
currency_country_map = {
        #"USD": "USA",  # United States Dollar
        #"EUR": "EUR",  # Euro (used by multiple European countries)
        "JPY": "JPN",  # Japanese Yen
        "GBP": "GBR",  # British Pound Sterling
        "AUD": "AUS",  # Australian Dollar
        "CAD": "CAN",  # Canadian Dollar
        "CHF": "CHE",  # Swiss Franc
        "CNY": "CNH",  # Chinese Yuan
        "SEK": "SWE",  # Swedish Krona
        "NZD": "NIU",  # New Zealand Dollar
        "MXN": "MEX",  # Mexican Peso
        "SGD": "SGP",  # Singapore Dollar
        "HKD": "HKG",  # Hong Kong Dollar
        "NOK": "NOR",  # Norwegian Krone
        "KRW": "KOR",  # South Korean Won
        "TRY": "TUR",  # Turkish Lira
        "RUB": "RUS",  # Russian Ruble
        "INR": "IND",  # Indian Rupee
        "BRL": "BRA",  # Brazilian Real
        "ZAR": "ZAF",  # South African Rand
        "NOK": "NOR",  # Norwegian Krone
        "KRW": "KOR",  # South Korean Won
        "PLN": "POL",  # Polish Zloty
        "ARS": "ARG",  # Argentine Peso
        # Add more currencies and country codes here
    }

start_date = '2010-01-01'

datafred = fred.series('DEXUSEU')

for i in range(len(XXUS)):
        key = 'DEX'+XXUS[i]+'US'
        datafred = datafred.join(fred.series(key))
for i in range(len(USXX)):
        key = 'DEXUS'+USXX[i]
        datafred = datafred.join(fred.series(key))
datafred.columns = datafred.columns.str.replace('DEX', '')
datafred = datafred.rename(columns={'USEU': 'EURUSD', 'CHUS': 'USDCNY', 'MXUS':'USDMXN','JPUS':'USDJPY','KOUS':'USDKRW',
                                        'CAUS':'USDCAD','HKUS':'USDHKD','INUS':'USDINR','UKUS':'USDGBP', 
                                        'AUUS':'USDAUD','NZUS':'USDNZD','SDUS':'USDSEK','NOUS':'USDNOK',
                                        'SIUS':'USDSGD','SZUS':'USDCHF','SFUS':'USDZAR','BZUS':'USDBRL',
                                        'USUK':'USDGBP','USNZ':'USDNZD','USAL':'USDAUD','VZUS':'USDVEF'})
datafred['EURUSD'] = 1/datafred['EURUSD']

today = datetime.datetime.today().strftime('%Y-%m-%d')

def url_builder(currency, start_date, end_date):
        # Building blocks for the URL
        entrypoint = 'https://sdw-wsrest.ecb.europa.eu/service/' # Using protocol 'https'
        resource = 'data'           # The resource for data queries is always'data'
        flowRef ='EXR'              # Dataflow describing the data that needs to be returned, exchange rates in this case
        key = f'D.{currency}.EUR.SP00.A'    # Defining the dimension values, explained below

        # https://sdw-wsrest.ecb.europa.eu/help/ for more information on the API

        # Define the parameters
        parameters = {
            'startPeriod':start_date,  # Start date of the time series
            'endPeriod': end_date     # End of the time series
        }
        url = entrypoint + resource + '/'+ flowRef + '/' + key
        return url, parameters

databce = pd.DataFrame()

response = requests.get(url_builder('USD', start_date, today)[0], params=url_builder('USD', start_date, today)[1], headers={'Accept': 'text/csv'})
df = pd.read_csv(io.StringIO(response.text))
df['OBS_VALUE'].describe()
databce = df.filter(['TIME_PERIOD', 'OBS_VALUE'], axis=1)
databce['TIME_PERIOD'] = pd.to_datetime(databce['TIME_PERIOD'])
databce = databce.set_index('TIME_PERIOD')
databce = databce.rename(columns={'OBS_VALUE': f'USDEUR'})

for i in currency_country_map.keys():
        response = requests.get(url_builder(i, start_date, today)[0], params=url_builder(i,start_date, today)[1], headers={'Accept': 'text/csv'})
        df = pd.read_csv(io.StringIO(response.text))
        
        if 'TIME_PERIOD' not in df.columns:
            print(f"No data found for currency {i}. Skipping.")
            continue

        ts = df.filter(['TIME_PERIOD', 'OBS_VALUE'], axis=1)
        ts['TIME_PERIOD'] = pd.to_datetime(ts['TIME_PERIOD'])
        ts = ts.set_index('TIME_PERIOD')
        ts = ts.rename(columns={'OBS_VALUE': f'{i}EUR'})
        databce = databce.join(ts, how='left')

database = databce.join(datafred, how='left')

datagld = yf.download('GC=F', start = start_date, end=today, progress=False)['Adj Close']

database['GLDUSD'] = datagld

database = database.fillna(method='ffill')

database['USDTAL'] = (1/database['USDCHF'])*100 + (1/database['USDEUR'])*250 + (1/database['USDGBP'])*50 + (1/database['USDJPY'])*18000 + (1/database['USDCNY'])*1600 + (1/database['USDSGD']*80) + ((database['GLDUSD'])*0.2)

database['USDTAL'] = database['USDTAL']*0.001

database['USDTAL'] = 1/database['USDTAL']

database['EURTAL'] = (1/database['CHFEUR'])*100 + 250 + (1/database['GBPEUR'])*50 + (1/database['JPYEUR'])*18000 + (1/database['CNYEUR'])*1600 + (1/database['SGDEUR']*80) + ((database['GLDUSD'])*0.2)*(1/database['USDEUR'])

database['EURTAL'] = database['EURTAL']*0.001

database['EURTAL'] = 1/database['EURTAL']
    
database = database[::-1]

st.write(database)
