import streamlit as st
import yfinance as yf
import pandas as pd
from yfinance.exceptions import YFRateLimitError

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Stock Financial Dashboard",
    layout="wide"
)

st.title("📈 Stock Info & Financial Statements Tool")

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
def load_company_info(symbol):
    t = yf.Ticker(symbol)

    data = {
        "Company Name": "Not Available",
        "Sector": "Not Available",
        "Industry": "Not Available",
        "Market Cap": "Not Available",
        "Current Price": "Not Available",
        "52 Week High": "Not Available",
        "52 Week Low": "Not Available",
        "Dividend Yield": "Not Available",
        "PE Ratio": "Not Available",
    }

    # ---------- FAST INFO (SAFE) ----------
    try:
        fast = t.fast_info
        data["Market Cap"] = fast.get("market_cap")
        data["Current Price"] = fast.get("last_price")
        data["52 Week High"] = fast.get("year_high")
        data["52 Week Low"] = fast.get("year_low")
    except Exception:
        pass

    # ---------- FULL INFO (MAY RATE LIMIT) ----------
    try:
        info = t.info
        data["Company Name"] = info.get("longName", data["Company Name"])
        data["Sector"] = info.get("sector", data["Sector"])
        data["Industry"] = info.get("industry", data["Industry"])
        data["Dividend Yield"] = info.get("dividendYield", data["Dividend Yield"])
        data["PE Ratio"] = info.get("trailingPE", data["PE Ratio"])
    except YFRateLimitError:
        pass
    except Exception:
        pass

    return data

# ---------------- LOAD DATA ----------------
with st.spinner("Fetching stock data..."):
    price_data = load_price(ticker_input, period)
    balance_sheet, income_statement, cash_flow = load_financials(
        ticker_input, statement_type
    )
    company_info = load_company_info(ticker_input)

# ---------------- COMPANY INFO ----------------
st.subheader("🏢 Company Information")

info_df = pd.DataFrame({
    "Field": company_info.keys(),
    "Value": company_info.values()
})

st.table(info_df)

if company_info["Company Name"] == "Not Available":
    st.info("Some company details may be temporarily unavailable due to Yahoo Finance limits.")

# ---------------- PRICE CHART ----------------
st.subheader("📊 Stock Price")

if not price_data.empty:
    st.line_chart(price_data["Close"])
else:
    st.warning("No price data available.")

with st.expander("Show Price Table"):
    st.dataframe(price_data)

# ---------------- FINANCIAL STATEMENTS ----------------
st.subheader("📄 Financial Statements")

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
