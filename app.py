import streamlit as st
import yfinance as yf
import pandas as pd
from yfinance.exceptions import YFRateLimitError

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Stock Financial Dashboard",
    layout="wide"
)

st.title("Stock Info & Financial Statements Tool")

# ---------------- USER INPUT ----------------
col1, col2, col3 = st.columns(3)

with col1:
    ticker_input = st.text_input("Enter Stock Ticker", value="AAPL")

with col2:
    period = st.selectbox(
        "Select Price Duration",
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

@st.cache_data(ttl=3600)
def load_basic_info(symbol):
    t = yf.Ticker(symbol)

    company_name = symbol
    current_price = "Not Available"

    # ---- FAST INFO (SAFE) ----
    try:
        fast = t.fast_info
        current_price = fast.get("last_price", current_price)
    except Exception:
        pass

    # ---- FULL INFO (OPTIONAL) ----
    try:
        info = t.info
        company_name = info.get("longName", company_name)
    except Exception:
        pass

    return company_name, current_price

# ---------------- LOAD DATA ----------------
with st.spinner("Fetching stock data..."):
    price_data = load_price(ticker_input, period)
    balance_sheet, income_statement, cash_flow = load_financials(
        ticker_input, statement_type
    )
    company_name, current_price = load_basic_info(ticker_input)

# ---------------- BASIC STOCK INFO ----------------
st.subheader("Company Overview")

col_a, col_b = st.columns(2)

with col_a:
    st.metric(
        label="Company Name",
        value=company_name
    )

with col_b:
    st.metric(
        label="Current / Last Closing Price",
        value=current_price
    )

# ---------------- PRICE CHART ----------------
st.subheader("Stock Price")

if not price_data.empty:
    st.line_chart(price_data["Close"])
else:
    st.warning("No price data available.")

with st.expander("Show Price Table"):
    st.dataframe(price_data)

# ---------------- FINANCIAL STATEMENTS ----------------
st.subheader(" Financial Statements")

tab1, tab2, tab3 = st.tabs(
    ["Balance Sheet", "Income Statement", "Cash Flow"]
)

with tab1:
    st.dataframe(balance_sheet)

with tab2:
    st.dataframe(income_statement)

with tab3:
    st.dataframe(cash_flow)

# ---------------- FOOTER ----------------
st.caption("Data source: Yahoo Finance (via yfinance)")
