import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px
from io import StringIO

st.set_page_config(page_title="Yahoo Finance Viewer", page_icon="📊", layout="wide")
st.title('📊 Yahoo Finance Ticker Data Viewer')

# =========================
# Input user
# =========================
ticker_input = st.text_input("Masukan Ticker (Seperti BTC-USD, BNB-USD):", 'BTC-USD, BNB-USD')
tickers = [ticker.strip().upper() for ticker in ticker_input.split(',')]

start_date = st.date_input("Pilih tanggal mulai", pd.to_datetime('today') - pd.DateOffset(years=1))
end_date = st.date_input("Pilih tanggal akhir", pd.to_datetime('today'))

# =========================
# Ambil data
# =========================
data = {}
for ticker in tickers:
    try:
        stock_data = yf.download(ticker, start=start_date, end=end_date, progress=False, threads=False)
        if not stock_data.empty:
            data[ticker] = stock_data
        else:
            st.warning(f"⚠️ Tidak ada data ditemukan untuk {ticker}. Coba periksa ticker atau rentang tanggal.")
    except Exception as e:
        st.error(f"❌ Gagal mengambil data {ticker}. Error: {e}")

# =========================
# Tampilkan data + chart
# =========================
for ticker, stock_data in data.items():
    st.subheader(f'📌 Data untuk {ticker}')
    st.dataframe(stock_data.tail(10))  # tampilkan 10 data terakhir saja

    # =========================
    # Plot harga penutupan
    # =========================
    if "Close" in stock_data.columns:
        st.subheader(f'📈 Grafik Harga Penutupan {ticker}')
        fig = px.line(
            stock_data,
            x=stock_data.index,
            y='Close',
            title=f'{ticker} Closing Price',
            labels={'Close': 'Close Price (USD)', 'index': 'Date'},
            color_discrete_sequence=px.colors.sequential.Viridis
        )

        fig.update_traces(line=dict(width=2.5))
        fig.update_layout(
            xaxis_title='Date',
            yaxis_title='Close Price (USD)',
            template='plotly_dark',
            title=dict(text=f'{ticker} Closing Prices', font=dict(size=20, color='white'), x=0.5),
            xaxis=dict(showline=True, showgrid=False, linecolor='white'),
            yaxis=dict(showline=True, showgrid=True, gridcolor='gray', linecolor='white')
        )

        st.plotly_chart(fig, use_container_width=True)

    # =========================
    # Download CSV
    # =========================
    csv_buffer = StringIO()
    stock_data.to_csv(csv_buffer)
    csv_data = csv_buffer.getvalue()

    st.download_button(
        label=f"⬇️ Download data {ticker} sebagai CSV",
        data=csv_data,
        file_name=f"{ticker}_data.csv",
        mime="text/csv"
    )
