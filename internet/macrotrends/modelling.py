# Use base values provided from access for modelling anomalies and conservative trends
from access import parse
import numpy as np
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt
import pandas
import time

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
    def get_ticker(self):
        return self.ticker
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
    def __init__(self, data, ticker,name):
        self.data = data[::-1]  # Swap for simplicity [oldest, ... , newest]
        self.name = name
        self.ticker = ticker
    def growth_rates(self):
        gr = []
        for index in range(1, len(self.data)):
            gr.append((self.data[index] - self.data[index - 1]) / self.data[index - 1])
        return gr

    def average(self):
        return sum(self.data) / len(self.data)

    def linear_regression_rate(self, view=False):
        xp = []
        length = len(self.data)
        for point in range(0, length):
            xp.append(point)
        x = np.array(xp).reshape((-1, 1))  # Transpose
        y = np.array(self.data)
        lrm = LinearRegression().fit(x, y)
        cd = (lrm.score(x, y))  # Coefficient of determination
        it = lrm.intercept_  # Intercept
        cf = lrm.coef_  # Slope
        if view:
            fig = plt.figure()
            fig.suptitle(self.name + ", "+self.ticker, fontsize=20)
            plt.scatter(x, y)
            g, u = np.polyfit(np.array(xp), y, 1)
            plt.plot(np.array(xp), g * np.array(xp) + u)
            plt.show()
        return cd,it,cf[0]

    def recent_rates(self):
        gr = []
        for index in range(round((len(self.data) * 3) / 4), len(self.data)):
            gr.append((self.data[index] - self.data[index - 1]) / self.data[index - 1])
        return gr

    def earliest_rates(self):
        gr = []
        for index in range(1, round(len(self.data) / 4)+1):
            gr.append((self.data[index] - self.data[index - 1]) / self.data[index - 1])
        return gr



class Regs:
    def __init__(self, ticker):
        self.ticker = ticker
        self.uo = Craft(self.ticker)

    def run(self, source, doc):
        doc = " ".join([(d[0].upper() + d[1:].lower()) for d in doc.split(" ")])
        source = source.lower()
        statement = self.uo.financial_statements()
        algs = IndAlgorithms(statement[source][doc],self.ticker,doc)
        return algs.linear_regression_rate(view=True)




ot = time.time()
tsla = Regs("tsla")
revenue = tsla.run("income statement", "Revenue")
net_income = tsla.run("income statement", "Gross Profit")
net_income = tsla.run("income statement", "Operating Income")
net_income = tsla.run("income statement", "Net Income")
print(time.time()-ot)
