import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px
import requests
from io import StringIO

st.set_page_config(page_title="Crypto Data Viewer", page_icon="📊", layout="wide")
st.title("📊 Crypto Data Viewer (Yahoo Finance + Alpha Vantage Fallback)")

# =========================
# Konfigurasi API
# =========================
API_KEY = "45G1G2AY7W8KD3S5"
BASE_URL = "https://www.alphavantage.co/query"

# =========================
# Input user
# =========================
ticker_input = st.text_input("Masukan Ticker (Seperti BTC, ETH, BNB):", "BTC, ETH")
tickers = [ticker.strip().upper() for ticker in ticker_input.split(",")]

start_date = st.date_input("Pilih tanggal mulai", pd.to_datetime("today") - pd.DateOffset(years=1))
end_date = st.date_input("Pilih tanggal akhir", pd.to_datetime("today"))

data = {}

# =========================
# Fungsi ambil data Alpha Vantage
# =========================
def get_alpha_vantage_data(symbol):
    params = {
        "function": "DIGITAL_CURRENCY_DAILY",
        "symbol": symbol,
        "market": "USD",
        "apikey": API_KEY
    }
    response = requests.get(BASE_URL, params=params)
    json_data = response.json()

    if "Time Series (Digital Currency Daily)" in json_data:
        ts = json_data["Time Series (Digital Currency Daily)"]
        df = pd.DataFrame([
            {
                "Date": date,
                "Open": float(values.get("1a. open (USD)", 0)),
                "High": float(values.get("2a. high (USD)", 0)),
                "Low": float(values.get("3a. low (USD)", 0)),
                "Close": float(values.get("4a. close (USD)", 0)),
                "Volume": float(values.get("5. volume", 0)),
            }
            for date, values in ts.items()
        ])
        df["Date"] = pd.to_datetime(df["Date"])
        df = df.sort_values("Date")
        return df
    else:
        return pd.DataFrame()

# =========================
# Ambil data untuk tiap ticker
# =========================
for ticker in tickers:
    try:
        stock_data = yf.download(f"{ticker}-USD", start=start_date, end=end_date, progress=False, threads=False)
        if not stock_data.empty:
            data[ticker] = stock_data
            st.success(f"✅ Data {ticker} berhasil diambil dari Yahoo Finance")
        else:
            raise ValueError("Data kosong dari yfinance")
    except Exception as e:
        st.warning(f"⚠️ Yahoo Finance gagal untuk {ticker}, mencoba Alpha Vantage...")
        stock_data = get_alpha_vantage_data(ticker)
        if not stock_data.empty:
            data[ticker] = stock_data
            st.success(f"✅ Data {ticker} berhasil diambil dari Alpha Vantage")
        else:
            st.error(f"❌ Tidak ada data untuk {ticker}")

# =========================
# Tampilkan data + grafik
# =========================
for ticker, df in data.items():
    st.subheader(f"📌 Data untuk {ticker}")
    st.dataframe(df.tail(10))

    if "Close" in df.columns:
        st.subheader(f"📈 Grafik Harga Penutupan {ticker}")
        fig = px.line(df, x="Date", y="Close", title=f"{ticker} Closing Price (USD)",
                      labels={"Close": "Close Price (USD)", "Date": "Date"},
                      color_discrete_sequence=px.colors.sequential.Viridis)
        fig.update_traces(line=dict(width=2.5))
        fig.update_layout(template="plotly_dark", xaxis_title="Date", yaxis_title="Price (USD)")
        st.plotly_chart(fig, use_container_width=True)

    # Download CSV
    csv_buffer = StringIO()
    df.to_csv(csv_buffer, index=False)
    st.download_button(
        label=f"⬇️ Download data {ticker} sebagai CSV",
        data=csv_buffer.getvalue(),
        file_name=f"{ticker}_data.csv",
        mime="text/csv"
    )
