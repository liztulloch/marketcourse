# Market Course ♡

Market Course is an educational stock-market research application designed to make financial data and investing concepts easier to understand.

The application combines live market data, financial analytics, SEC/company data, and a retrieval-based AI chatbot in an interactive Streamlit interface backed by FastAPI.

> Market Course is designed for educational purposes only and does not provide investment advice.

---

## Features

### Stock Research

Search for a stock by ticker symbol and view a simplified snapshot of its recent performance.

Current analytics include:

- Current stock price
- Historical return
- Revenue growth
- Annualized volatility
- 50-day simple moving average
- 200-day simple moving average
- Historical price visualization

The goal is not only to display financial metrics, but also to explain what those numbers mean.

### Popular Stocks Dashboard

The homepage displays a collection of popular stocks with quick-access metrics such as:

- Current price
- Historical return
- Revenue growth
- Volatility

Market Course caches stock data to reduce unnecessary API requests.

### Market Course AI

Market Course includes an educational AI assistant powered by Google Gemini.

The chatbot uses a custom stock-market knowledge base and a lightweight RAG-style retrieval pipeline.

Instead of sending the entire knowledge base to the model for every question, the application:

1. Loads educational `.txt` files from the knowledge base.
2. Splits the documents into smaller chunks.
3. Compares the user's question with those chunks.
4. Retrieves the most relevant sections.
5. Sends only the selected context and question to Gemini.
6. Returns an educational response based on the retrieved material.

Example questions:

- What is a P/E ratio?
- What does volatility mean?
- What's the difference between the S&P 500 and the Dow?
- What is a 10-K?
- What's the difference between revenue and earnings?
- Why can a stock fall after beating earnings?
- How do the three financial statements connect?

### Educational Knowledge Base

The RAG chatbot is supported by a growing stock-market education knowledge base.

Topics currently include areas such as:

- Stock market fundamentals
- Financial statements
- Growth and profitability
- Stock valuation
- Risk and return
- Portfolio fundamentals
- Stock market indexes
- Earnings and earnings reports
- SEC filings and EDGAR

The knowledge base is designed around plain-English explanations, examples, related terminology, common misconceptions, and common questions.

---

## Tech Stack

### Backend

- Python
- FastAPI
- Pydantic
- Google Gemini API

### Frontend

- Streamlit
- Pandas

### Financial Data

- Market Data API
- Alpha Vantage
- SEC EDGAR

### AI / RAG

- Google Gemini
- Custom knowledge-base chunking
- Keyword-based retrieval
- Context-grounded prompt generation

---

## Project Architecture