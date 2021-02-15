
# It should be assumed that there is stable dividends from the company in question
# Dividends should be paid quarterly
class Compute:
    def __init__(self, ticker, desired_growth = 0.175):
        self.ticker = ticker
        self.desired_growth = desired_growth
        self.dividends = ticker["_dividends"]

    def compute_prediction(self):
        _dividends = []
        if self.dividends == 0:
            return 0
        try:
            _dividend = self.dividends[0]["amount"] * 4
        except IndexError:
            return 0 # No dividends
        for dividend in range(0, len(self.dividends)-1):
            try:
                _dividends.append((self.dividends[dividend]["amount"] - self.dividends[dividend + 1]["amount"]) /
                              self.dividends[dividend]["amount"])
            except ZeroDivisionError:
                pass
        try:
            approx_rate = 4 * sum(_dividends) / len(_dividends)
        except ZeroDivisionError:
            return 0
        try:
            return _dividend / (self.desired_growth - approx_rate)
        except ZeroDivisionError:
            return 0

# tsla = Compute("f")
# print(tsla.compute_prediction())
