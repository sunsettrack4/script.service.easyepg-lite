from datetime import datetime, timedelta, timezone
import gzip, lzma, requests, xmltodict


def file_decoder(data):
    p = None

    try:  # RAW XML
        p = xmltodict.parse(data)
    except:
        pass
            
    if not p:        
        try:  # GZIP/GZ
            p = xmltodict.parse(gzip.decompress(data))
        except:
            pass
    
    if not p:
        try:  # XZ
            p = xmltodict.parse(lzma.decompress(data))
        except:
            raise Exception("File type could not be verified.")
        
    return p

def channels(data, session, headers={}):
    chlist = {}

    url = data["url"]

    r = requests.get(url, headers=headers)
    p = file_decoder(r.content)

    for ch in p["tv"]["channel"]:
        chlist[ch["@id"]] = {}
        if ch.get("icon") and type(ch["icon"]) == dict:
            chlist[ch["@id"]]["icon"] = ch["icon"]["@src"]
        elif ch.get("icon") and type(ch["icon"]) == list:
            chlist[ch["@id"]]["icon"] = ch["icon"][0]["@src"]
        if "@lang" in ch["display-name"]:
            chlist[ch["@id"]]["name"] = ch["display-name"]["#text"]
            chlist[ch["@id"]]["lang"] = ch["display-name"]["@lang"]
        else:
            chlist[ch["@id"]]["name"] = ch["display-name"]

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

        g["c_id"] = p["@channel"]
        
        g["start"] = int(datetime.strptime(f'{p["@start"]} {datetime.now(timezone.utc).astimezone().strftime("%z")}' if len(p["@start"]) == 14 else p["@start"], "%Y%m%d%H%M%S %z").timestamp())
        g["end"] = int(datetime.strptime(f'{p["@stop"]} {datetime.now(timezone.utc).astimezone().strftime("%z")}' if len(p["@stop"]) == 14 else p["@stop"], "%Y%m%d%H%M%S %z").timestamp())
        g["b_id"] = f"{g['c_id']}_{g['start']}"

        if g["c_id"] in channels and dt_start <= g["start"] <= dt_end:
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
                g["country"] = p["country"]
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
                    if type(p["credits"]["actor"]) == list:
                        g["actor"] = p["credits"]["actor"]
                    elif type(p["credits"]["actor"]) == str:
                        g["actor"] = [p["credits"]["actor"]]
                    else:
                        g["actor"] = []
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

