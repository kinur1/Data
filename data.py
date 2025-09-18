import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px

st.title("📈 Yahoo Finance Data Viewer")

# Input ticker dari user
ticker = st.text_input("Masukkan Ticker (contoh: BTC-USD, ETH-USD, AAPL):", "BTC-USD")

# Input rentang tanggal
start_date = st.date_input("Tanggal Mulai", pd.to_datetime("2022-01-01"))
end_date = st.date_input("Tanggal Akhir", pd.to_datetime("today"))

if st.button("Lihat Data"):
    try:
        # Ambil data dari yfinance
        data = yf.download(ticker, start=start_date, end=end_date)

        if data.empty:
            st.warning("⚠️ Data tidak ditemukan untuk ticker dan tanggal tersebut.")
        else:
            # Tampilkan data
            st.subheader(f"Data {ticker}")
            st.dataframe(data)

            # Plot harga penutupan
            fig = px.line(data, x=data.index, y="Close", title=f"Harga Penutupan {ticker}")
            st.plotly_chart(fig)

            # Plot volume
            fig_vol = px.bar(data, x=data.index, y="Volume", title=f"Volume Perdagangan {ticker}")
            st.plotly_chart(fig_vol)

    except Exception as e:
        st.error(f"Terjadi kesalahan: {e}")
