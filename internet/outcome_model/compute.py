# This should only be run if an item has been determined to be intrinsically undervalued
# All the files use for this compute must be saves
import json
import requests
from bs4 import BeautifulSoup
import pandas as pd

# This should print if there is an issue
def determine(ticker):
    ticker = ticker.upper()
    with open('../wikipedia/russel_1000.json') as russel:
        file = json.loads(russel.read())
        for item in file:
            if file[item] == ticker:
                try:
                    with open(f"../macrotrends/saves/{item}.json") as instance:
                        instance = json.loads(instance.read())
                        return instance
                except FileNotFoundError:
                    return 0
        return 0


# Middleman
class Data:
    def __init__(self, ticker):
        self.instance = determine(ticker)
        # print(self.instance) If zero we need to append

    def income_statement(self):
        return self.instance["income statement"]

    def margins(self):
        return self.instance["margins"]

    def balance_sheet(self):
        return self.instance["balance sheet"]

    def cash_flow(self):
        try:
            return self.instance["cash flow statement"]
        except TypeError:
            return 0

class Functions:
    def __init__(self, data):
        self.data = data



    def yoy_modeller(self):
        values = []
        for data in self.data:
            if self.data[data]!="":
                values.append(self.data[data])
        trends = []
        for index in range(1, len(values)):
            trends.append((float(values[index - 1]) - float(values[index])) / float(values[index]))
        return trends

    def yoy_modeller_arr(self):
        values = []
        for data in self.data:
            if data!="":
                values.append(data)
        trends = []
        for index in range(1, len(values)):
            trends.append((float(values[index - 1]) - float(values[index])) / float(values[index]))
        return trends
    def modeller(self):
        values = []
        for data in self.data:
            if self.data[data]:
                values.append(self.data[data])
        trends = []
        for index in range(1, len(values)):
            trends.append((float(values[index - 1])))
        return trends
    def fcf_calculator(self):
        fcf = []

        op = []#[float(self.data[0][data]) for data in self.data[0]]
        for data in self.data[0]:
            try:
                op.append(float(self.data[0][data]))
            except ValueError:
                pass
        ppe = []#[float(self.data[1][data]) for data in self.data[1]]
        for data in self.data[1]:
            try:
                ppe.append(float(self.data[1][data]))
            except ValueError:
                pass
        dep = []#[float(self.data[2][data]) for data in self.data[2]]
        for data in self.data[2]:
            try:
                dep.append(float(self.data[2][data]))
            except ValueError:
                pass
        for index in range(0, len(op)):
            try:
                fcf.append(op[index] - (ppe[index] + dep[index]))
            except IndexError:
                pass
        return fcf

    def taxes(self):
        pre = [float(self.data[0][data]) for data in self.data[0]]

        # taxes = [float(self.data[1][data]) for data in self.data[1]]
        taxes = []
        for data in self.data[1]:
            try:
                taxes.append(float(self.data[1][data]))
            except ValueError:
                pass
        rates = []
        for index in range(0, len(pre)):
            try:
                rates.append(taxes[index] / pre[index])
            except IndexError:
                pass
        return rates

    def interest_rate(self):
        ebit = [(self.data[0][data]) for data in self.data[0]]
        taxes = [(self.data[1][data]) for data in self.data[1]]
        earnings = [(self.data[2][data]) for data in self.data[2]]
        debt = [(self.data[3][data]) for data in self.data[3]]
        interest_rate = []
        # Not working properly
        for index in range(0, len(earnings)):
            try:
                print((float(ebit[index]) - float(earnings[index])))
                interest_rate.append((float(ebit[index]) - float(earnings[index])) / float(debt[index]))
            except ValueError:
                pass
        return 0.8
    def fcf_compute(self, years):
        x = 1
        iv = 0
        wacc = self.data["wacc"]
        cf = self.data["cf"]
        try:
            cf_rate = sum(Functions(cf).yoy_modeller_arr()) / len(cf)
        except ZeroDivisionError:
            return 0
        cf2 = sum(cf) / len(cf)
        while x < years:
            iv += ((cf2 * 1000000 *((1+cf_rate)**x)) / ((1+wacc)**x))
            x+=1
        return iv
class DCF_Data:
    def __init__(self, ticker):
        self.data = Data(ticker)
        self.ticker = ticker
        try:
            self.operating_cf = (self.data.cash_flow()["Cash Flow From Operating Activities"])
        except TypeError:
            self.operating_cf = {"i":0}
        self.ppe = (self.data.cash_flow()["Net Change In Property, Plant, And Equipment"])
        self.deprecation = (self.data.cash_flow()["Total Depreciation And Amortization - Cash Flow"])

        self.pre_tax = self.data.income_statement()["Pre-Tax Income"]
        self.taxes = self.data.income_statement()["Income Taxes"]

        self.ebit = self.data.income_statement()["Pre-Tax Income"]
        self.debt = self.data.balance_sheet()["Long Term Debt"]
        self.earnings = self.data.income_statement()["Net Income"]

    def free_cash_flow(self):
        fcf = Functions([self.operating_cf, self.ppe, self.deprecation])
        return fcf.fcf_calculator()

    def tax_rate(self):
        rates = Functions([self.pre_tax, self.taxes])
        return rates.taxes()

    def interest_rate(self):
        # i_rate = Functions([self.ebit, self.taxes, self.earnings, self.debt])
        return [0.08, 0.08 * Functions(self.ebit).modeller()[0]]  # i_rate.interest_rate()

    def get_debt(self):
        debt = Functions(self.debt).modeller()
        return debt

    def market_cap(self):
        url = f"https://www.marketwatch.com/investing/stock/{self.ticker}"
        soup = BeautifulSoup(requests.get(url).content.decode(), "html.parser")
        panel = soup.find("div", attrs={"class": "region region--primary"}).find("div", attrs={
            "class": "column column--aside"})
        panel = panel.find("div", attrs={"class": "group group--elements left"}).find("ul").findAll("li")
        data = ""
        for item in panel:
            text = item.get_text()
            if "Market Cap" in text:
                data = (item.get_text().strip("\n")).split("\n")[1][1:]
                if data[-1].upper() == "T":
                    data = float(data[:-1]) * 1000000000000
                elif data[-1].upper() == "B":
                    data = float(data[:-1]) * 1000000000
                elif data[-1].upper() == "M":
                    data = float(data[:-1]) * 1000000
                elif data[-1].upper() == "K":
                    data = float(data[:-1]) * 1000
                else:
                    data = 0
        return data

    def coe(self, rror=15):
        mror = 12.5 / 100
        rror = rror / 100
        rfrot = float(json.loads(requests.get(
            "https://api.stlouisfed.org/fred/series/observations?series_id=IRLTLT01CAM156N&api_key=10d1cf69d80e6bc531f68386d2abb938&file_type=json").content.decode())[
                          "observations"][-1]["value"]) / 100
        url = f"https://www.marketwatch.com/investing/stock/{self.ticker}"
        soup = BeautifulSoup(requests.get(url).content.decode(), "html.parser")
        panel = soup.find("div", attrs={"class": "region region--primary"}).find("div", attrs={
            "class": "column column--aside"})
        panel = panel.find("div", attrs={"class": "group group--elements left"}).find("ul").findAll("li")
        beta = 1
        for item in panel:
            text = item.get_text()
            if "beta" in text.lower():
                beta = float(text.strip("\n").split("\n")[1])
        return rror + (beta * (mror - rfrot))

    def wacc(self):
        # print(self.market_cap()/((1000000 * self.get_debt()[0]) + self.market_cap()))
        try:

            return (self.market_cap() * self.coe() / (self.market_cap() + (1000000 * self.get_debt()[0]))) +\
               ((1 / (self.market_cap() + self.get_debt()[0])) * ((1 - self.tax_rate()[0]) ** 2) * self.interest_rate()[0])
        except IndexError:
            return 0.15

class DCF:
    def __init__(self, ticker):
        self.ticker = ticker
        self.data = DCF_Data(self.ticker)
        self.wacc = self.data.wacc()
        self.free_cash_flow = self.data.free_cash_flow()
    def compute(self, years = 10):
        computable = Functions({"wacc": self.wacc,"cf":self.free_cash_flow}).fcf_compute(years)
        return computable
    def cap(self):
        return self.data.market_cap()
# This produces the values that are used for valuation
class Modeller:
    def __init__(self, ticker):
        self.data = Data(ticker)

    def revenue_growth_yoy(self):
        revenues = Functions(self.data.income_statement()["Revenue"])
        return revenues.yoy_modeller()

    def net_margin_growth_yoy(self):
        margins = Functions(self.data.margins()["Net Profit Margin"])
        return margins.yoy_modeller()

    def asset_growth_yoy(self):
        assets = Functions(self.data.balance_sheet()["Total Assets"])
        return assets.yoy_modeller()

    def earnings(self):
        earnings = Functions(self.data.income_statement()["Net Income"])
        return earnings.yoy_modeller()


with open("../wikipedia/russel_1000.json") as rs:
    russel = json.loads(rs.read())
    header = [["ticker", "cap/iv", "cap", "iv"]]
    for name in russel:
        ticker = russel[name]
        try:
            try:
                model = DCF(ticker)
                iv = model.compute()
                cap = model.cap()
                try:
                    print("Ticker: ", ticker, " Cap/IV: ",cap/iv ," Cap: ", cap, " IV: ", iv)
                    header.append([ticker, cap/iv, cap, iv])
                except ZeroDivisionError:
                    pass
            except FileNotFoundError:
                pass
        except:
            pass
    frame = pd.DataFrame(header)
    frame.to_excel(excel_writer="iv_resultr.xlsx")
