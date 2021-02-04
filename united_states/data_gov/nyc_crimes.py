import requests
import time
import datetime
import json

base_url = "https://data.ny.gov/api/views/ptx6-hh79/rows.json?accessType=DOWNLOAD"

def format_file():
    json_file = json.loads(request.get(base_url).contend.decode())
    print(json_file)
print(datetime.datetime.fromtimestamp(1366216625).strftime('%Y-%m-%d %H:%M:%S'))
