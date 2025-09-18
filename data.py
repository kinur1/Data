import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from io import StringIO
from datetime import datetime, timedelta

st.title('📊 Cryptocurrency Data Viewer (CoinMarketCap API)')

API_KEY = "14bd8091-fe61-4ddb-8942-35818a4360d2"
BASE_URL = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/historical"

# User input for tickers
ticker_input = st.text_input("Masukan Ticker (Seperti BTC, BNB):", 'BTC, BNB')
tickers = [ticker.strip().upper() for ticker in ticker_input.split(',')]

# User input for date range
start_date = st.date_input("Select start date", datetime.today() - timedelta(days=365))
end_date = st.date_input("Select end date", datetime.today())

headers = {
    "Accepts": "application/json",
    "X-CMC_PRO_API_KEY": API_KEY,
}

data = {}

for ticker in tickers:
    try:
        params = {
            "symbol": ticker,
            "time_start": int(datetime.combine(start_date, datetime.min.time()).timestamp()),
            "time_end": int(datetime.combine(end_date, datetime.min.time()).timestamp()),
            "interval": "1d",  # daily data
            "convert": "USD"
        }
        response = requests.get(BASE_URL, headers=headers, params=params)
        json_data = response.json()

        if "data" in json_data and "quotes" in json_data["data"]:
            quotes = json_data["data"]["quotes"]
            df = pd.DataFrame([{
                "Date": q["timestamp"][:10],
                "Open": q["quote"]["USD"]["open"],
                "High": q["quote"]["USD"]["high"],
                "Low": q["quote"]["USD"]["low"],
                "Close": q["quote"]["USD"]["close"],
                "Volume": q["quote"]["USD"]["volume"]
            } for q in quotes])

            df["Date"] = pd.to_datetime(df["Date"])
            data[ticker] = df
        else:
            st.warning(f"Tidak ada data untuk {ticker} pada rentang tanggal tersebut.")

    except Exception as e:
        st.error(f"Error mengambil data {ticker}: {e}")

# Tampilkan data + grafik
for ticker, df in data.items():
    st.subheader(f'Data untuk {ticker}')
    st.write(df)

    # Plot line chart harga penutupan
    st.subheader(f'Grafik Harga Penutupan {ticker}')
    fig = px.line(df, x="Date", y="Close", title=f'{ticker} Close Price',
                  labels={'Close': 'Close Price', 'Date': 'Date'},
                  color_discrete_sequence=px.colors.sequential.Viridis)

    fig.update_traces(line=dict(width=2.5))
    fig.update_layout(
        xaxis_title='Date',
        yaxis_title='Close Price (USD)',
        template='plotly_dark',
        title=dict(text=f'{ticker} Closing Prices', font=dict(size=20, color='white'), x=0.5),
        xaxis=dict(showline=True, showgrid=False, linecolor='white'),
        yaxis=dict(showline=True, showgrid=True, gridcolor='gray', linecolor='white')
    )
    st.plotly_chart(fig)

    # Save CSV
    csv_buffer = StringIO()
    df.to_csv(csv_buffer, index=False)
    csv_data = csv_buffer.getvalue()

    st.download_button(
        label=f"Download {ticker} data as CSV",
        data=csv_data,
        file_name=f"{ticker}_data.csv",
        mime="text/csv"
    )
