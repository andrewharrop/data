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
        try:
            return json.loads(ms)["context"]["dispatcher"]["stores"]["QuoteSummaryStore"]
        except KeyError:
            return 0
    def cash_flow(self):
        cf = requests.get(f"{self.base_url}{self.ticker}/cash-flow").content.decode()
        soup = BeautifulSoup(cf, "html.parser")
        scripts = soup.findAll("script")
        ms = ""
        for script in scripts:
            strin = str(script)
            if "root.App.main = " in strin:
                ms = str(script).split("root.App.main = ")[1].split("}(this)")[0].strip(" ").strip("\n")[:-1]
        try:
            return json.loads(ms)["context"]["dispatcher"]["stores"]["QuoteTimeSeriesStore"]["timeSeries"]
        except KeyError:
            return 0
    def balance_sheet(self):
        cf = requests.get(f"{self.base_url}{self.ticker}/balance-sheet").content.decode()
        soup = BeautifulSoup(cf, "html.parser")
        scripts = soup.findAll("script")
        ms = ""
        for script in scripts:
            strin = str(script)
            if "root.App.main = " in strin:
                ms = str(script).split("root.App.main = ")[1].split("}(this)")[0].strip(" ").strip("\n")[:-1]
        try:
            return json.loads(ms)["context"]["dispatcher"]["stores"]["QuoteTimeSeriesStore"]["timeSeries"]
        except KeyError:
            return 0
    def statistics(self):
        cf = requests.get(f"{self.base_url}{self.ticker}/key-statistics").content.decode()
        soup = BeautifulSoup(cf, "html.parser")
        scripts = soup.findAll("script")
        ms = ""
        for script in scripts:
            strin = str(script)
            if "root.App.main = " in strin:
                ms = str(script).split("root.App.main = ")[1].split("}(this)")[0].strip(" ").strip("\n")[:-1]
        try:
            m_dict = json.loads(ms)["context"]["dispatcher"]["stores"]["QuoteSummaryStore"]
            return {**m_dict["defaultKeyStatistics"], **m_dict["financialData"], **m_dict["price"], **m_dict["summaryDetail"]}
        except KeyError:
            return 0
    def income_statement(self):
        cf = requests.get(f"{self.base_url}{self.ticker}/financials").content.decode()
        soup = BeautifulSoup(cf, "html.parser")
        scripts = soup.findAll("script")
        ms = ""
        for script in scripts:
            strin = str(script)
            if "root.App.main = " in strin:
                ms = str(script).split("root.App.main = ")[1].split("}(this)")[0].strip(" ").strip("\n")[:-1]
        try:
            return json.loads(ms)["context"]["dispatcher"]["stores"]["QuoteTimeSeriesStore"]["timeSeries"]
        except KeyError:
            return 0
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
        try:
            divs = json.loads(ms)["context"]["dispatcher"]["stores"]["HistoricalPriceStore"]["eventsData"]
        except KeyError:
            return 0
        cleaned = []
        for item in divs:
            try:
                x = item["splitRatio"]
            except:
                cleaned.append(item)
        return cleaned

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
        try:
            price_data = json.loads(ms)["context"]["dispatcher"]["stores"]["HistoricalPriceStore"]["prices"]
        except KeyError:
            return 0
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

    # For statements
    def long_sheet(self):
        _long_sheet = self.data
        __long_sheet = {}
        for item in _long_sheet:
            if _long_sheet[item]:
                if "annual" in item:
                    key = item[6:]
                elif "trailing" in item:
                    key = item[8:]
                for entry in _long_sheet[item]:
                    if entry:
                        try:
                            try:
                                __long_sheet[entry["asOfDate"]][key] = \
                                    entry["reportedValue"]["raw"]
                            except KeyError:
                                __long_sheet[entry["asOfDate"]] = \
                                    {key: entry["reportedValue"]["raw"]}
                        except TypeError:
                            pass
        return __long_sheet
class Run:
    def __init__(self, ticker):
        self.ticker = ticker
        self.init = Parse(self.ticker)
        # self._summary = (self.init.summary())
        self._dividends = (self.init.dividends())
        self._financials = self.init.financials_summary()
        self._prices = self.init.prices()
        self._cash_flow = self.init.cash_flow()
        self._income_statement = self.init.income_statement()
        self._balance_sheet = self.init.balance_sheet()
        self._statistics = self.init.statistics()
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
        return self._statistics

    def cash_flow(self):
        __cash_flows = Formatter(self._cash_flow)
        return __cash_flows.long_sheet()

    def balance_sheet(self):
        _balance_sheet = Formatter(self._balance_sheet)
        return _balance_sheet.long_sheet()

    def income_statement(self):
        _income_statement = Formatter(self._income_statement)
        return _income_statement.long_sheet()


# print(json.dumps(Run("gs").balance_sheet()))
