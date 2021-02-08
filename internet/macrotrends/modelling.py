# Use base values provided from access for modelling anomalies and conservative trends
from access import parse
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
import matplotlib.pyplot as plt
import pandas
import time
import datetime


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
    def __init__(self, data, ticker, name):
        self.data = data  # Swap for simplicity [oldest, ... , newest]
        self.name = name
        self.ticker = ticker

    def growth_rates(self):
        gr = []
        for index in range(1, len(self.data)):
            gr.append((self.data[index] - self.data[index - 1]) / self.data[index - 1])
        return gr

    def average(self):
        return sum(self.data) / len(self.data)

    def linear_regression_rate(self, view=True):
        xp = []
        length = len(self.data)
        for point in range(1, length + 1):
            xp.append(point)
        xp = xp[::-1]
        gm = []
        for item in xp:
            gm.append(datetime.datetime.now().year - item + 1)
        x = np.array(xp).reshape((-1, 1))  # Transpose
        y = np.array(self.data)
        lrm = LinearRegression().fit(x, y)
        cd = (lrm.score(x, y))  # Coefficient of determination
        it = lrm.intercept_  # Intercept
        cf = lrm.coef_  # Slope
        regressor3 = RandomForestRegressor(max_depth=5, random_state=50, n_jobs=3)
        regressor3 = regressor3.fit(x, y)
        X_grid = np.arange(min(x), max(x), 0.01)
        X_grid = X_grid.reshape((len(X_grid), 1))

        if view:
            fig = plt.figure()
            fig.suptitle(self.name + ", " + self.ticker + ", " + "Approx " + str(round(len(xp) / 4)) + " years of data",
                         fontsize=12)
            plt.scatter(x, y)
            g, u = np.polyfit(np.array(xp), y, 1)
            plt.plot(np.array(xp), g * np.array(xp) + u)
            plt.plot(X_grid, regressor3.predict(X_grid),
                     color='green')
            plt.show()
        return cd, it, cf[0]

    def non_linear_and_linear_regression(self, view=True):
        xp = []
        length = len(self.data)
        for point in range(1, length + 1):
            xp.append(point)
        xp = xp[::-1]
        gm = []
        for item in xp:
            gm.append(datetime.datetime.now().year - item + 1)
        x = np.array(xp).reshape((-1, 1))  # Transpose
        y = np.array(self.data)
        regressor1 = RandomForestRegressor(max_depth=1, random_state=1, n_jobs=3, max_samples=10)
        regressor2 = RandomForestRegressor(max_depth=3, random_state=50, n_jobs=3)
        regressor3 = RandomForestRegressor(max_depth=5, random_state=50, n_jobs=3)
        regressor4 = RandomForestRegressor(max_depth=30, random_state=50, n_jobs=3)

        regressor1 = regressor1.fit(x, y)
        regressor2 = regressor2.fit(x, y)
        regressor3 = regressor3.fit(x, y)
        regressor4 = regressor4.fit(x, y)

        cd1 = (regressor1.score(x, y))  # Coefficient of determination
        cd2 = (regressor2.score(x, y))  # Coefficient of determination
        cd3 = (regressor3.score(x, y))  # Coefficient of determination
        cd4 = (regressor4.score(x, y))  # Coefficient of determination

        X_grid = np.arange(min(x), max(x), 0.01)
        X_grid = X_grid.reshape((len(X_grid), 1))

        # it = lrm.intercept_  # Intercept
        # cf = lrm.coef_  # Slope
        if view:
            fig = plt.figure()
            fig.suptitle(self.name + ", " + self.ticker + ", " + "Approx " + str(round(len(xp) / 4)) + " years of data",
                         fontsize=12)
            plt.scatter(x, y)
            g, u = np.polyfit(np.array(xp), y, 1)
            plt.plot(X_grid, regressor1.predict(X_grid),
                     color='green')
            plt.plot(X_grid, regressor2.predict(X_grid),
                     color='red')
            plt.plot(X_grid, regressor3.predict(X_grid),
                     color='black')
            # plt.plot(X_grid, regressor4.predict(X_grid),
            #          color='blue')
            plt.plot(np.array(xp), g * np.array(xp) + u)
            plt.show()
        return cd1, cd2, cd3

    def non_linear_and_linear_regression_main(self, view=True):
        xp = []
        length = len(self.data)
        for point in range(1, length + 1):
            xp.append(point)
        xp = xp[::-1]
        gm = []
        for item in xp:
            gm.append(datetime.datetime.now().year - item + 1)
        x = np.array(xp).reshape((-1, 1))  # Transpose
        y = np.array(self.data)
        regressor1 = RandomForestRegressor(max_depth=1, random_state=1, n_estimators=150, n_jobs=3, max_samples=10)

        regressor1 = regressor1.fit(x, y)

        cd1 = (regressor1.score(x, y))  # Coefficient of determination

        X_grid = np.arange(min(x), max(x), 0.01)
        X_grid = X_grid.reshape((len(X_grid), 1))

        if view:
            fig = plt.figure()
            fig.suptitle(self.name + ", " + self.ticker + ", " + "Approx " + str(round(len(xp) / 4)) + " years of data",
                         fontsize=12)
            plt.scatter(x, y)
            g, u = np.polyfit(np.array(xp), y, 1)
            plt.plot(X_grid, regressor1.predict(X_grid),
                     color='green')

            plt.plot(np.array(xp), g * np.array(xp) + u)
            plt.show()
        return cd1

    def recent_rates(self):
        gr = []
        for index in range(round((len(self.data) * 3) / 4), len(self.data)):
            gr.append((self.data[index] - self.data[index - 1]) / self.data[index - 1])
        return gr

    def earliest_rates(self):
        gr = []
        for index in range(1, round(len(self.data) / 4) + 1):
            gr.append((self.data[index] - self.data[index - 1]) / self.data[index - 1])
        return gr


class TargetCompute:
    def __init__(self, ticker):
        self.data = parse(ticker)

    def compute_variables(self):
        ps = float(next(iter(self.data["price sales"].values())))
        pb = float(next(iter(self.data["price book"].values())))
        pfcf = float(next(iter(self.data["price fcf"].values())))[1:]
        pe = float(next(iter(self.data["pe ratio"].values())))
        npm = float(next(iter(self.data["net profit margin"].values()))[:-1])
        cr = float(next(iter(self.data["current ratio"].values())))

        bv = 1
        spe = 15
        pbw = 2.5
        fcfw = 12
        npmw = 20

        bv = bv / (ps)
        if pe > 0:
            bv = bv * (spe / (pe))
        else:
            bv = bv * 0.1
        bv = bv * (pbw / (pb))

        bv = bv * (fcfw / (pfcf))
        if npm > 0:
            bv = bv * ((npm) / npmw)
        else:
            bv = bv * 0.1
        return bv * float(self.data["price"]["value"])

    def get_wacc(self):
        return 0.1

    def compute_fcf(self, p_length=10):
        pfcf = (self.data["price fcf"])
        l_rates = []
        for yr in pfcf:
            try:
                l_rates.append(float(pfcf[yr][1:]))
            except ValueError:
                pass
        average = sum(l_rates[round(len(l_rates)*3/4):]) / (len(l_rates)*1/4) * 4

        x = len(l_rates) - 1
        x_ = []
        while x > -1:
            x_.append(x)
            x -= 1
        x_ = x_[::-1]
        # print(len(l_rates), x_)
        X, Y = np.array(x_).reshape(-1, 1), np.array(l_rates).reshape(-1, 1)
        alg = LinearRegression().fit(X, Y)
        yoy_rate = (alg.coef_[0][0] * 4)

        y = 1
        pd_apt = []
        while y < p_length:

            pd_apt.append(average / ((1 + self.get_wacc()) ** y))
            y += 1
        return sum(pd_apt) # 10 years of holding


class Regs:
    def __init__(self, ticker):
        self.ticker = ticker
        self.uo = Craft(self.ticker)

    def runPrim(self, source, doc):
        doc = " ".join([(d[0].upper() + d[1:].lower()) for d in doc.split(" ")])
        source = source.lower()
        statement = self.uo.financial_statements()
        algs = IndAlgorithms(statement[source][doc], self.ticker, doc)
        return algs.linear_regression_rate(view=True)

    def runAlt(self, source, doc):
        doc = " ".join([(d[0].upper() + d[1:].lower()) for d in doc.split(" ")])
        source = source.lower()
        statement = self.uo.financial_statements()
        algs = IndAlgorithms(statement[source][doc], self.ticker, doc)
        return algs.non_linear_and_linear_regression(view=True)

    def run(self, source, doc):
        doc = " ".join([(d[0].upper() + d[1:].lower()) for d in doc.split(" ")])
        source = source.lower()
        statement = self.uo.financial_statements()
        algs = IndAlgorithms(statement[source][doc], self.ticker, doc)
        return algs.non_linear_and_linear_regression_main(view=True)


def get(state, sheet, alt):
    sheet = " ".join([(sheetz[0].upper() + sheetz[1:].lower()) for sheetz in sheet.split(" ")])
    print(sheet)
    if sheet in ['Revenue', 'Cost Of Goods Sold', 'Gross Profit', 'Research And Development Expenses', 'SG&A Expenses',
                 'Other Operating Income Or Expenses', 'Operating Expenses', 'Operating Income',
                 'Total Non-Operating Income/Expense', 'Pre-Tax Income', 'Income Taxes', 'Income After Taxes',
                 'Other Income', 'Income From Continuous Operations', 'Income From Discontinued Operations',
                 'Net Income', 'EBITDA', 'EBIT', 'Basic Shares Outstanding', 'Shares Outstanding', 'Basic EPS',
                 'EPS - Earnings Per Share']:
        doc = "income statement, quarterly"
        if alt == 1:
            return state.run(doc, sheet)
        elif alt == 2:
            return state.runAlt(doc, sheet)
        elif alt == 3:
            return state.runPrim(doc, sheet)
    elif sheet in ['Cash On Hand', 'Receivables', 'Inventory', 'Pre-Paid Expenses', 'Other Current Assets',
                   'Total Current Assets', 'Property, Plant, And Equipment', 'Long-Term Investments',
                   'Goodwill And Intangible Assets', 'Other Long-Term Assets', 'Total Long-Term Assets', 'Total Assets',
                   'Total Current Liabilities', 'Long Term Debt', 'Other Non-Current Liabilities',
                   'Total Long Term Liabilities', 'Total Liabilities', 'Common Stock Net',
                   'Retained Earnings (Accumulated Deficit)', 'Comprehensive Income', 'Other Share Holders Equity',
                   'Share Holder Equity', 'Total Liabilities And Share Holders Equity']:
        doc = "balance sheet, quarterly"
        if alt == 1:
            return state.run(doc, sheet)
        elif alt == 2:
            return state.runAlt(doc, sheet)
        elif alt == 3:
            return state.runPrim(doc, sheet)

    elif sheet in ['Net Income/Loss', 'Total Depreciation And Amortization - Cash Flow', 'Other Non-Cash Items',
                   'Total Non-Cash Items', 'Change In Accounts Receivable', 'Change In Inventories',
                   'Change In Accounts Payable', 'Change In Assets/Liabilities', 'Total Change In Assets/Liabilities',
                   'Cash Flow From Operating Activities', 'Net Change In Property, Plant, And Equipment',
                   'Net Change In Intangible Assets', 'Net Acquisitions/Divestitures',
                   'Net Change In Short-term Investments', 'Net Change In Long-Term Investments',
                   'Net Change In Investments - Total', 'Investing Activities - Other',
                   'Cash Flow From Investing Activities', 'Net Long-Term Debt', 'Net Current Debt',
                   'Debt Issuance/Retirement Net - Total', 'Net Common Equity Issued/Repurchased',
                   'Net Total Equity Issued/Repurchased', 'Total Common And Preferred Stock Dividends Paid',
                   'Financial Activities - Other', 'Cash Flow From Financial Activities', 'Net Cash Flow',
                   'Stock-Based Compensation', 'Common Stock Dividends Paid']:
        doc = "cash flow statement, quarterly"
        if alt == 1:
            return state.run(doc, sheet)
        elif alt == 2:
            return state.runAlt(doc, sheet)
        elif alt == 3:
            return state.runPrim(doc, sheet)
    elif sheet in ['Current Ratio', 'Long-term Debt / Capital', 'Debt/Equity Ratio', 'Gross Margin', 'Operating Margin',
                   'EBIT Margin', 'EBITDA Margin', 'Pre-Tax Profit Margin', 'Net Profit Margin', 'Asset Turnover',
                   'Inventory Turnover Ratio', 'Receiveable Turnover', 'Days Sales In Receivables',
                   'ROE - Return On Equity', 'Return On Tangible Equity', 'ROA - Return On Assets',
                   'ROI - Return On Investment', 'Book Value Per Share', 'Operating Cash Flow Per Share',
                   'Free Cash Flow Per Share']:
        doc = "financial ratios, quarterly"
        if alt == 1:
            return state.run(doc, sheet)
        elif alt == 2:
            return state.runAlt(doc, sheet)
        elif alt == 3:
            return state.runPrim(doc, sheet)
    else:
        return None


def run(ticker, alt=1):
    state = Regs(ticker)
    standard_run = ["revenue", "Gross Profit", "Operating Income", "Net Income", "Cash On Hand", "Total Current Assets",
                    "Total Assets", "Total Current Liabilities", "Long Term Debt", "Total Liabilities",
                    "Share Holder Equity", "Long Term Debt", "Net Cash Flow", "Cash Flow From Financial Activities",
                    "Cash Flow From Investing Activities", "Cash Flow From Operating Activities", "Current Ratio",
                    'Net Profit Margin',
                    'Free Cash Flow Per Share', 'Book Value Per Share'
                    ]
    for item in standard_run:
        print(get(state, item, alt))


ot = time.time()

ticker = "bb"
# run(ticker, 1)
print(TargetCompute(ticker).compute_fcf())
print("EX time:", time.time() - ot, " seconds")
