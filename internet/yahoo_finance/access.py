import requests
import json
from time import time
from bs4 import BeautifulSoup


# There are some great indicators here
class Parse:

    def __init__(self, ticker):
        self.base_url = "https://finance.yahoo.com/quote/"
        self.ticker = ticker

    def summary(self):
        summary = requests.get(f"{self.base_url}{self.ticker}/").content.decode()
        soup = BeautifulSoup(summary, "html.parser")
        scripts = soup.findAll("script")
        scripts = soup.findAll("script")
        ms = ""
        for script in scripts:
            strin = str(script)
            if "root.App.main = " in strin:
                ms = str(script).split("root.App.main = ")[1].split("}(this)")[0].strip(" ").strip("\n")[:-1]
        return json.loads(ms)["context"]["dispatcher"]["stores"]

    def financials_summary(self):
        financials = requests.get(f"{self.base_url}{self.ticker}/financials").content.decode()
        soup = BeautifulSoup(financials, "html.parser")
        scripts = soup.findAll("script")
        ms = ""
        for script in scripts:
            strin = str(script)
            if "root.App.main = " in strin:
                ms = str(script).split("root.App.main = ")[1].split("}(this)")[0].strip(" ").strip("\n")[:-1]
        return json.loads(ms)["context"]["dispatcher"]["stores"]["QuoteSummaryStore"]

    def dividends(self):
        dividends = requests.get(
            f"{self.base_url}{self.ticker}/history?period1=689868800&period2=1612742400&interval=div%7Csplit&filter=div&frequency=1d&includeAdjustedClose=true").content.decode()
        soup = BeautifulSoup(dividends, "html.parser")
        scripts = soup.findAll("script")
        ms = ""
        for script in scripts:
            strin = str(script)
            if "root.App.main = " in strin:
                ms = str(script).split("root.App.main = ")[1].split("}(this)")[0].strip(" ").strip("\n")[:-1]
        return json.loads(ms)["context"]["dispatcher"]["stores"]["HistoricalPriceStore"]["eventsData"]
    def prices(self):
        prices = requests.get(
            f"{self.base_url}{self.ticker}/history?period1=689868800&period2=1612828800&interval=1d&filter=history&frequency=1d&includeAdjustedClose=true").content.decode()
        soup = BeautifulSoup(prices, "html.parser")
        scripts = soup.findAll("script")
        ms = ""

        for script in scripts:
            strin = str(script)
            if "root.App.main = " in strin:
                ms = str(script).split("root.App.main = ")[1].split("}(this)")[0].strip(" ").strip("\n")[:-1]
        price_data =  json.loads(ms)["context"]["dispatcher"]["stores"]["HistoricalPriceStore"]["prices"]
        prices = []
        for item in price_data:
            try:
                d = item["type"]
            except:
                prices.append(item)
        return prices
class Formatter:

    def __init__(self, data):
        self.data = data

    def load(self):
        return json.loads(self.data)

    def dump(self):
        return json.dumps(self.data)

    def sheet(self):
        _sheet = self.data
        __sheet = {}
        for year in _sheet:
            tmp_sheet = {}
            for entry in year:
                if isinstance(year[entry], dict):
                    if entry == "endDate":
                        report_date = year[entry]["fmt"]
                    else:
                        tmp_sheet[entry] = year[entry]["raw"]
            __sheet[report_date] = tmp_sheet
        return __sheet


class Run:
    def __init__(self, ticker):
        self.ticker = ticker
        self.init = Parse(self.ticker)
        self._summary = (self.init.summary())
        self._dividends = (self.init.dividends())
        self._financials = self.init.financials_summary()
        self._prices = self.init.prices()
    # Get a list of dividends paid since 1989
    def dividends(self):
        return self._dividends

    # Get a list of the prices, every day since 1989
    def prices(self):
        return self._prices

    # Get related securities and some basic information
    def related(self):
        _related = [r for r in self._summary["RecommendationStore"]["recommendedSymbols"][self.ticker]]
        __related = {}
        for entry in _related:
            __related[entry["symbol"]] = {
                "regularMarketOpen": entry["regularMarketOpen"],
                "currency": entry["currency"],
                "exchange": entry["fullExchangeName"],
                "shortName": entry["shortName"],
                "longName": entry["longName"],
                "fiftyTwoWeekRange": entry["fiftyTwoWeekRange"]["raw"],
                "sharesOutstanding": entry["sharesOutstanding"]["raw"],
                "regularMarketDayHigh": entry["regularMarketDayHigh"],
                "regularMarketChange": entry["regularMarketChange"]["raw"],
                "regularMarketPreviousClose": entry["regularMarketPreviousClose"]["raw"],
                "fiftyTwoWeekHighChange": entry["fiftyTwoWeekHighChange"]["raw"],
                "fiftyTwoWeekLowChange": entry["fiftyTwoWeekLowChange"]["raw"],
                "exchangeDataDelayedBy": entry["exchangeDataDelayedBy"],
                "regularMarketDayLow": entry["regularMarketDayLow"]["raw"],
                "regularMarketPrice": entry["regularMarketPrice"]["raw"],
                "regularMarketVolume": entry["regularMarketVolume"]["raw"],
                "marketCap": entry["marketCap"]["raw"],
                "fiftyTwoWeekLowChangePercent": entry["fiftyTwoWeekLowChangePercent"]["raw"],
                "regularMarketDayRange": entry["regularMarketDayRange"]["raw"],
                "fiftyTwoWeekHigh": entry["fiftyTwoWeekHigh"]["raw"],
                "fiftyTwoWeekHighChangePercent": entry["fiftyTwoWeekHighChangePercent"]["raw"],
                "fiftyTwoWeekLow": entry["fiftyTwoWeekLow"]["raw"]
            }
        return __related

    def statistics(self):
        _statistics = [{statistic: self._summary["QuoteSummaryStore"]["defaultKeyStatistics"][statistic]} for statistic
                       in self._summary["QuoteSummaryStore"]["defaultKeyStatistics"]]
        __statistics = {}
        for entry in _statistics:
            if isinstance(entry, dict):
                for key in entry:
                    if isinstance(entry[key], dict):
                        if entry[key] == {}:
                            __statistics[key] = None
                        else:
                            __statistics[key] = entry[key]['raw']
        return __statistics

    def cash_flow(self):
        _cash_flow = self._financials["cashflowStatementHistory"]["cashflowStatements"]
        f_cash_flow = Formatter(_cash_flow)
        return f_cash_flow.sheet()

    def balance_sheet(self):
        _balance_sheet = self._financials["balanceSheetHistory"]["balanceSheetStatements"]
        f_balance_sheet = Formatter(_balance_sheet)
        return f_balance_sheet.sheet()

    def income_statement(self):
        _income_statement = self._financials["incomeStatementHistory"]["incomeStatementHistory"]
        f_income_statement = Formatter(_income_statement)
        return f_income_statement.sheet()





