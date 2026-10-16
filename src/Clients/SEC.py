import os
import requests
from dotenv import load_dotenv

load_dotenv()


class SECClient:
    def __init__(self):
        self.user_agent = os.getenv("SEC_USER_AGENT")
        self.data_url = "https://data.sec.gov"
        self.sec_url = "https://www.sec.gov"

        if not self.user_agent:
            raise ValueError("SEC_USER_AGENT not found in .env")

        self.headers = {
            "User-Agent": self.user_agent,
            "Accept-Encoding": "gzip, deflate"
        }

    def _get(self, url):
        response = requests.get(url, headers=self.headers, timeout=15)

        if response.status_code != 200:
            raise Exception(
                f"SEC API error {response.status_code}: {response.text}"
            )

        return response

    def get_cik(self, ticker):
        ticker = ticker.upper()
        url = f"{self.sec_url}/files/company_tickers.json"
        data = self._get(url).json()

        for company in data.values():
            if company["ticker"].upper() == ticker:
                return str(company["cik_str"]).zfill(10)

        raise ValueError(f"CIK not found for {ticker}")

    def get_submissions(self, ticker):
        cik = self.get_cik(ticker)
        url = f"{self.data_url}/submissions/CIK{cik}.json"

        return self._get(url).json()

    def get_latest_filing(self, ticker, form_type):
        ticker = ticker.upper()
        submissions = self.get_submissions(ticker)
        recent = submissions["filings"]["recent"]

        for i, form in enumerate(recent["form"]):
            if form == form_type:
                return {
                    "ticker": ticker,
                    "cik": str(submissions["cik"]),
                    "company": submissions["name"],
                    "form": form,
                    "filing_date": recent["filingDate"][i],
                    "accession_number": recent["accessionNumber"][i],
                    "primary_document": recent["primaryDocument"][i]
                }

        raise ValueError(f"No {form_type} found for {ticker}")

    def get_latest_10k(self, ticker):
        return self.get_latest_filing(ticker, "10-K")

    def get_latest_10q(self, ticker):
        return self.get_latest_filing(ticker, "10-Q")

    def get_filing_text(self, ticker, form_type="10-K"):
        filing = self.get_latest_filing(ticker, form_type)

        cik = filing["cik"]
        accession = filing["accession_number"].replace("-", "")
        document = filing["primary_document"]

        url = (
            f"{self.sec_url}/Archives/edgar/data/"
            f"{cik}/{accession}/{document}"
        )

        response = self._get(url)

        return {
            **filing,
            "url": url,
            "text": response.text
        }