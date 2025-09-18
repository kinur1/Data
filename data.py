import streamlit as st
import requests
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Crypto Data Viewer", page_icon="📊", layout="wide")

API_KEY = "45G1G2AY7W8KD3S5"

st.title("📊 Cryptocurrency Data Viewer (Alpha Vantage API)")
tickers = st.text_input("Masukkan Ticker (Seperti BTC, ETH, BNB):", "BTC, ETH")

if tickers:
    tickers = [t.strip().upper() for t in tickers.split(",")]

    for ticker in tickers:
        st.subheader(f"Data untuk {ticker}")

        url = f"https://www.alphavantage.co/query?function=DIGITAL_CURRENCY_DAILY&symbol={ticker}&market=USD&apikey={API_KEY}"
        r = requests.get(url)
        data = r.json()

        if "Time Series (Digital Currency Daily)" not in data:
            st.error(f"Gagal ambil data {ticker}")
            continue

        ts = data["Time Series (Digital Currency Daily)"]

        df = pd.DataFrame(ts).T
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

        st.dataframe(df.tail(10))  # tampilkan 10 data terakhir

        # Chart harga penutupan pakai Plotly
        st.subheader(f"Grafik Harga Penutupan {ticker}")
        fig = px.line(df, x=df.index, y="Close", title=f"{ticker} Closing Price (USD)",
                      labels={"x": "Date", "Close": "Price (USD)"},
                      template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)
