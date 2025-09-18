import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px
from io import StringIO

st.title('Yahoo Finance Ticker Data Viewer')

# User input for tickers
ticker_input = st.text_input("Masukan Ticker (Seperti BTC-USD, BNB-USD):", 'BTC-USD, BNB-USD')
tickers = [ticker.strip().upper() for ticker in ticker_input.split(',') if ticker.strip()]

# User input for date range
default_start = pd.to_datetime('today') - pd.DateOffset(years=1)
default_end = pd.to_datetime('today')

start_date = st.date_input("Select start date", default_start)
end_date = st.date_input("Select end date", default_end)

if pd.to_datetime(start_date) >= pd.to_datetime(end_date):
    st.error("Tanggal akhir harus lebih besar dari tanggal mulai.")
    st.stop()

# Helper: flatten MultiIndex columns -> strings
def flatten_columns(columns):
    flat = []
    for col in columns:
        if isinstance(col, tuple):
            parts = [str(c) for c in col if c not in ("", None)]
            flat.append("_".join(parts) if parts else "")
        else:
            flat.append(str(col))
    return flat

# Helper: prepare DF for plotting, return (df_flattened, y_col)
def prepare_df_for_plot(df, ticker):
    df_reset = df.reset_index()

    # Flatten MultiIndex columns (including ('Date',''))
    if isinstance(df_reset.columns, pd.MultiIndex):
        df_reset.columns = flatten_columns(df_reset.columns)
    else:
        df_reset.columns = [str(c) for c in df_reset.columns]

    # Pastikan kolom 'Date' ada (kadang hasil reset index = 'index')
    if 'Date' not in df_reset.columns and 'index' in df_reset.columns:
        df_reset = df_reset.rename(columns={'index': 'Date'})

    # Cari kandidat kolom y untuk Close
    candidates = [
        f'Close_{ticker}',    # format jika MultiIndex diflatten jadi Close_TICKER
        'Close',              # format single-ticker
        f'Adj Close_{ticker}',
        'Adj Close'
    ]
    y_col = next((c for c in candidates if c in df_reset.columns), None)
    return df_reset, y_col

# Download data untuk tiap ticker
data = {}
for ticker in tickers:
    try:
        stock_data = yf.download(
            ticker,
            start=pd.to_datetime(start_date),
            end=pd.to_datetime(end_date),
            progress=False,
            group_by="column",  # konsistenkan orientasi MultiIndex
            auto_adjust=False
        )
        if not stock_data.empty:
            data[ticker] = stock_data
        else:
            st.warning(f"No data found for ticker: {ticker}")
    except Exception as e:
        st.error(f"Error downloading data for ticker: {ticker}. Error: {e}")

# Tampilkan table, chart, dan tombol unduh
for ticker, stock_data in data.items():
    st.subheader(f'Data for {ticker}')
    df_plot, y_col = prepare_df_for_plot(stock_data, ticker)

    # Tampilkan tabel yang sudah rapi (kolom flatten)
    st.dataframe(df_plot)

    if y_col is None:
        st.warning(f"Kolom harga penutupan untuk {ticker} tidak ditemukan.")
        continue

    # Plot line chart
    st.subheader(f'Enhanced Line Chart for {ticker}')
    fig = px.line(
        df_plot,
        x="Date",
        y=y_col,
        title=f"{ticker} Close Price",
        labels={y_col: "Close Price", "Date": "Date"},
        color_discrete_sequence=px.colors.sequential.Viridis
    )
    fig.update_traces(line=dict(width=2.5))
    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Close Price",
        template="plotly_dark",
        title=dict(text=f"{ticker} Closing Prices", font=dict(size=20, color="white"), x=0.5),
        xaxis=dict(showline=True, showgrid=False, linecolor="white"),
        yaxis=dict(showline=True, showgrid=True, gridcolor="gray", linecolor="white"),
    )
    st.plotly_chart(fig, use_container_width=True)

    # Download CSV pakai df_plot (kolom sudah rata)
    csv_buffer = StringIO()
    df_plot.to_csv(csv_buffer, index=False)
    csv_data = csv_buffer.getvalue()

    st.download_button(
        label=f"Download {ticker} data as CSV",
        data=csv_data,
        file_name=f"{ticker}_data.csv",
        mime="text/csv"
    )
