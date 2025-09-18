import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from io import StringIO

st.title("📊 Cryptocurrency Data Viewer (Alpha Vantage API)")

API_KEY = "45G1G2AY7W8KD3S5"
BASE_URL = "https://www.alphavantage.co/query"

# Input ticker
ticker_input = st.text_input("Masukan Ticker (Seperti BTC, ETH, BNB):", "BTC, ETH")
tickers = [ticker.strip().upper() for ticker in ticker_input.split(",")]

data = {}

for ticker in tickers:
    try:
        params = {
            "function": "DIGITAL_CURRENCY_DAILY",
            "symbol": ticker,
            "market": "USD",
            "apikey": API_KEY
        }
        response = requests.get(BASE_URL, params=params)
        json_data = response.json()

        if "Time Series (Digital Currency Daily)" in json_data:
            ts = json_data["Time Series (Digital Currency Daily)"]
            records = []
            for date, values in ts.items():
                records.append({
                    "Date": date,
                    "Open": float(values.get("1a. open (USD)", values.get("1b. open (USD)", 0))),
                    "High": float(values.get("2a. high (USD)", values.get("2b. high (USD)", 0))),
                    "Low": float(values.get("3a. low (USD)", values.get("3b. low (USD)", 0))),
                    "Close": float(values.get("4a. close (USD)", values.get("4b. close (USD)", 0))),
                    "Volume": float(values.get("5. volume", 0))
                })
            df = pd.DataFrame(records)

            # Urutkan berdasarkan tanggal
            df["Date"] = pd.to_datetime(df["Date"])
            df = df.sort_values("Date")
            data[ticker] = df
        else:
            st.warning(f"Tidak ada data untuk {ticker}. Cek simbolnya.")

    except Exception as e:
        st.error(f"Gagal ambil data {ticker}: {e}")

# Tampilkan data + grafik
for ticker, df in data.items():
    st.subheader(f"Data untuk {ticker}")
    st.write(df.tail(10))  # tampilkan 10 terakhir

    # Plot harga penutupan
    st.subheader(f"Grafik Harga Penutupan {ticker}")
    fig = px.line(df, x="Date", y="Close", title=f"{ticker} Closing Price",
                  labels={"Close": "Close Price (USD)", "Date": "Date"},
                  color_discrete_sequence=px.colors.sequential.Viridis)
    fig.update_traces(line=dict(width=2.5))
    fig.update_layout(template="plotly_dark", xaxis_title="Date", yaxis_title="Price (USD)")
    st.plotly_chart(fig)

    # Download CSV
    csv_buffer = StringIO()
    df.to_csv(csv_buffer, index=False)
    st.download_button(
        label=f"Download {ticker} data as CSV",
        data=csv_buffer.getvalue(),
        file_name=f"{ticker}_data.csv",
        mime="text/csv"
    )
