import requests
import time
import datetime
import json

base_url = "https://data.ny.gov/api/views/ptx6-hh79/rows.json?accessType=DOWNLOAD"

def format_file():
    t_req = requests.get(base_url)
    if t_req.status_code == 200:
        json_obj = json.loads(t_req.content.decode())

        re_struct = {"meta":{}, "data":{}}
        # Now that we have an iterable dictionary:
        meta = json_obj["meta"]
        data = json_obj["data"]

        # Meta header setup for document information.  This used low complexity, likely O(1)
        view = meta["view"]
        title = view["name"]
        created = datetime.datetime.fromtimestamp(view["createdAt"]).strftime('%Y-%m-%d %H:%M:%S')
        description = view["description"]
        last_modified = datetime.datetime.fromtimestamp(view["viewLastModified"]).strftime('%Y-%m-%d %H:%M:%S')
        re_struct["meta"] = {"title":title, "description":description, "created": created, "modified":last_modified, "source":base_url}

        # Construct the data object, O(n)
        for entry in data[::-1]:
            incident_id = entry[0]
            incident =entry[-2]
            incident_time = entry[-1]
            re_struct["data"][incident_id] = {"incident": incident, "report time":incident_time}
        return json.dumps(re_struct)

# Average time: .39 seconds.  Data set seems to be discontinued.  Most recent filing on March 3, 2016
print(format_file())
