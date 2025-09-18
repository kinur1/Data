import streamlit as st
import yfinance as yf
import pandas as pd
import datetime

# Judul aplikasi
st.title("📈 Yahoo Finance Stock Viewer")

# Input ticker
ticker = st.text_input("Masukkan Ticker Saham (contoh: AAPL, TSLA, BBRI.JK)", "AAPL")

# Pilih rentang tanggal
start_date = st.date_input("Tanggal Mulai", datetime.date(2024, 1, 1))
end_date = st.date_input("Tanggal Akhir", datetime.date.today())

# Tombol ambil data
if st.button("Ambil Data"):
    try:
        # Download data
        data = yf.download(ticker, start=start_date, end=end_date)

        if not data.empty:
            st.subheader(f"Data Harga {ticker}")
            st.write(data.tail())  # tampilkan data terakhir
            
            # Chart harga penutupan
            st.subheader("Grafik Harga Penutupan")
            st.line_chart(data['Close'])

            # Volume perdagangan
            st.subheader("Grafik Volume")
            st.bar_chart(data['Volume'])
        else:
            st.warning("Data tidak ditemukan. Coba ticker lain.")
    except Exception as e:
        st.error(f"Terjadi error: {e}")
