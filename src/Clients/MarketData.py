import os
import requests
from dotenv import load_dotenv

load_dotenv()


class MarketDataClient:
    def __init__(self):
        self.token = os.getenv("MARKETDATA_API_KEY")
        self.base_url = "https://api.marketdata.app"

        if not self.token:
            raise ValueError("MARKETDATA_API_KEY not found in .env")

        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/json"
        }

    def _get(self, endpoint, params=None):
        response = requests.get(
            f"{self.base_url}{endpoint}",
            headers=self.headers,
            params=params,
            timeout=15
        )

        if response.status_code not in (200, 203):
            raise Exception(
                f"Market Data API error {response.status_code}: "
                f"{response.text}"
            )

        return response.json()

    def get_current_quote(self, ticker):
        ticker = ticker.upper()

        return self._get(
            f"/v1/stocks/quotes/{ticker}/"
        )

    def get_historical_prices(
        self,
        ticker,
        start_date,
        end_date,
        resolution="D"
    ):
        ticker = ticker.upper()

        params = {
            "from": start_date,
            "to": end_date
        }

        return self._get(
            f"/v1/stocks/candles/{resolution}/{ticker}/",
            params=params
        )

    def get_stock_data(
        self,
        ticker,
        start_date,
        end_date
    ):
        quote = self.get_current_quote(ticker)

        history = self.get_historical_prices(
            ticker,
            start_date,
            end_date
        )

        return {
            "ticker": ticker.upper(),
            "quote": quote,
            "history": history
        }
