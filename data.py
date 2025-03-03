import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px
from io import StringIO

st.title('Yahoo Finance Ticker Data Viewer')

# User input for tickers
ticker_input = st.text_input("Masukan Ticker (Seperti BTC-USD, BNB-USD):", 'BTC-USD, BNB-USD')
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

# Display data in tables and enhanced line charts
for ticker, stock_data in data.items():
    st.subheader(f'Data for {ticker}')
    st.write(stock_data)

    # Plot enhanced line chart with color gradient
    st.subheader(f'Enhanced Line Chart for {ticker}')
    fig = px.line(stock_data, x=stock_data.index, y='Close', title=f'{ticker} Close Price',
                  labels={'Close': 'Close Price', 'index': 'Date'},
                  color_discrete_sequence=px.colors.sequential.Viridis)

    # Customize layout for better visuals
    fig.update_traces(line=dict(width=2.5))  # Adjust line width
    fig.update_layout(
        xaxis_title='Date',
        yaxis_title='Close Price',
        template='plotly_dark',  # Dark background for contrast
        title=dict(
            text=f'{ticker} Closing Prices',
            font=dict(size=20, color='white'),
            x=0.5  # Center title
        ),
        xaxis=dict(
            showline=True, showgrid=False, linecolor='white'
        ),
        yaxis=dict(
            showline=True, showgrid=True, gridcolor='gray', linecolor='white'
        )
    )

    st.plotly_chart(fig)

    # Save data to CSV for download
    csv_buffer = StringIO()
    stock_data.to_csv(csv_buffer)
    csv_data = csv_buffer.getvalue()

    # Create download button
    st.download_button(
        label=f"Download {ticker} data as CSV",
        data=csv_data,
        file_name=f"{ticker}_data.csv",
        mime="text/csv"
    )
