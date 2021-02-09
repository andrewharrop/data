import requests
from bs4 import BeautifulSoup

base = "https://finance.yahoo.com/quote/"
dir = "/community"
def get(ticker):
    conv = requests.get(f"{base}{ticker}{dir}").content.decode()

