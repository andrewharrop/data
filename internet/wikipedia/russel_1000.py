import requests
from bs4 import BeautifulSoup
import json
def get():
    url = "https://en.wikipedia.org/wiki/Russell_1000_Index"
    page = requests.get(url).content.decode()
    soup = BeautifulSoup(page, "html.parser")
    table = soup.findAll("table")[2]
    tables = (table.get_text().split("\n\n"))
    t2 = {}

    for item in tables[2:]:
        mt = (item.split("\n")[1:3])
        t2[mt[0]]= mt[1]
    with open("russel_1000.json", "w") as rs1000:
        json.dump(t2, rs1000)
get()
