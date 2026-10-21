

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
import streamlit as st
from datetime import date, timedelta
import requests
    
from src.Clients.MarketData import MarketDataClient
from src.Clients.Alpha import AlphaVantageClient
from src.Services.analytics_service import AnalyticsService
from src.Data.Popular_stocks import POPULAR_STOCKS
from src.Services.Home_view import HomeService
if "messages" not in st.session_state:
    st.session_state.messages = []


st.set_page_config(
    page_title="Market Course",
    page_icon="♡",
    layout="wide"
)
st.markdown("""
<style>
/* Chat panel */
.chat-title {
    color: #8f4f68;
    font-size: 24px;
    font-weight: 700;
    margin-bottom: 2px;
}

.chat-subtitle {
    color: #a47b8b;
    font-size: 13px;
    margin-bottom: 18px;
}

.chat-answer {
    background: #fff5f8;
    border: 1px solid #f3dbe4;
    border-radius: 16px;
    padding: 12px 14px;
    margin: 8px 0;
    color: #5b4450;
}

.chat-user {
    background: #ead1dc;
    border-radius: 16px;
    padding: 12px 14px;
    margin: 8px 0;
    color: #543b46;
}

/* Make buttons softer */
.stButton > button {
    border-radius: 14px;
    border: 1px solid #e7bbc9;
}
</style>
""", unsafe_allow_html=True)


st.markdown("""
<style>.stApp {
    background: linear-gradient(135deg, #fffafb 0%, #fdf4f7 100%);
    color: #3d2932;
}

p, label {
    color: #5b3444;
}
.block-container {
    max-width: 1100px;
    padding-top: 3rem;
}

h1 {
    color: #5b3444;
    font-family: Georgia, serif;
}

h2, h3 {
    color: #6e4354;
}

[data-testid="stMetric"] {
    background-color: #ffffff;
    border: 1px solid #f1dce4;
    border-radius: 18px;
    padding: 22px;
    box-shadow: 0 5px 18px rgba(121, 73, 91, 0.06);
}

[data-testid="stMetricLabel"] {
    color: #9d7081;
    font-size: 14px;
}

[data-testid="stMetricValue"] {
    color: #5b3444;
    font-weight: 600;
}.stTextInput input {
    background-color: #ffffff !important;
    color: #3d2932 !important;
    border: 1px solid #e7cbd6 !important;
    border-radius: 14px !important;
    padding: 12px !important;
}

.stTextInput input::placeholder {
    color: #b99aa6 !important;
}

.stTextInput label {
    color: #5b3444 !important;
}
.stButton > button {
    background: #b86683;
    color: white;
    border: none;
    border-radius: 14px;
    padding: 10px 28px;
    font-weight: 600;
}

.stButton > button:hover {
    background: #9f526e;
    color: white;
    border: none;
}

.subtitle {
    color: #9a7885;
    font-size: 17px;
    margin-top: -12px;
    margin-bottom: 30px;
}

.section-label {
    color: #99677a;
    font-size: 13px;
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-top: 25px;
}

.explanation {
    background-color: #fff;
    border-left: 4px solid #d99aae;
    border-radius: 12px;
    padding: 18px 22px;
    color: #60444f;
    margin-top: 10px;
}
</style>
""", unsafe_allow_html=True)


market_client = MarketDataClient()
alpha_client = AlphaVantageClient()
analytics = AnalyticsService()

home_service = HomeService(
    market_client,
    alpha_client,
    analytics
)
@st.cache_data(ttl=3600)
def load_popular_stock(ticker):
    return home_service.get_stock_summary(ticker)

st.title("Market Course ♡")
@st.cache_data(ttl=3600)
def load_popular_stock(ticker):
    return home_service.get_stock_summary(ticker)

st.markdown(
    '<p class="subtitle">'
    'Learn the market. Understand the numbers. Invest in your knowledge.'
    '</p>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="section-label">Stock Research</div>',
    unsafe_allow_html=True
)

ticker = st.text_input(
    "Which stock are we learning about today?",
    placeholder="Try AAPL, MSFT, NVDA..."
).strip().upper()

analyze = st.button("Explore Stock ♡")
st.markdown(
    '<div class="section-label">Popular Stocks</div>',
    unsafe_allow_html=True
)

st.subheader("Popular picks ♡")
st.caption("A quick look at some well-known stocks.")

cols = st.columns(5)

for i, stock in enumerate(POPULAR_STOCKS):
    ticker = stock["ticker"]
    name = stock["name"]

    with cols[i % 5]:
        try:
            data = load_popular_stock(ticker)

            st.markdown(f"### {ticker}")
            st.caption(name)
            st.metric(
                label="Current Price",
                value=f"${data['current_price']:.2f}",
                delta=f"{data['return_percent']:.2f}% 1Y"
            )
            st.write(
                f"Revenue growth: "
                f"**{data['revenue_growth']:.2f}%**"
            )

            st.write(
                f"Volatility: "
                f"**{data['annualized_volatility']:.2f}%**"
            )
        except Exception as error:
            st.markdown(f"### {ticker}")
            st.caption(stock["name"])
            st.write("Data unavailable")
            st.caption(str(error))

if analyze and ticker:
    try:
        with st.spinner(f"Studying {ticker}..."):
            end_date = date.today()
            start_date = end_date - timedelta(days=365)

            history = market_client.get_historical_prices(
                ticker,
                start_date.isoformat(),
                end_date.isoformat()
            )

            income_statement = alpha_client.get_income_statement(ticker)

            results = analytics.analyze(
                history,
                income_statement
            )

        st.markdown(
            f'<div class="section-label">Snapshot</div>',
            unsafe_allow_html=True
        )

        st.header(ticker)

        col1, col2, col3 = st.columns(3)

        col1.metric(
            "♡ Historical Return",
            f"{results['return_percent']:.2f}%"
        )

        col2.metric(
            "✿ Revenue Growth",
            f"{results['revenue_growth']:.2f}%"
        )

        col3.metric(
            "◇ Volatility",
            f"{results['annualized_volatility']:.2f}%"
        )

        st.markdown(
            '<div class="section-label">Price Trends</div>',
            unsafe_allow_html=True
        )

        col4, col5 = st.columns(2)

        col4.metric(
            "50-Day Moving Average",
            f"${results['sma_50']:.2f}"
        )

        col5.metric(
            "200-Day Moving Average",
            f"${results['sma_200']:.2f}"
        )

        st.markdown(
            '<div class="section-label">Learn the Numbers</div>',
            unsafe_allow_html=True
        )

        return_direction = (
            "increased"
            if results["return_percent"] >= 0
            else "decreased"
        )

        st.markdown(
            f"""
            <div class="explanation">
                <b>Historical Return ♡</b><br>
                {ticker} {return_direction}
                {abs(results["return_percent"]):.2f}% over the
                historical period analyzed.
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown(
            f"""
            <div class="explanation">
                <b>Revenue Growth ✿</b><br>
                The company's annual revenue changed
                {results["revenue_growth"]:.2f}% compared with
                the previous annual reporting period.
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown(
            f"""
            <div class="explanation">
                <b>Volatility ◇</b><br>
                Annualized historical volatility for the analyzed
                price data is {results["annualized_volatility"]:.2f}%.
                Volatility measures how much returns have varied.
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown(
            """
            <br>
            <p style="
                text-align:center;
                color:#ae8c98;
                font-size:12px;
            ">
                Market Course ♡ Educational purposes only.
                Not investment advice.
            </p>
            """,
            unsafe_allow_html=True
        )

    except Exception as error:
        st.error(f"Sorry, we couldn't analyze {ticker}.")
        st.caption(str(error))

with st.sidebar:
    st.title("✨ Market Course AI")

    st.caption("Ask questions about stocks, investing, and financial concepts.")

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    question = st.chat_input("Ask about the market...")

    if question:
        st.session_state.messages.append({
            "role": "user",
            "content": question
        })

        with st.chat_message("user"):
            st.write(question)

        try:
            response = requests.post(
                "http://127.0.0.1:8000/chat/",
                json={"message": question},
                timeout=60
            )

            response.raise_for_status()

            answer = response.json()["answer"]

        except requests.RequestException:
            answer = "I couldn't reach the Market Course API."

        st.session_state.messages.append({
            "role": "assistant",
            "content": answer
        })

        with st.chat_message("assistant"):
            st.write(answer)