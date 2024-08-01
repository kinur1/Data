import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

st.title('Yahoo Finance Ticker Data Viewer')

# User input for tickers
ticker_input = st.text_input("Enter Ticker Symbols (comma-separated, e.g., TSLA, AAPL):", 'TSLA, AAPL')
tickers = [ticker.strip().upper() for ticker in ticker_input.split(',')]

# User input for date range
start_date = st.date_input("Select start date", pd.to_datetime('today') - pd.DateOffset(years=1))
end_date = st.date_input("Select end date", pd.to_datetime('today'))

# Download data for each ticker
data = {}
for ticker in tickers:
    try:
        stock_data = yf.download(ticker, start=start_date, end=end_date)
        if not stock_data.empty:
            data[ticker] = stock_data
        else:
            st.warning(f"No data found for ticker: {ticker}")
    except Exception as e:
        st.error(f"Error downloading data for ticker: {ticker}. Error: {e}")

# Display data in tables and candlestick charts
for ticker, stock_data in data.items():
    st.subheader(f'Data for {ticker}')
    st.write(stock_data)

    # Plot candlestick chart
    st.subheader(f'Candlestick Chart for {ticker}')
    fig = go.Figure(data=[go.Candlestick(x=stock_data.index,
                                         open=stock_data['Open'],
                                         high=stock_data['High'],
                                         low=stock_data['Low'],
                                         close=stock_data['Close'])])

    fig.update_layout(title=f'{ticker} Candlestick Chart',
                      xaxis_title='Date',
                      yaxis_title='Price')

    st.plotly_chart(fig)
