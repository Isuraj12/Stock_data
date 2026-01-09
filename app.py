import streamlit as st
import yfinance as yf
import pandas as pd

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Stock Financial Statements Tool",
    layout="wide"
)

st.title("Stock Financial Statements Tool")

# ---------------- USER INPUT ----------------
col1, col2, col3 = st.columns(3)

with col1:
    ticker_input = st.text_input("Enter Stock Ticker", value="AAPL")

with col2:
    period = st.selectbox(
        "Select Price Duration (Table Only)",
        ["1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "max"],
        index=3
    )

with col3:
    statement_type = st.selectbox(
        "Financial Statement Type",
        ["Annual", "Quarterly"]
    )

if not ticker_input:
    st.warning("Please enter a stock ticker.")
    st.stop()

# ---------------- CACHED LOADERS ----------------
@st.cache_data(ttl=1800)
def load_price(symbol, period):
    return yf.download(symbol, period=period)

@st.cache_data(ttl=1800)
def load_financials(symbol, statement_type):
    t = yf.Ticker(symbol)
    if statement_type == "Annual":
        return (
            t.balance_sheet.T,
            t.financials.T,
            t.cashflow.T
        )
    else:
        return (
            t.quarterly_balance_sheet.T,
            t.quarterly_financials.T,
            t.quarterly_cashflow.T
        )

# ---------------- LOAD DATA ----------------
with st.spinner("Fetching data..."):
    price_data = load_price(ticker_input, period)
    balance_sheet, income_statement, cash_flow = load_financials(
        ticker_input, statement_type
    )

# ---------------- PRICE DATA TABLE ONLY ----------------
st.subheader("Stock Price Data")

if not price_data.empty:
    st.dataframe(price_data)
else:
    st.warning("No price data available.")

# ---------------- FINANCIAL STATEMENTS ----------------
st.subheader("Financial Statements")

tab1, tab2, tab3 = st.tabs(
    ["Balance Sheet", "Income Statement", "Cash Flow"]
)

with tab1:
    st.dataframe(balance_sheet)

with tab2:
    st.dataframe(income_statement)

with tab3:
    st.dataframe(cash_flow)


