import streamlit as st
import yfinance as yf
import datetime

st.title("📈 Yahoo Finance Stock Viewer")

ticker = st.text_input("Masukkan Ticker Saham (contoh: AAPL, TSLA, BBRI.JK)", "AAPL")

start_date = st.date_input("Tanggal Mulai", datetime.date(2024, 1, 1))
end_date = st.date_input("Tanggal Akhir", datetime.date.today())

if st.button("Ambil Data"):
    try:
        # Tambah 1 hari ke end_date biar data terbaru bisa masuk
        data = yf.download(
            ticker,
            start=start_date,
            end=end_date + datetime.timedelta(days=1),
            interval="1d",
            progress=False
        )

        if not data.empty:
            st.subheader(f"Data Harga {ticker}")
            st.write(data.tail())

            st.subheader("Grafik Harga Penutupan")
            st.line_chart(data['Close'])

            st.subheader("Grafik Volume")
            st.bar_chart(data['Volume'])
        else:
            st.warning("⚠️ Data tidak ditemukan. Coba cek ticker atau rentang tanggal.")
    except Exception as e:
        st.error(f"Terjadi error: {e}")
