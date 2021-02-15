from ticker import Company
import requests
import json


# Get all the values.  Has been optimized
class Collect:
    def __init__(self, ticker):
        self.ticker = ticker
        try:
            self.balance_sheet = self.ticker["_balance_sheet"]
        except:
            self.balance_sheet = self.ticker["_balance_sheet"]

        try:
            self.cash_flow = self.ticker["_cash_flow"]
        except:
            self.cash_flow = self.ticker["_cash_flow"]

        try:
            self.statistics = self.ticker["_statistics"]
        except:
            self.statistics = self.ticker["_statistics"]

        self.free_cash_flows = []

    def assets(self):
        return sum([self.balance_sheet[year]["TotalAssets"] for year in self.balance_sheet]) / len(self.balance_sheet)

    def debt(self):
        try:
            return sum([self.balance_sheet[year]["TotalDebt"] for year in self.balance_sheet]) / len(self.balance_sheet)
        except:
            return 0
    def free_cash_flow(self):
        for year in self.cash_flow:
            try:
                self.free_cash_flows.append(self.cash_flow[year]["FreeCashFlow"])
            except KeyError:
                pass
        try:
            average_fcf = sum(self.free_cash_flows) / len(self.free_cash_flows)
        except ZeroDivisionError:
            average_fcf = 0
        return average_fcf

    def fcf_rate(self):
        fcf_rate = []
        for fcf in range(0, len(self.free_cash_flows) - 1):
            fcf_rate.append((self.free_cash_flows[fcf] - self.free_cash_flows[fcf + 1]) / self.free_cash_flows[fcf])
        try:
            fcf_rate = sum(fcf_rate) / len(fcf_rate)
        except ZeroDivisionError:
            fcf_rate = 0
        return fcf_rate

    def market_cap(self):
        try:
            return float(self.statistics["marketCap"]["raw"])
        except KeyError:
            return 0
    def beta(self):
        try:
            return self.statistics["beta"]["raw"]
        except KeyError:
            return 0
    def risk_free_rate(self):
        return float(json.loads(requests.get(
            "https://api.stlouisfed.org/fred/series/observations?series_id=IRLTLT01CAM156N&api_key=10d1cf69d80e6bc531f68386d2abb938&file_type=json").content.decode())[
                         "observations"][-1]["value"]) / 100

    def taxes(self):
        taxes = float(json.loads(requests.get(
            "https://api.stlouisfed.org/fred/series/observations?series_id=IITTRHB&api_key=10d1cf69d80e6bc531f68386d2abb938&file_type=json").content.decode())[
                          "observations"][-1]["value"]) * 0.75 / 100

        return taxes

    def amr(self):
        return 0.10

    def ra(self):
        return 0.125

    def repayment(self):
        rps = []
        for item in self.cash_flow:
            try:
                rps.append(float(self.cash_flow[item]["InterestPaidSupplementalData"]))
            except KeyError:
                pass
        try:
            return sum(rps) / len(rps)
        except ZeroDivisionError:
            print("Repayment default")
            return 0.05 * self.debt()  # 20yr assumption low interest


class Compile:
    def __init__(self, ticker, years):
        self.collect = Collect(ticker)
        self.years = years

    def wacc(self):
        try:
            return (self.collect.market_cap() * (1 / (self.collect.market_cap() + self.collect.debt())) *
                (float(self.collect.risk_free_rate()) + ((float(self.collect.beta())) *
                                                         (float(self.collect.amr()) - float(
                                                             self.collect.risk_free_rate()))))) \
               + ((float(self.collect.repayment()) / (float(self.collect.debt()))) * self.collect.debt() /
                      (self.collect.debt() + self.collect.market_cap()) * (1 - float(self.collect.taxes())))
        except ZeroDivisionError:
            return  0
    def fcf_adjust(self):
        x = 1
        fcfs = []
        rate = self.collect.fcf_rate()
        old = (self.collect.free_cash_flow())
        while x < self.years + 1:
            fcfs.append(old)
            old = old * (1 + rate)
            x += 1
        return fcfs


class Compute:
    def __init__(self, ticker, years=10):
        self.compile = Compile(ticker, years)
        self.fcf = self.compile.fcf_adjust()
        self.wacc = self.compile.wacc()

    def run(self):
        x = 1
        intrinsic_value = 0
        while x < len(self.fcf):
            intrinsic_value += (self.fcf[x - 1] / ((1 + self.wacc) ** x))
            x += 1
        return round(intrinsic_value)


# tesla = Collect(("tsla"))
# print(tesla.risk_free_rate())
# print(tesla.beta())
# print(tesla.amr())
# print(tesla.repayment())
# print(tesla.taxes())
# print(tesla.debt())

# 0.730952381
# 2.090715
# 0.1
# 365601750.0
# 0.2775
# 13422804750.0

# print(tesla.wacc())
# print(tesla.market_cap())
# print(tesla.fcf_rate())
# print(tesla.free_cash_flow())
# print(tesla.assets())
# print(tesla.debt())
# print(tesla.beta())
# print(tesla.risk_free_rate())

# ~8s compute time
#
# tesla = Compute("mo")
# print(tesla.run())
#
# tesla = Compute("jpm")
# print(tesla.run())
#
# tesla = Compute("gs")
# print(tesla.run())
