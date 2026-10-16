# marketcourse

## getting started 
please start a pyenv
run: 
pip install -r requirements.txt    


APis used: 


# AI Stock Education Platform

An AI-powered stock research and education platform that combines market data, company financials, and SEC filings.

## APIs

### Market Data API

Used for stock market data:

- Current stock quotes
- Historical prices
- Open, high, low, close (OHLC)
- Trading volume

This data will later be used to calculate returns, moving averages, volatility, momentum, and other market analytics.

### Alpha Vantage

Used for company fundamentals:

- Income statements
- Balance sheets
- Cash flow statements
- Company financial data

This data will later be used to calculate revenue growth, profitability, financial health, valuation metrics, and other fundamental analytics.

### SEC EDGAR

Used for official company filings:

- Company CIK lookup
- 10-K filings
- 10-Q filings
- Filing metadata
- Filing text

SEC filings will eventually be processed and stored for the educational RAG chatbot so users can ask questions about a company's filings.

## Current Structure

```text
clients/
├── marketdata_client.py
├── alpha_vantage_client.py
└── sec_client.py