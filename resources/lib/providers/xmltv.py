from datetime import datetime, timedelta
import requests, xmltodict


def channels(data, session, headers={}):
    chlist = {}

    url = data["url"]

    r = requests.get(url, headers=headers)
    p = xmltodict.parse(r.content)

    for ch in p["tv"]["channel"]:
        chlist[ch["@id"]] = {"name": ch["display-name"], "icon": ch.get("icon", {"@src": None}["@src"])["@src"]}

    return chlist

def epg_main_links(data, channels, settings, session, headers):
    return [{"url": data["link"]}]

def epg_main_converter(data, channels, settings, ch_id=None):
    item = xmltodict.parse(data)
    
    airings = []

    dt_now = datetime.now()
    dt_start = datetime(dt_now.year, dt_now.month, dt_now.day, 6, 0).timestamp()
    dt_end = (datetime(dt_now.year, dt_now.month, dt_now.day, 5, 59) + timedelta(days=int(settings["days"]))).timestamp()

    for p in item["tv"]["programme"]:
        g = dict()

        g["c_id"] = p["@channel"]
        
        g["start"] = int(datetime.strptime(p["@start"], "%Y%m%d%H%M%S %z").timestamp())
        g["end"] = int(datetime.strptime(p["@stop"], "%Y%m%d%H%M%S %z").timestamp())
        g["b_id"] = f"{g['c_id']}_{g['start']}"

        if g["c_id"] in channels and dt_start <= g["start"] <= dt_end:
            g["title"] = p["title"]
            if p.get("icon"):
                g["image"] = p["icon"]["@src"]
            if p.get("sub-title"):
                g["subtitle"] = p["sub-title"]
            if p.get("desc"):
                g["desc"] = p["desc"]
            if p.get("date"):
                g["date"] = p["date"]

            airings.append(g)

    return airings

