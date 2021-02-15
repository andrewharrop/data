# The idea of this is to create an instance of a company to reduce network traffic and processing overhead

from access import Run

# Much faster
class Company:
    def __init__(self, ticker):
        self._company = Run(ticker)
        try:
            self._prices = self._company.prices()
        except:
            try:
                self._prices = self._company.prices()
            except:
                self._prices = 0
        try:
            self._dividends = self._company.dividends()
        except:
            try:
                self._dividends = self._company.dividends()
            except KeyError:
                self._dividends = 0

        try:
            self._income_statement = self._company.income_statement()
        except:
            self._income_statement = self._company.income_statement()

        try:
            self._statistics = self._company.statistics()
        except:
            self._statistics = self._company.statistics()

        try:
            self._cash_flow = self._company.cash_flow()
        except:
            self._cash_flow = self._company.cash_flow()

        try:
            self._balance_sheet = self._company.balance_sheet()
        except:
            self._balance_sheet = self._company.balance_sheet()



def get(_ticker):
    return Company(_ticker).__dict__

