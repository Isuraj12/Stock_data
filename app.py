import streamlit as st
import yfinance as yf
import pandas as pd
from yfinance.exceptions import YFRateLimitError

st.set_page_config(page_title="Stock Financial Dashboard", layout="wide")
st.title("Stock Info & Financial Statements Tool")

# ---------------- USER INPUT ----------------
col1, col2, col3 = st.columns(3)

with col1:
    ticker_input = st.text_input("Enter Stock Ticker", value="AAPL")

with col2:
    period = st.selectbox(
        "Select Duration",
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

# ---------------- CACHED DATA LOADERS ----------------
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
def load_company_info(symbol):
    t = yf.Ticker(symbol)

    # SAFE FIRST (fast_info)
    fast = t.fast_info

    info_data = {
        "Company Name": None,
        "Sector": None,
        "Industry": None,
        "Market Cap": fast.get("market_cap"),
        "Current Price": fast.get("last_price"),
        "52 Week High": fast.get("year_high"),
        "52 Week Low": fast.get("year_low"),
        "Dividend Yield": None,
        "PE Ratio": None,
    }

    # OPTIONAL: Try full info (may rate-limit)
    try:
        info = t.info
        info_data.update({
            "Company Name": info.get("longName"),
            "Sector": info.get("sector"),
            "Industry": info.get("industry"),
            "Dividend Yield": info.get("dividendYield"),
            "PE Ratio": info.get("trailingPE"),
        })
    except YFRateLimitError:
        pass  # silently ignore rate limit

    return info_data

# ---------------- LOAD DATA ----------------
price_data = load_price(ticker_input, period)
balance_sheet, income_statement, cash_flow = load_financials(ticker_input, statement_type)
company_info = load_company_info(ticker_input)

# ---------------- COMPANY INFO ----------------
st.subheader("Company Information")

info_df = pd.DataFrame({
    "Field": company_info.keys(),
    "Value": company_info.values()
})

st.table(info_df)

# ---------------- PRICE CHART ----------------
st.subheader("Stock Price")
st.line_chart(price_data["Close"])

with st.expander("Show Price Table"):
    st.dataframe(price_data)

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
