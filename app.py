import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="Stock Financial Dashboard", layout="wide")

st.title("Stock Info & Financial Statements Tool")

# ---------------- USER INPUT ----------------
col1, col2, col3 = st.columns(3)

with col1:
    ticker_input = st.text_input("Enter Stock Ticker", value="AAPL")

with col2:
    period = st.selectbox(
        "Select Duration",
        ["1mo", "3mo", "6mo", "1y", "2y", "5y","10y", "max"],
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

# ---------------- LOAD DATA ----------------
ticker = yf.Ticker(ticker_input)

# Price Data
price_data = yf.download(ticker_input, period=period)

# Financial Statements
if statement_type == "Annual":
    balance_sheet = ticker.balance_sheet.T
    income_statement = ticker.financials.T
    cash_flow = ticker.cashflow.T
else:
    balance_sheet = ticker.quarterly_balance_sheet.T
    income_statement = ticker.quarterly_financials.T
    cash_flow = ticker.quarterly_cashflow.T

# ---------------- COMPANY INFO ----------------
st.subheader("Company Information")

info = ticker.info
info_df = pd.DataFrame({
    "Field": [
        "Company Name",
        "Sector",
        "Industry",
        "Market Cap",
        "Current Price",
        "52 Week High",
        "52 Week Low",
        "Dividend Yield",
        "PE Ratio"
    ],
    "Value": [
        info.get("longName"),
        info.get("sector"),
        info.get("industry"),
        info.get("marketCap"),
        info.get("currentPrice"),
        info.get("fiftyTwoWeekHigh"),
        info.get("fiftyTwoWeekLow"),
        info.get("dividendYield"),
        info.get("trailingPE")
    ]
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
    st.write("### Balance Sheet")
    st.dataframe(balance_sheet)

with tab2:
    st.write("### Income Statement (P&L)")
    st.dataframe(income_statement)

with tab3:
    st.write("### Cash Flow Statement")
    st.dataframe(cash_flow)


