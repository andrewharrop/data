import requests
from bs4 import BeautifulSoup
import json

url = "https://en.wikipedia.org/wiki/S%26P/TSX_Composite_Index"
def get():
    my_rows = []
    m_obj = {}
    page = requests.get(url).content.decode()
    soup = BeautifulSoup(page, "html.parser")
    tables = soup.findAll("table")[1]
    t_body = tables.find("tbody")
    rows = t_body.findAll("tr")
    for row in rows[1:]:
        my_rows.append((row.get_text().strip("\n").split("\n"))[:2])
    for item in my_rows:
        m_obj[item[1]] = item[0]+ ".TO"
    with open("tsx.json", "w") as tsx:
        json.dump(m_obj, tsx)
        tsx.close()
get()
