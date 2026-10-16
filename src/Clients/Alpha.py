import os
import requests
from dotenv import load_dotenv

load_dotenv()


class AlphaVantageClient:
    def __init__(self):
        self.api_key = os.getenv("ALPHA_VANTAGE_API_KEY")
        self.base_url = "https://www.alphavantage.co/query"

        if not self.api_key:
            raise ValueError("ALPHA_VANTAGE_API_KEY not found in .env")

    def _get(self, function, ticker):
        params = {
            "function": function,
            "symbol": ticker.upper(),
            "apikey": self.api_key
        }

        response = requests.get(self.base_url, params=params, timeout=15)

        if response.status_code != 200:
            raise Exception(
                f"Alpha Vantage API error {response.status_code}: {response.text}"
            )

        data = response.json()

        if "Error Message" in data:
            raise Exception(data["Error Message"])

        if "Note" in data:
            raise Exception(data["Note"])

        if "Information" in data:
            raise Exception(data["Information"])

        return data

    def get_company_overview(self, ticker):
        return self._get("OVERVIEW", ticker)

    def get_income_statement(self, ticker):
        return self._get("INCOME_STATEMENT", ticker)

    def get_balance_sheet(self, ticker):
        return self._get("BALANCE_SHEET", ticker)

    def get_cash_flow(self, ticker):
        return self._get("CASH_FLOW", ticker)

    def get_fundamentals(self, ticker):
        ticker = ticker.upper()

        return {
            "ticker": ticker,
            "overview": self.get_company_overview(ticker),
            "income_statement": self.get_income_statement(ticker),
            "balance_sheet": self.get_balance_sheet(ticker),
            "cash_flow": self.get_cash_flow(ticker)
        }