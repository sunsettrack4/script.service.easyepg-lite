from datetime import datetime, timedelta, timezone
import gzip, lzma, requests, time, xmltodict


def convert_timestring(string):
    dt = datetime(*(time.strptime(string[0:13],'%Y%m%d%H%M%S')[0:6])).astimezone(timezone.utc)
    
    if string[15] == "+":
        dt -= timedelta(hours=int(string[16:18]), 
                                 minutes=int(string[18:]))
    elif string[15] == '-':
        dt += timedelta(hours=int(string[16:18]),
                                 minutes=int(string[18:]))

    return int(dt.timestamp())

def file_decoder(data):
    p = None

    try:  # RAW XML
        p = xmltodict.parse(data, dict_constructor=dict)
    except:
        pass
            
    if not p:        
        try:  # GZIP/GZ
            p = xmltodict.parse(gzip.decompress(data), dict_constructor=dict)
        except:
            pass
    
    if not p:
        try:  # XZ
            p = xmltodict.parse(lzma.decompress(data), dict_constructor=dict)
        except:
            raise Exception("File type could not be verified.")
        
    return p

def channels(data, session, headers={}):
    chlist = {}

    url = data["url"]

    r = requests.get(url, headers=headers)
    p = file_decoder(r.content)

    for ch in p["tv"]["channel"]:
        chan = ch["@id"].replace("&amp;", "and")
        chlist[chan] = {}
        if ch.get("icon") and type(ch["icon"]) == dict:
            chlist[chan]["icon"] = ch["icon"]["@src"]
        elif ch.get("icon") and type(ch["icon"]) == list:
            chlist[chan]["icon"] = ch["icon"][0]["@src"]
        if type(ch["display-name"]) == list:
            chlist[chan]["name"] = ch["display-name"][0]
        elif "@lang" in ch["display-name"]:
            chlist[chan]["name"] = ch["display-name"]["#text"]
            chlist[chan]["lang"] = ch["display-name"]["@lang"]
        else:
            chlist[chan]["name"] = ch["display-name"]

    return chlist

def epg_main_links(data, channels, settings, session, headers):
    return [{"url": data["link"]}]

def epg_main_converter(data, channels, settings, ch_id=None):
    item = file_decoder(data)
    
    airings = []

    dt_now = datetime.now()
    dt_start = datetime(dt_now.year, dt_now.month, dt_now.day, 6, 0).timestamp()
    dt_end = (datetime(dt_now.year, dt_now.month, dt_now.day, 5, 59) + timedelta(days=int(settings["days"]))).timestamp()

    for p in item["tv"]["programme"]:
        g = dict()

        g["c_id"] = p["@channel"].replace("&amp;", "and")
        
        g["start"] = convert_timestring(f'{p["@start"]} {datetime.now(timezone.utc).astimezone().strftime("%z")}' if len(p["@start"]) == 14 else p["@start"])
        g["end"] = convert_timestring(f'{p["@stop"]} {datetime.now(timezone.utc).astimezone().strftime("%z")}' if len(p["@stop"]) == 14 else p["@stop"])
        g["b_id"] = f"{g['c_id']}_{g['start']}"

        if g["c_id"] in channels and dt_start <= g["start"] <= dt_end:
            if type(p["title"]) == list:
                g["title"] = p["title"][0]["#text"] if "@lang" in p["title"][0] else p["title"][0]
            else:
                g["title"] = p["title"]["#text"] if "@lang" in p["title"] else p["title"]
            if p.get("icon"):
                g["image"] = p["icon"]["@src"]
            if p.get("sub-title"):
                g["subtitle"] = p["sub-title"]["#text"] if "@lang" in p["sub-title"] else p["sub-title"]
            if p.get("desc"):
                g["desc"] = p["desc"]["#text"] if "@lang" in p["desc"] else p["desc"]
            if p.get("date"):
                g["date"] = p["date"]
            if p.get("country"):
                if type(p["country"]) == list:
                    g["country"] = ", ".join([i["#text"] for i in p["country"]]) if any([i.get("@lang") for i in p["country"]]) else ", ".join(p["country"])
                else:
                    g["country"] = p["country"]["#text"] if "@lang" in p["country"] else p["country"]            
            if p.get("star-rating"):
                if p["star-rating"].get("@system"):
                    g["star"] = {"system": p["star-rating"]["@system"], "value": p["star-rating"]["value"]}
                else:
                    g["star"] = {"value": p["star-rating"]["value"]}
            if p.get("credits"):
                g["director"] = []
                if p["credits"].get("director"):
                    if type(p["credits"]["director"]) == list:
                        g["director"] = p["credits"]["director"]
                    elif type(p["credits"]["director"]) == str:
                        g["director"] = [p["credits"]["director"]]
                g["actor"] = []
                if p["credits"].get("actor"):
                    g["actor"] = []
                    if type(p["credits"]["actor"]) == list:
                        for i in p["credits"]["actor"]:
                            if type(i) == str:
                                g["actor"].append(i)
                            elif type(i) == dict and i.get("#text"):
                                g["actor"].append(i["#text"])
                    elif type(p["credits"]["actor"]) == dict and p["credits"]["actor"].get("#text"):
                        g["actor"].append(p["credits"]["actor"]["#text"])
                    elif type(p["credits"]["actor"]) == str:
                        g["actor"] = [p["credits"]["actor"]]
                g["credits"] = {"director": g["director"], "actor": g["actor"]}
                if p.get("episode-num"):
                    if p["episode-num"].get("@system") == "xmltv_ns":
                        e = [i.replace(" ", "") for i in p["episode-num"]["#text"].split(".")]
                        if len(e) == 3:
                            g["s"] = int(e[0].split("/")[0]) + 1 if e[0] != "" else 0
                            g["e"] = int(e[1].split("/")[0]) + 1 if e[1] != "" else 0
                            g["season_episode_num"] = {"season": g["s"], "episode": g["e"]}
                g["genres"] = []
                if p.get("category"):
                    if type(p["category"]) == list:
                        for i in p["category"]:
                            if i.get("#text"):
                                g["genres"].append(i["#text"])
                            else:
                                g["genres"].append(i)
                    if type(p["category"]) == dict:
                        g["genres"] = [p["category"]["#text"]]
                    if type(p["category"]) == str:
                        g["genres"] = [p["category"]]
                if p.get("rating"):
                    if p["rating"].get("@system"):
                        g["rating"] = {"system": p["rating"]["@system"], "value": p["rating"]["value"]}
                    else:
                        g["rating"] = {"value": p["rating"]["value"]}

            airings.append(g)

    return airings

