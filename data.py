import requests
import pandas as pd

API_KEY = "45G1G2AY7W8KD3S5"
symbol = "BTC"
market = "USD"

url = f"https://www.alphavantage.co/query?function=DIGITAL_CURRENCY_DAILY&symbol={symbol}&market={market}&apikey={API_KEY}"
r = requests.get(url)
data = r.json()

time_series = data["Time Series (Digital Currency Daily)"]

df = pd.DataFrame(time_series).T
df = df.rename(columns={
    "1a. open (USD)": "Open",
    "2a. high (USD)": "High",
    "3a. low (USD)": "Low",
    "4a. close (USD)": "Close",
    "5. volume": "Volume"
})

df = df[["Open", "High", "Low", "Close", "Volume"]].astype(float)
df.index = pd.to_datetime(df.index)
df = df.sort_index()

print(df.head())
