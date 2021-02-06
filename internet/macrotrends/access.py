# Access the macrotrends page for any given input ticker.
# Note that this is only to be used for educational purposes.
# I am not responsible for the use of information that is produced from this script
import requests
from bs4 import BeautifulSoup
from time import sleep
import ast
import json

sample_tickers = ["BHLB", "GOOG", "TSLA", "BAM"]

msl = 5000  # Minimum safe length

active_directories = [
    "stock-price-history",
    "market-cap",
    "income-statement",
    "income-statement?freq=Q",
    "balance-sheet",
    "balance-sheet?freq=Q",
    "cash-flow-statement",
    "cash-flow-statement?freq=Q",
    "financial-ratios",
    "financial-ratios?freq=Q",
    "revenue",
    "gross-profit",
    "operating-income",
    "ebitda",
    "net-income",
    "eps-earnings-per-share-diluted",
    "shares-outstanding",
    "total-assets",
    "cash-on-hand",
    "long-term-debt",
    "total-liabilities",
    "total-share-holder-equity",
    "profit-margins",
    "gross-margin",
    "operating-margin",
    "ebitda-margin",
    "pre-tax-profit-margin",
    "net-profit-margin",
    "pe-ratio",
    "price-sales",
    "price-book",
    "price-fcf",
    "net-worth",
    "current-ratio",
    "quick-ratio",
    "debt-equity-ratio",
    "roe",
    "roa",
    "roi",
    "return-on-tangible-equity",
    "dividend-yield-history"
]


def construct_url(ticker):
    # There is a strange redirect where it automatically fills out the name associated with the ticker on request
    url = requests.get(f"https://www.macrotrends.net/stocks/charts/{ticker}/")  # Not what we want
    return url.url  # But this is (Our base directory for company x)


def parse(ticker):
    t = construct_url(ticker)
    t_dict = {"ticker": ticker}
    for dir in active_directories:

        xr = requests.get(t + dir).content.decode()
        soup = BeautifulSoup(xr, "html.parser")

        if dir == "stock-price-history":
            content = (soup.find("div", {"id": "main_content"}))
            price = float(content.find("div", {
                "style": "background-color:#fff; margin: 0px 0px 20px 0px; padding:20px 30px; border:1px solid #dfdfdf;"}).find(
                "strong").get_text())
            hist_table = content.find("table", {"class": "historical_data_table"})
            th = hist_table.findAll("thead")
            ttitle = th[0].get_text().strip("\n").strip("\t")
            tcolumns = th[1].get_text().strip("\n").strip("\t").split("\n")
            tb = hist_table.find("tbody")
            trs = tb.findAll("tr")
            rows = [[r.get_text() for r in x.findAll("td")] for x in trs]
            price_dict = {"title": ttitle, "value": price, "historical": {}}
            for item in rows:
                year = item[0]
                price_dict["historical"][year] = {}
                for i in range(1, len(item)):
                    price_dict["historical"][year][tcolumns[i]] = item[i]
            t_dict["price"] = (price_dict)
        elif dir == "market-cap" or dir == "net-worth":
            content = (soup.find("div", {"id": "main_content"}))
            market_cap = content.find("div", {
                "style": "background-color:#fff; margin: 0px 0px 20px 0px; padding:20px 30px; border:1px solid #dfdfdf;"}).find(
                "strong").get_text()
            t_dict[dir.replace("-", " ")] = {"value": market_cap}
        elif dir == "income-statement" or dir == "balance-sheet" or dir == "cash-flow-statement" or dir == "income-statement?freq=Q" \
                or dir == "balance-sheet?freq=Q" or dir == "cash-flow-statement?freq=Q" or dir == "financial-ratios" or \
                dir == "financial-ratios?freq=Q":

            # Get scripts (The information we want is stored in executables on page not visible in non-browser requests)
            content = (requests.get(t + dir).content.decode())
            scripts = (BeautifulSoup(content, "html.parser").find_all("script"))

            # Convert the correct script into text ->Find and evaluate the variable that stores desired data.
            script = [str(script) for script in scripts if len(str(script)) > msl][0]
            eval = ast.literal_eval(script.split("originalData")[1].split("\n")[0][3:-2])

            # Craft the object we want
            des_dict = {}
            for item in eval:
                fn = item["field_name"].split(">")[1].split("<")[0].replace("\\", "")
                des_dict[fn] = {}
                for key in item:
                    if key != "popup_icon" and key != "field_name":
                        des_dict[fn][key] = item[key]
            if dir[-1] == "Q":
                t_dict[dir.replace("-", " ").split("?")[0] + ", quarterly"] = des_dict
            else:
                t_dict[dir.replace("-", " ")] = des_dict
        elif dir == "revenue" or dir == "gross-profit" or dir == "operating-income" or dir == "ebitda" or dir == "net-income" \
                or dir == "eps-earnings-per-share-diluted" or dir == "shares-outstanding" or dir == "total-assets" or \
                dir == "cash-on-hand" or dir == "long-term-debt" or dir == "total-liabilities" or dir == "total-share-holder-equity":
            content = (soup.find("div", {"id": "main_content"}))
            table_out = content.find("div", {
                "style": "background-color:#fff; height:510px; overflow:auto; margin: 30px 0px 30px 0px; padding:0px 30px 20px 0px; border:1px solid #dfdfdf;"})
            tables = table_out.find_all("table")
            o_dict = {}
            for table in tables:
                head = " (".join(table.find("thead").get_text().split("(")).strip(" ").strip("\n").strip("\t")
                body = table.find("tbody")
                data = {}
                for row in body.find_all("tr"):
                    i_row = (row.get_text().split("\n")[1:-1])
                    data[i_row[0]] = i_row[1]
                o_dict[head] = data
            t_dict[dir] = o_dict
        elif dir == "profit-margins":
            content = (soup.find("div", {"id": "main_content"}))
            current_margins = content.find("div", {
                "style": "background-color:#fff; margin: 0px 0px 20px 0px; padding:20px 30px; border:1px solid #dfdfdf;"}).find(
                "strong")
            if current_margins:
                current_margins = current_margins.get_text()

            table_out = content.find("div", {
                "style": "background-color:#fff; height:510px; overflow:auto; margin: 30px 0px 30px 0px; padding:0px 30px 20px 0px; border:1px solid #dfdfdf;"})
            if table_out:
                tables = table_out.find_all("table")
            else:
                table_out = []
            o_dict = {}
            for table in tables:
                head = " (".join(table.find("thead").get_text().split("(")).strip(" ").strip("\n").strip("\t")
                body = table.find("tbody")
                data = {}
                for row in body.find_all("tr"):
                    i_row = (row.get_text().split("\n")[1:-1])
                    data[i_row[0]] = i_row[1]
                if data:
                    o_dict[head] = data
            if o_dict and current_margins:
                t_dict[dir] = {"current": current_margins, "historical": o_dict}
            elif current_margins:
                t_dict[dir] = {"current": current_margins}
            elif o_dict:
                t_dict[dir] = {"historical": o_dict}
        elif dir == "gross-margin" or dir == "operating-margin" or dir == "ebitda-margin" or dir == "pre-tax-profit-margin" or dir == "net-profit-margin":
            content = (soup.find("div", {"id": "main_content"}))
            table_out = content.find("div", {
                "style": "background-color:#fff; height: 500px; overflow:auto; margin: 0px 0px 30px 0px; padding:0px 30px 20px 0px; border:1px solid #dfdfdf;"})
            table = table_out.find("table")
            body = table.find("tbody")
            m_data = {}
            for row in body.findAll("tr"):
                data = (row.get_text().strip("\n").split("\n"))
                date = data[0]
                value = data[3]
                m_data[date] = value
            t_dict[dir.replace("-", " ")] = m_data
        elif dir == "pe-ratio" or dir == "price-sales" or dir == "price-book" or dir == "price-fcf" or dir == "current-ratio" \
                or dir == "quick-ratio" or dir == "debt-equity-ratio" or dir == "roe" or dir == "roa" or dir == "roi" \
                or dir == "return-on-tangible-equity":
            content = (soup.find("div", {"id": "main_content"}))
            current_margins = content.find("div", {
                "style": "background-color:#fff; margin: 0px 0px 20px 0px; padding:20px 30px; border:1px solid #dfdfdf;"}).find(
                "strong")
            if current_margins:
                current_margins = current_margins.get_text()
            table_out = content.find("div", {
                "style": "background-color:#fff; height: 500px; overflow:auto; margin: 0px 0px 30px 0px; padding:0px 30px 20px 0px; border:1px solid #dfdfdf;"})
            table = table_out.find("table")
            body = table.find("tbody")
            m_data = {}
            if current_margins:
                m_data["current"] = current_margins
            for row in body.findAll("tr"):
                data = (row.get_text().strip("\n").split("\n"))
                date = data[0]
                value = data[3]
                m_data[date] = value
            if dir == "roa":
                t_dict["return on assets"] = m_data

            elif dir == "roi":
                t_dict["return on investments"] = m_data

            elif dir == "roe":
                t_dict["return on equity"] = m_data

            else:
                t_dict[dir.replace("-", " ")] = m_data
        elif dir == "dividend-yield-history":
            content = (soup.find("div", {"id": "main_content"}))
            current_margins = content.find("div", {
                "style": "background-color:#fff; margin: 0px 0px 20px 0px; padding:20px 30px; border:1px solid #dfdfdf;"}).findAll(
                "strong")
            if (current_margins):
                payout = current_margins[0].get_text()
                dyield = current_margins[1].get_text()
                t_dict[dir.replace("-", " ")] = {"last payout": payout, "last yield": dyield}

    return (t_dict)


def compare(obj1, obj2):
    for key in obj1:
        if key != "ticker":
            if key in obj2:
                for level_1 in obj1[key]:
                    # try:
                        if type(obj1[key][level_1]) is str:
                            # Current level comparable:
                            if "%" in obj1[key][level_1]:
                                print("\nQuery: ",obj1["ticker"], ">", obj2["ticker"])
                                print(key, " : " , level_1)
                                try:
                                    print("Query status: ",
                                    float(obj1[key][level_1].replace("%", "")) > float(obj2[key][level_1].replace("%", "")))
                                except KeyError:
                                    print("Error, key mismatch")
                            elif "B" in obj1[key][level_1] and "B" in obj2[key][level_1]:
                                print("\nQuery: ",obj1["ticker"], ">", obj2["ticker"])
                                print(key, " : " , level_1)
                                print(float(obj1[key][level_1].replace("$", "").replace("B", "")) > float(
                                    obj2[key][level_1].replace("$", "").replace("B", "")))
                            elif "$" in obj1[key][level_1]:
                                print("\nQuery: ",obj1["ticker"], ">", obj2["ticker"])
                                print(key, " : " , level_1)
                                print("Query status: ",
                                    float(obj1[key][level_1].replace("$", "")) > float(obj2[key][level_1].replace("$", "")))
                        elif type(obj1[key][level_1]) is float:
                            print("\nQuery: ",obj1["ticker"], ">", obj2["ticker"])
                            print(key, " : " ,level_1)
                            print("Query status: ", obj1[key][level_1] > obj2[key][level_1])
                        else:
                            for level2 in obj1[key][level_1]:

                                try:
                                    if type(obj1[key][level_1][level2]) != dict:
                                        if obj1[key][level_1][level2] and obj2[key][level_1][level2]:
                                            print("\nQuery: ", obj1["ticker"], ">", obj2["ticker"])
                                            print(key, " : " , level_1, " : ",level2)
                                            print("Query status: ", float(obj1[key][level_1][level2]) > float(obj2[key][level_1][level2]))
                                except KeyError:
                                    pass

# for tick in sample_tickers:
# aapl = parse("bac")
# amzn = parse("gs")
# print(parse("amzn"))
# compare(aapl, amzn)
