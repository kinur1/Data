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

        # 🔹 Cek kolom yang tersedia
        st.write("Kolom asli:", df.columns.tolist())

        # Cari kolom yang sesuai
        rename_map = {}
        for col in df.columns:
            if "open" in col: rename_map[col] = "Open"
            elif "high" in col: rename_map[col] = "High"
            elif "low" in col: rename_map[col] = "Low"
            elif "close" in col: rename_map[col] = "Close"
            elif "volume" in col: rename_map[col] = "Volume"

        df = df.rename(columns=rename_map)

        # Pilih hanya kolom yang berhasil diubah namanya
        available_cols = [c for c in ["Open", "High", "Low", "Close", "Volume"] if c in df.columns]
        df = df[available_cols].astype(float)

        df.index = pd.to_datetime(df.index)
        df = df.sort_index()

        st.dataframe(df.tail(10))  # tampilkan 10 data terakhir

        if "Close" in df.columns:
            # Chart harga penutupan pakai Plotly
            st.subheader(f"Grafik Harga Penutupan {ticker}")
            fig = px.line(df, x=df.index, y="Close", title=f"{ticker} Closing Price (USD)",
                          labels={"x": "Date", "Close": "Price (USD)"},
                          template="plotly_dark")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning(f"Tidak ada data harga penutupan (Close) untuk {ticker}")
