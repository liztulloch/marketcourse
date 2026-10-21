from concurrent.futures import ThreadPoolExecutor, as_completed
import sys
from datetime import date, timedelta
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import pandas as pd
import requests
import streamlit as st

from src.Clients.MarketData import MarketDataClient
from src.Clients.Alpha import AlphaVantageClient
from src.Services.analytics_service import AnalyticsService
from src.Data.Popular_stocks import POPULAR_STOCKS
from src.Services.Home_view import HomeService

CHAT_API_URL = "http://127.0.0.1:8000/chat/"

STARTER_QUESTIONS = [
    "What is a P/E ratio?",
    "What does volatility mean?",
    "How do the three financial statements connect?",
    "What's the difference between the S&P 500 and the Dow?",
]

st.set_page_config(
    page_title="Market Course",
    page_icon="♡",
    layout="wide",
)

if "messages" not in st.session_state:
    st.session_state.messages = []
if "selected_ticker" not in st.session_state:
    st.session_state.selected_ticker = None


# ---------------------------------------------------------------------------
# Styling
# ---------------------------------------------------------------------------
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@500;600;700&family=Inter:wght@400;500;600&display=swap');

:root {
    --rose-900: #5b3444;
    --rose-800: #6e4354;
    --rose-700: #8f4f68;
    --rose-600: #9f526e;
    --rose-500: #b86683;
    --rose-400: #d99aae;
    --rose-300: #e7bbc9;
    --rose-200: #f3dbe4;
    --rose-100: #fdf4f7;
    --ink: #3d2932;
    --muted: #9a7885;
}

/* ---------- Base ---------- */
.stApp {
    background:
        radial-gradient(circle at 12% 8%, rgba(248, 215, 227, 0.55) 0, transparent 38%),
        radial-gradient(circle at 92% 30%, rgba(246, 225, 235, 0.7) 0, transparent 34%),
        linear-gradient(135deg, #fffafb 0%, #fdf4f7 100%);
    color: var(--ink);
    font-family: 'Inter', -apple-system, 'Segoe UI', sans-serif;
}

footer { visibility: hidden; }

.block-container {
    max-width: 1150px;
    padding-top: 2.2rem;
    padding-bottom: 3rem;
}

p, label, li { color: #5b3444; }

h1, h2, h3 {
    font-family: 'Playfair Display', Georgia, serif;
    color: var(--rose-800);
}

/* ---------- Hero ---------- */
.hero {
    position: relative;
    overflow: hidden;
    background: linear-gradient(135deg, #fbe4ec 0%, #f6d3e0 55%, #efc5d6 100%);
    border: 1px solid #f1d4df;
    border-radius: 28px;
    padding: 36px 40px 30px 40px;
    margin-bottom: 26px;
    box-shadow: 0 12px 34px rgba(121, 73, 91, 0.12);
}
.hero::after {
    content: "♡";
    position: absolute;
    right: 38px;
    top: -18px;
    font-family: Georgia, serif;
    font-size: 170px;
    color: rgba(255, 255, 255, 0.45);
    pointer-events: none;
}
.hero-title {
    font-family: 'Playfair Display', Georgia, serif;
    font-size: 46px;
    font-weight: 700;
    color: var(--rose-900);
    line-height: 1.1;
}
.hero-sub {
    color: var(--rose-700);
    font-size: 17px;
    margin-top: 8px;
}
.pill {
    display: inline-block;
    background: rgba(255, 255, 255, 0.72);
    border: 1px solid rgba(255, 255, 255, 0.9);
    border-radius: 999px;
    padding: 6px 15px;
    font-size: 13px;
    font-weight: 500;
    color: var(--rose-700);
    margin: 16px 8px 0 0;
}

/* ---------- Section headings ---------- */
.section-label {
    color: #99677a;
    font-size: 12px;
    font-weight: 600;
    letter-spacing: 2.4px;
    text-transform: uppercase;
    margin: 30px 0 6px 0;
}
.section-title {
    font-family: 'Playfair Display', Georgia, serif;
    font-size: 28px;
    font-weight: 600;
    color: var(--rose-800);
    margin: 0 0 2px 0;
}
.section-caption {
    color: var(--muted);
    font-size: 14px;
    margin-bottom: 16px;
}

/* ---------- Search form ---------- */
[data-testid="stForm"] {
    background: #ffffff;
    border: 1px solid #f1dce4;
    border-radius: 24px;
    padding: 24px 26px 18px 26px;
    box-shadow: 0 8px 26px rgba(121, 73, 91, 0.08);
}
.form-prompt {
    font-family: 'Playfair Display', Georgia, serif;
    color: var(--rose-800);
    font-size: 19px;
    font-weight: 600;
    margin-bottom: 8px;
}
.stTextInput input {
    background-color: #fff8e7;
    color: var(--ink) !important;
    border: 1px solid #e7cbd6 !important;
    border-radius: 14px !important;
    padding: 12px 14px !important;
}
.stTextInput input:focus {
    border-color: var(--rose-500) !important;
    box-shadow: 0 0 0 3px rgba(184, 102, 131, 0.15) !important;
}
.stTextInput input::placeholder { color: #b99aa6 !important; }

/* ---------- Buttons ---------- */
.stButton > button,
[data-testid="stFormSubmitButton"] button {
    background: linear-gradient(135deg, #c27590 0%, #b86683 100%);
    color: white;
    border: none;
    border-radius: 14px;
    padding: 10px 26px;
    font-weight: 600;
    transition: transform 0.15s ease, box-shadow 0.15s ease;
}
.stButton > button:hover,
[data-testid="stFormSubmitButton"] button:hover {
    background: linear-gradient(135deg, #b86683 0%, #9f526e 100%);
    color: white;
    border: none;
    transform: translateY(-1px);
    box-shadow: 0 6px 16px rgba(159, 82, 110, 0.28);
}

/* ---------- Metrics ---------- */
[data-testid="stMetric"] {
    background-color: #ffffff;
    border: 1px solid #f1dce4;
    border-radius: 20px;
    padding: 20px 22px;
    box-shadow: 0 6px 20px rgba(121, 73, 91, 0.07);
}
[data-testid="stMetricLabel"] { color: #9d7081; font-size: 14px; }
[data-testid="stMetricValue"] { color: var(--rose-900); font-weight: 600; }

/* ---------- Ticker header ---------- */
.ticker-title {
    display: inline-block;
    font-family: 'Playfair Display', Georgia, serif;
    font-size: 40px;
    font-weight: 700;
    color: var(--rose-900);
    margin: 4px 0 14px 0;
}
.ticker-title span {
    font-size: 15px;
    font-family: 'Inter', sans-serif;
    font-weight: 500;
    color: var(--rose-700);
    background: var(--rose-200);
    border-radius: 999px;
    padding: 4px 12px;
    margin-left: 12px;
    vertical-align: middle;
}

/* ---------- Popular stock cards ---------- */
.stock-card {
    background: #ffffff;
    border: 1px solid #f1dce4;
    border-radius: 22px;
    padding: 18px 18px 14px 18px;
    box-shadow: 0 6px 20px rgba(121, 73, 91, 0.07);
    transition: transform 0.18s ease, box-shadow 0.18s ease;
    margin-bottom: 16px;
    min-height: 168px;
}
.stock-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 12px 28px rgba(121, 73, 91, 0.14);
}
.stock-card.muted { background: #fffafb; border-style: dashed; }
.stock-top {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    gap: 6px;
}
.stock-ticker {
    font-family: 'Playfair Display', Georgia, serif;
    font-size: 21px;
    font-weight: 700;
    color: var(--rose-900);
}
.stock-name {
    font-size: 12px;
    color: var(--muted);
    max-width: 105px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}
.stock-price {
    font-size: 24px;
    font-weight: 600;
    color: var(--rose-900);
    margin: 10px 0 8px 0;
}
.stock-row {
    display: flex;
    justify-content: space-between;
    font-size: 12.5px;
    color: #8c6a79;
    padding: 3px 0;
    border-top: 1px dashed #f1dce4;
}
.stock-row b { color: var(--rose-800); font-weight: 600; }
.delta {
    font-size: 11.5px;
    font-weight: 600;
    border-radius: 999px;
    padding: 3px 9px;
    white-space: nowrap;
}
.delta.up { background: #eaf6ef; color: #3f8a62; }
.delta.down { background: #fdecef; color: #bf4a68; }
.unavailable { color: var(--muted); font-size: 13px; margin-top: 18px; }

/* ---------- Explanation cards ---------- */
.explanation {
    background-color: #ffffff;
    border-left: 4px solid var(--rose-400);
    border-radius: 14px;
    padding: 18px 22px;
    color: #60444f;
    margin-top: 12px;
    box-shadow: 0 4px 14px rgba(121, 73, 91, 0.05);
    line-height: 1.55;
}
.explanation b { color: var(--rose-800); font-size: 16px; }

.trend-note {
    background: var(--rose-100);
    border: 1px solid var(--rose-200);
    border-radius: 14px;
    padding: 12px 16px;
    color: #6e4354;
    font-size: 14px;
    margin-top: 12px;
}

.disclaimer {
    text-align: center;
    color: #ae8c98;
    font-size: 12px;
    margin-top: 36px;
}

/* ---------- Chat sidebar ---------- */
[data-testid="stSidebar"] {
    background: linear-gradient(
        180deg,
        #fffaf0 0%,
        #fbe9f0 100%
    );

    left: auto !important;
    right: 0 !important;

    border-right: none !important;
    border-left: 1px solid #f1d4df !important;
}
[data-testid="stSidebarCollapsedControl"] {
    left: auto !important;
    right: 1rem !important;
}
.chat-title {
    font-family: 'Playfair Display', Georgia, serif;
    color: var(--rose-700);
    font-size: 26px;
    font-weight: 700;
    line-height: 1.15;
    margin-bottom: 4px;
}
.chat-subtitle {
    color: #a47b8b;
    font-size: 13px;
    margin-bottom: 16px;
}
[data-testid="stSidebar"] [data-testid="stVerticalBlockBorderWrapper"] {
    background: rgba(255, 255, 255, 0.55);
    border: 1px solid #f1d4df;
    border-radius: 20px;
}
[data-testid="stChatMessage"] {
    background: #fffaf0;
    border: 1px solid #f3dbe4;
    border-radius: 18px;
    padding: 12px 14px;
    margin-bottom: 10px;
}
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) {
    background: #f3dce6;
    border-color: #e9c6d4;
}
[data-testid="stChatMessage"] p { color: #5b4450; font-size: 14px; }
[data-testid="stChatMessageAvatarUser"] { background: var(--rose-300); }
[data-testid="stChatMessageAvatarAssistant"] { background: var(--rose-500); }
/* Chat input outer container */
[data-testid="stChatInput"] {
    background: #fff8e7 !important;
    border: 1px solid #e7cbd6 !important;
    border-radius: 18px !important;
}

/* Inner input wrapper */
[data-testid="stChatInput"] > div {
    background: #fff8e7 !important;
    border-radius: 18px !important;
}

/* Actual typing area */
[data-testid="stChatInput"] textarea {
    background-color: #fff8e7 !important;
    color: #3d2932 !important;
    -webkit-text-fill-color: #3d2932 !important;
    caret-color: #8f4f68 !important;
}

/* Placeholder */
[data-testid="stChatInput"] textarea::placeholder {
    color: #a47b8b !important;
    -webkit-text-fill-color: #a47b8b !important;
    opacity: 1 !important;
}

/* Soft outline buttons inside the sidebar (starter questions, clear chat) */
[data-testid="stSidebar"] .stButton > button {
    background: #ffffff;
    color: var(--rose-700);
    border: 1px solid var(--rose-300);
    border-radius: 14px;
    padding: 8px 14px;
    font-weight: 500;
    font-size: 13px;
    text-align: left;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background: var(--rose-100);
    color: var(--rose-600);
    border: 1px solid var(--rose-400);
    transform: none;
    box-shadow: none;
}
</style>
""",
    unsafe_allow_html=True,
)


# ---------------------------------------------------------------------------
# Services
# ---------------------------------------------------------------------------
market_client = MarketDataClient()
alpha_client = AlphaVantageClient()
analytics = AnalyticsService()

home_service = HomeService(market_client, alpha_client, analytics)


@st.cache_data(ttl=3600)
def load_all_popular_stocks():
    results = {}

    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {
            executor.submit(
                load_popular_stock,
                stock["ticker"]
            ): stock["ticker"]
            for stock in POPULAR_STOCKS
        }

        for future in as_completed(futures):
            ticker = futures[future]

            try:
                results[ticker] = future.result()
            except Exception as error:
                print(f"Failed loading {ticker}: {error}")
                results[ticker] = None

    return results

@st.cache_data(ttl=3600, show_spinner=False)
def run_analysis(symbol):
    end_date = date.today()
    start_date = end_date - timedelta(days=365)

    history = market_client.get_historical_prices(
        symbol,
        start_date.isoformat(),
        end_date.isoformat(),
    )
    income_statement = alpha_client.get_income_statement(symbol)
    results = analytics.analyze(history, income_statement)
    return history, results


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def pct(value):
    return "N/A" if value is None else f"{value:.2f}%"


def money(value):
    return "N/A" if value is None else f"${value:,.2f}"


def volatility_label(value):
    if value is None:
        return "an unknown"
    if value < 20:
        return "relatively low"
    if value < 40:
        return "moderate"
    return "relatively high"


def extract_closes(history):
    """Best-effort: pull a closing-price series out of whatever the client returns."""
    try:
        df = pd.DataFrame(history)
        if df.empty:
            return None

        cols = {str(c).lower(): c for c in df.columns}
        close_col = next(
            (cols[k] for k in ("close", "adj close", "adj_close", "adjclose", "price") if k in cols),
            None,
        )
        if close_col is None:
            return None

        series = pd.to_numeric(df[close_col], errors="coerce")
        date_col = next(
            (cols[k] for k in ("date", "datetime", "timestamp", "time") if k in cols),
            None,
        )
        if date_col is not None:
            series.index = pd.to_datetime(df[date_col])

        series = series.dropna()
        return series if len(series) > 1 else None
    except Exception:
        return None


def section_label(text):
    st.markdown(f'<div class="section-label">{escape(text)}</div>', unsafe_allow_html=True)


def explain(title, icon, body):
    st.markdown(
        f'<div class="explanation"><b>{icon} {title}</b><br>{body}</div>',
        unsafe_allow_html=True,
    )


def stock_card(symbol, name, data):
    top = (
        f'<div class="stock-top"><div>'
        f'<div class="stock-ticker">{escape(symbol)}</div>'
        f'<div class="stock-name" title="{escape(name)}">{escape(name)}</div>'
        f'</div>'
    )

    if data is None:
        return (
            f'<div class="stock-card muted">{top}</div>'
            f'<div class="unavailable">Data unavailable right now</div></div>'
        )

    ret = data.get("return_percent")
    if ret is None:
        pill = ""
    else:
        css = "up" if ret >= 0 else "down"
        arrow = "▲" if ret >= 0 else "▼"
        pill = f'<span class="delta {css}">{arrow} {abs(ret):.2f}% 1Y</span>'

    return (
        f'<div class="stock-card">{top}{pill}</div>'
        f'<div class="stock-price">{money(data.get("current_price"))}</div>'
        f'<div class="stock-row"><span>Revenue growth</span>'
        f'<b>{pct(data.get("revenue_growth"))}</b></div>'
        f'<div class="stock-row"><span>Volatility</span>'
        f'<b>{pct(data.get("annualized_volatility"))}</b></div>'
        f'</div>'
    )


def queue_question(text):
    st.session_state.pending_question = text


def clear_chat():
    st.session_state.messages = []


def clear_results():
    st.session_state.selected_ticker = None

def ask_market_course(question):
    try:
        response = requests.post(
            CHAT_API_URL,
            json={"message": question},
            timeout=(5, 45),
        )

        response.raise_for_status()

        data = response.json()

        return data["answer"]

    except requests.Timeout:
        return "Market Course AI took too long to respond."

    except requests.ConnectionError:
        return "The Market Course API isn't running."

    except requests.HTTPError as error:
        try:
            detail = error.response.json().get("detail")
        except ValueError:
            detail = error.response.text

        return f"API error: {detail}"

    except (KeyError, ValueError) as error:
        return f"Unexpected API response: {error}"

# ---------------------------------------------------------------------------
# Analysis view
# ---------------------------------------------------------------------------
def render_analysis(symbol):
    try:
        with st.spinner(f"Studying {symbol}..."):
            history, results = run_analysis(symbol)
    except Exception as error:
        st.error(f"Sorry, we couldn't analyze {symbol}.")
        st.caption(str(error))
        return

    section_label("Snapshot")
    head_left, head_right = st.columns([5, 1])
    head_left.markdown(
        f'<div class="ticker-title">{escape(symbol)}<span>1-year view</span></div>',
        unsafe_allow_html=True,
    )
    head_right.button("Clear ✕", key="clear_results", on_click=clear_results)

    ret = results.get("return_percent")
    rev = results.get("revenue_growth")
    vol = results.get("annualized_volatility")

    col1, col2, col3 = st.columns(3)
    col1.metric(
        "♡ Historical Return",
        pct(ret),
        help="How much the price changed from the start to the end of the period.",
    )
    col2.metric(
        "✿ Revenue Growth",
        pct(rev),
        help="Change in annual revenue versus the previous annual reporting period.",
    )
    col3.metric(
        "◇ Volatility",
        pct(vol),
        help="Annualized standard deviation of returns: how much the price has swung.",
    )

    section_label("Price Trends")

    closes = extract_closes(history)
    if closes is not None:
        try:
            st.line_chart(closes, color="#b86683", height=260)
        except Exception:
            pass

    sma_50 = results.get("sma_50")
    sma_200 = results.get("sma_200")

    col4, col5 = st.columns(2)
    col4.metric("50-Day Moving Average", money(sma_50))
    col5.metric("200-Day Moving Average", money(sma_200))

    if sma_50 is not None and sma_200 is not None:
        relation = "above" if sma_50 >= sma_200 else "below"
        st.markdown(
            f'<div class="trend-note">The 50-day average is currently <b>{relation}</b> '
            f"the 200-day average. Some people watch this relationship as a rough sign of "
            f"short-term vs. long-term momentum, but it only describes the past.</div>",
            unsafe_allow_html=True,
        )

    section_label("Learn the Numbers")

    left, right = st.columns(2)

    with left:
        if ret is not None:
            direction = "increased" if ret >= 0 else "decreased"
            explain(
                "Historical Return",
                "♡",
                f"{escape(symbol)} {direction} {abs(ret):.2f}% over the period analyzed. "
                f"Return is simply the change from start to finish; it says nothing "
                f"about what comes next.",
            )

        explain(
            "Volatility",
            "◇",
            f"Annualized historical volatility is {pct(vol)}, a {volatility_label(vol)} "
            f"level of price movement. Volatility measures how much returns have varied, "
            f"not whether they went up or down.",
        )

    with right:
        if rev is not None:
            rev_direction = "grew" if rev >= 0 else "shrank"
            explain(
                "Revenue Growth",
                "✿",
                f"The company's annual revenue {rev_direction} {abs(rev):.2f}% compared "
                f"with the previous annual reporting period. Revenue is the money earned "
                f"from sales before any expenses.",
            )
        else:
            explain(
                "Revenue Growth",
                "✿",
                "Revenue growth isn't available for this company right now.",
            )

        explain(
            "Moving Averages",
            "✧",
            "A moving average smooths out daily price noise by averaging the last 50 or "
            "200 trading days. Comparing the two shows how recent prices stack up "
            "against the longer trend.",
        )

    st.caption("Curious about a term? Ask Market Course AI in the sidebar ♡")


# ---------------------------------------------------------------------------
# Page
# ---------------------------------------------------------------------------
st.markdown(
    """
<div class="hero">
    <div class="hero-title">Market Course ♡</div>
    <div class="hero-sub">Learn the market. Understand the numbers. Invest in your knowledge.</div>
    <span class="pill">✿ Research a stock</span>
    <span class="pill">◇ Learn the numbers</span>
    <span class="pill">♡ Ask Market Course AI</span>
</div>
""".replace("\n    ", "").replace("\n", ""),
    unsafe_allow_html=True,
)

# --- Stock research (search sits above the popular stocks) ---
section_label("Stock Research")

with st.form("search_form", clear_on_submit=False):
    st.markdown(
        '<div class="form-prompt">Which stock are we learning about today?</div>',
        unsafe_allow_html=True,
    )
    input_col, button_col = st.columns([5, 1.4])
    raw_ticker = input_col.text_input(
        "Ticker symbol",
        placeholder="Try AAPL, MSFT, NVDA...",
        label_visibility="collapsed",
    )
    submitted = button_col.form_submit_button("Explore ♡")

if submitted:
    symbol = raw_ticker.strip().upper()
    if symbol:
        st.session_state.selected_ticker = symbol
    else:
        st.warning("Type a ticker symbol first ♡")

if st.session_state.selected_ticker:
    render_analysis(st.session_state.selected_ticker)

# --- Popular stocks ---
section_label("Popular Stocks")
st.markdown('<div class="section-title">Popular picks ♡</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="section-caption">A quick look at some well-known stocks. Updated hourly.</div>',
    unsafe_allow_html=True,
)

CARDS_PER_ROW = 5
for start in range(0, len(POPULAR_STOCKS), CARDS_PER_ROW):
    row = POPULAR_STOCKS[start:start + CARDS_PER_ROW]
    cols = st.columns(CARDS_PER_ROW)

    for col, stock in zip(cols, row):
        with col:
            try:
                data = load_popular_stock(stock["ticker"])
            except Exception:
                data = None
            st.markdown(
                stock_card(stock["ticker"], stock["name"], data),
                unsafe_allow_html=True,
            )

st.markdown(
    '<div class="disclaimer">Market Course ♡ Educational purposes only. Not investment advice.</div>',
    unsafe_allow_html=True,
)


# ---------------------------------------------------------------------------
# Chat sidebar
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown(
        '<div class="chat-title">Market Course AI ♡</div>'
        '<div class="chat-subtitle">Ask questions about stocks, investing, and financial concepts.</div>',
        unsafe_allow_html=True,
    )

    chat_box = st.container(height=440)

    with chat_box:
        if not st.session_state.messages:
            with st.chat_message("assistant"):
                st.write(
                    "Hi, I'm your Market Course guide ♡ Ask me about valuation, "
                    "financial statements, risk, portfolios, or stock indexes."
                )
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.write(message["content"])

    starter_slot = st.empty()
    if not st.session_state.messages:
        with starter_slot.container():
            st.caption("Try asking:")
            for i, text in enumerate(STARTER_QUESTIONS):
                st.button(text, key=f"starter_{i}", on_click=queue_question, args=(text,))

    question = st.chat_input("Ask about the market...")
    if not question:
        question = st.session_state.pop("pending_question", None)

    if question:
        starter_slot.empty()
        st.session_state.messages.append({"role": "user", "content": question})

        with chat_box:
            with st.chat_message("user"):
                st.write(question)
            with st.chat_message("assistant"):
                with st.spinner("Thinking ♡"):
                    answer = ask_market_course(question)
                st.write(answer)

        st.session_state.messages.append({"role": "assistant", "content": answer})

    if st.session_state.messages:
        st.button("Clear chat", key="clear_chat", on_click=clear_chat)