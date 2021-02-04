import requests
import xmltodict
import json
import time

base_url = "https://alerts.weather.gov/cap/us.php?x=0"



def parse_xml():
    # Feed in format xml/atom (rss)
    feed = requests.get(base_url)

    # Make sure link is up
    if feed.status_code == 200:

        # Boilerplate feed parser libraries do not work well recursively, so we will have to create a tailored parser

        # First parse the xml feed with the handy xmltodict library
        parsed_feed = (xmltodict.parse(feed.content.decode()))["feed"]
        feed_obj = {"meta": {}, "data":{}}
        # Meta
        title = parsed_feed["title"]
        author = parsed_feed["author"]["name"]
        link = base_url
        feed_obj["meta"] = {"title":title, "author":author, "link":link}

        # Data
        entries = parsed_feed["entry"]  # Iterable entry
        for entry in entries:
            entry_id = entry["id"]
            published = entry["published"]
            updated = entry["updated"]
            entry_title = entry["title"]
            entry_summary = entry["summary"]
            event = entry["cap:event"]
            effective_start = entry["cap:effective"]
            effective_end = entry["cap:expires"]
            urgency = entry["cap:urgency"]
            severity = entry["cap:severity"]
            certainty = entry["cap:certainty"]
            area_desc = entry["cap:areaDesc"]
            location = entry["cap:geocode"]["value"][0].split(" ") # Match up fips code
            locations = []
            states = ""
            with open("fips.json", "r") as fips:
                mjs = json.loads(fips.read())
                for code in location:
                    try:
                        loc = (mjs[code[1:]])
                        locations.append(loc)
                        if loc["state"] not in states:
                            states += loc["state"] + ", "

                    except KeyError:
                        pass

            feed_obj["data"][states[:-2] + " " + event + ", " + effective_start] = {
                "title":entry_title,
                "published":published,
                "updated":updated,
                "event":event,
                "event summary": entry_summary,
                "event severity": severity,
                "event urgency": urgency,
                "event start": effective_start,
                "event end": effective_end,
                "event certainty":certainty,
                "event area": area_desc,
                "event locations": locations,
                "event link": entry_id
            }
        return json.dumps(feed_obj)
    # _feed = feedparser.parse(base_url)  # Creates a feed object
    # feed_obj = {"title": _feed.feed.title, "events": {}}
    # entries = _feed.entries
    #
    # # Likely O(n)
    # for entry in entries:
    #     # print(json.dumps(entry))
    #     print(entry)
    #
    #     feed_obj["events"][entry.id] = {"Event title": entry.title, "Last updated": entry.updated, "Link": entry.link,
    #                                     "Event summary": entry.summary, "Event": entry.cap_event,
    #                                     "Event urgency": entry.cap_urgency, "Event severity": entry.cap_severity,
    #                                     "Area": entry.cap_areadesc, "County code": entry.cap_geocode}
    # return json.dumps(feed_obj)


# Average time is o.65 seconds
print(parse_xml())
