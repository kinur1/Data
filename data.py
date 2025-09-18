import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from io import StringIO
from datetime import datetime, date

st.set_page_config(page_title="Alpha Vantage Crypto Viewer", layout="wide", page_icon="📈")
st.title("📊 Cryptocurrency Data Viewer (Alpha Vantage)")

# === CONFIG ===
API_KEY = "45G1G2AY7W8KD3S5"  # ganti kalau perlu
BASE_URL = "https://www.alphavantage.co/query"

# === INPUTS ===
ticker_input = st.text_input("Masukkan ticker (mis. BTC, ETH, BNB) — pisah koma jika lebih dari satu:", "BTC")
tickers = [t.strip().upper() for t in ticker_input.split(",") if t.strip()]

col1, col2 = st.columns(2)
with col1:
    start_date = st.date_input("Tanggal mulai", date.today().replace(year=date.today().year - 1))
with col2:
    end_date = st.date_input("Tanggal akhir", date.today())

if start_date >= end_date:
    st.error("Tanggal mulai harus sebelum tanggal akhir.")
    st.stop()

if not tickers:
    st.info("Masukkan setidaknya 1 ticker (mis. BTC).")
    st.stop()

if len(tickers) > 1:
    st.warning("Alpha Vantage free tier: 5 request/menit. Masukkan sedikit ticker atau tunggu antar request untuk menghindari rate limit.")

# === caching fetch supaya tidak berulang-ulang ===
@st.cache_data(ttl=60*60)  # cache 1 jam
def fetch_alpha_vantage_symbol(symbol: str, apikey: str):
    params = {
        "function": "DIGITAL_CURRENCY_DAILY",
        "symbol": symbol,
        "market": "USD",
        "apikey": apikey
    }
    r = requests.get(BASE_URL, params=params, timeout=30)
    return r.status_code, r.json()

# helper: pilih key yg mengandung field (prefer USD)
def pick_value_from_values(values: dict, field: str):
    # field: 'open','high','low','close','volume'
    keys = [k for k in values.keys() if field in k.lower()]
    # prefer keys containing '(usd)'
    usd_keys = [k for k in keys if '(usd)' in k.lower()]
    use_key = None
    if usd_keys:
        use_key = usd_keys[0]
    elif keys:
        use_key = keys[0]
    else:
        # for volume, sometimes named "5. volume"
        vol_keys = [k for k in values.keys() if 'volume' in k.lower()]
        use_key = vol_keys[0] if vol_keys else None

    if use_key is None:
        return 0.0
    try:
        return float(values.get(use_key, 0))
    except Exception:
        # if value not convertible, return 0
        try:
            return float(str(values.get(use_key, "0")).replace(",", ""))
        except Exception:
            return 0.0

# === main loop: ambil & tampilkan ===
for ticker in tickers:
    with st.spinner(f"Mengambil data {ticker} dari Alpha Vantage..."):
        status, payload = fetch_alpha_vantage_symbol(ticker, API_KEY)

    # cek error response
    if status != 200:
        st.error(f"Gagal memanggil Alpha Vantage (HTTP {status}) untuk {ticker}. Coba lagi nanti.")
        continue

    # handle note / error (rate limit, invalid API key, etc)
    if "Note" in payload:
        st.error(f"Rate limit/Info dari Alpha Vantage: {payload.get('Note')}")
        continue
    if "Error Message" in payload:
        st.error(f"Error dari Alpha Vantage untuk {ticker}: {payload.get('Error Message')}")
        continue
    if "Time Series (Digital Currency Daily)" not in payload:
        st.error(f"Tidak ada data historis (digital currency daily) untuk {ticker}. Response keys: {list(payload.keys())}")
        continue

    ts = payload["Time Series (Digital Currency Daily)"]
    records = []
    for dt_str, values in ts.items():
        # ambil nilai dengan prefer USD (jika ada)
        o = pick_value_from_values(values, "open")
        h = pick_value_from_values(values, "high")
        l = pick_value_from_values(values, "low")
        c = pick_value_from_values(values, "close")
        v = pick_value_from_values(values, "volume")
        records.append({
            "Date": dt_str,
            "Open": o,
            "High": h,
            "Low": l,
            "Close": c,
            "Volume": v
        })

    df = pd.DataFrame(records)
    if df.empty:
        st.warning(f"Tidak ada data yang bisa diparsing untuk {ticker}.")
        continue

    # convert & sort & filter by date inputs
    df["Date"] = pd.to_datetime(df["Date"])
    df = df.sort_values("Date").reset_index(drop=True)
    mask = (df["Date"].dt.date >= start_date) & (df["Date"].dt.date <= end_date)
    df = df.loc[mask].reset_index(drop=True)

    if df.empty:
        st.warning(f"Tidak ada data untuk {ticker} pada rentang tanggal {start_date} s/d {end_date}.")
        continue

    # tampilkan
    st.subheader(f"{ticker} — data {start_date} s/d {end_date}")
    st.dataframe(df.tail(20))

    # chart close price (jika tersedia)
    if "Close" in df.columns and df["Close"].notna().any():
        fig = px.line(df, x="Date", y="Close", title=f"{ticker} Closing Price (USD)",
                      labels={"Close": "Close (USD)"}, template="plotly_dark")
        fig.update_traces(line=dict(width=2.5))
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning(f"Tidak ada kolom Close untuk {ticker}.")

    # download CSV
    csv_buf = StringIO()
    df.to_csv(csv_buf, index=False)
    csv_data = csv_buf.getvalue()
    st.download_button(f"⬇️ Download {ticker} CSV", data=csv_data, file_name=f"{ticker}_data.csv", mime="text/csv")
