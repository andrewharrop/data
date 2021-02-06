# Use base values provided from access for modelling anomalies and conservative trends
from access import parse
import numpy as np
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt
import pandas
# Datasets are structured from most recent to least recent
class Craft:
    def __init__(self, ticker):
        self.res = parse(ticker)
        self.ticker = ticker
        self.sheets = ["income statement",
                       "income statement, quarterly",
                       "balance sheet",
                       "balance sheet, quarterly",
                       "cash flow statement",
                       "cash flow statement, quarterly",
                       "financial ratios",
                       "financial ratios, quarterly",
                       ]

    def price_data(self):
        return self.res["price"]["historical"]

    def price_struct(self):
        # Comprehensive data grouping
        p_data = self.price_data()

        averages = []
        opens = []
        closes = []
        lows = []
        highs = []
        changes = []
        for year in p_data:
            averages.append(float(p_data[year]["Average Stock Price"]))
            opens.append(float(p_data[year]["Year Open"]))
            highs.append(float(p_data[year]["Year High"]))
            lows.append(float(p_data[year]["Year Low"]))
            closes.append(float(p_data[year]["Year Close"]))
            changes.append(float(p_data[year]["Annual % Change"][:-1]))
        return {
            "average": averages,
            "open": opens,
            "close": closes,
            "low": lows,
            "high": highs,
            "change": changes
        }

    def financial_statements(self):
        sheet_obj = {}
        for sheet in self.sheets:
            sheet_obj[sheet] = {}
            for entry in self.res[sheet]:
                sheet_obj[sheet][entry] = []
                for year in self.res[sheet][entry]:
                    try:
                        sheet_obj[sheet][entry].append(float(self.res[sheet][entry][year]))
                    except ValueError:
                        sheet_obj[sheet][entry].append(float(0))

        return sheet_obj

    def get(self):
        return self.res


# Statistical calculations for datasets
class IndAlgorithms:
    def __init__(self, data):
        self.data = data[::-1] # Swap for simplicity [oldest, ... , newest]

    def growth_rates(self):
        gr = []
        for index in range(1, len(self.data)):
            gr.append((self.data[index] - self.data[index - 1]) / self.data[index - 1])
        return gr
    def average(self):
        return sum(self.data) / len(self.data)

    def linear_regression_rate(self, view = False):
        xp = []
        length = len(self.data)
        for point in range(0, length):
            xp.append(point)
        x = np.array(xp).reshape((-1,1)) # Transpose
        y = np.array(self.data)
        lrm = LinearRegression().fit(x,y)
        cd = (lrm.score(x,y)) # Coefficient of determination
        it = lrm.intercept_ # Intercept
        cf = lrm.coef_ # Slope
        if view:
            plt.scatter(x,y)
            g,u = np.polyfit(np.array(xp),y,1)
            plt.plot(np.array(xp),g*np.array(xp)+u)
            plt.show()
        return cf

amzn = Craft("amzn")
statements = amzn.financial_statements()
amzn_algs = IndAlgorithms(statements["income statement"]["Revenue"])
print(amzn_algs.linear_regression_rate(view=True))

bhlb = Craft("bhlb")
statements = bhlb.financial_statements()
bhlb_algs = IndAlgorithms(statements["income statement"]["Revenue"])
print(bhlb_algs.linear_regression_rate(view=True))

aapl = Craft("aapl")
statements = aapl.financial_statements()
aapl_algs = IndAlgorithms(statements["income statement"]["Revenue"])
print(aapl_algs.linear_regression_rate(view=True))
