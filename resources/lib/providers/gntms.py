from datetime import datetime, timedelta
import json, requests, time

def login(data, credentials, headers):
    new_key = credentials["key"]
    url = f"http://data.tmsapi.com/v1.1/stations/10359?lineupId=USA-TX42500-X&api_key={str(new_key)}"

    try:
        s = json.loads(requests.get(url, headers=headers).content)        
        return True, {"key": new_key}
    except (json.JSONDecodeError, requests.HTTPError):
        return False, {"message": "Invalid key"}
    
def epg_main_links(data, channels, settings, session, headers):
    url_list = []

    time_start = datetime.now().strftime("%Y-%m-%dT06:00Z")
    time_end = (datetime.now() + timedelta(int(settings["days"]))).strftime("%Y-%m-%dT06:00Z")
    
    for i in channels:
        url_list.append(
            {"url": f"http://data.tmsapi.com/v1.1/stations/{i}/airings?startDateTime={time_start}&endDateTime={time_end}&imageSize={settings['is']}&imageAspectTV={settings['it']}&api_key={session['session']['key']}",
             "h": headers, "c": i})
    
    return url_list
    
def epg_main_converter(item, data, channels, settings, ch_id=None, genres={}):
    item = json.loads(item)
    airings = []

    for i in item:
        g = dict()
        
        g["c_id"] = ch_id
        g["start"] = int(datetime(*(time.strptime(i["startTime"], "%Y-%m-%dT%H:%MZ")[0:6])).timestamp())
        g["end"] = int(datetime(*(time.strptime(i["endTime"], "%Y-%m-%dT%H:%MZ")[0:6])).timestamp())
        g["b_id"] = f'{i["program"]["tmsId"]}_{g["start"]}_{g["end"]}_{g["c_id"]}'

        entity_type = i["program"].get("entityType", "None")
        qualifiers = i.get("qualifiers", [])

        title_string = i["program"]["title"]
        subtitle = i["program"].get("episodeTitle", i["program"].get("eventTitle"))
        if subtitle is not None and entity_type == "Sports":
            title_string = f"{title_string} {subtitle}"
        if "Live" in qualifiers:
            title_string = f"[LIVE] {title_string}"
        g["title"] = title_string

        if subtitle is not None and subtitle != "" and entity_type != "Sports":
            g["subtitle"] = subtitle

        g["image"] = i["program"].get("preferredImage", {"uri": None})["uri"]
        g["desc"] = i["program"].get("longDescription", i["program"].get("shortDescription"))
        g["date"] = datetime(*(time.strptime(i["program"]["origAirDate"], "%Y-%m-%d")[0:6])).strftime("%Y") if i["program"].get("origAirDate") is not None else \
            str(i["program"]["releaseYear"]) if i["program"].get("releaseYear") is not None else None
        
        star = i["program"].get("qualityRating", {"value": None})["value"]
        if star is not None:
            g["star"] = {"system": "TMS", "value": f"{str(star)}/4"}

        g["director"] = i["program"].get("directors", [])
        g["actor"] = i["program"].get("topCast", [])
        g["credits"] = {"director": g["director"], "actor": g["actor"]}
        
        e_num = i["program"].get("episodeNum")
        s_num = i["program"].get("seasonNum")
        g["season_episode_num"] = {"season": s_num, "episode": e_num}

        g["genres"] = i["program"].get("genres", [])
        if entity_type == "Sports" or entity_type == "Movie":
            g["genres"].append(entity_type)
        if qualifiers is not None:
            g["qualifiers"] = i.get("qualifiers", [])

        # DEFINE AGE RATING
        rating = None
        rating_type = None
        for r in i["program"].get("ratings", []):
            if r["body"] == "Freiwillige Selbstkontrolle der Filmwirtschaft" and settings["at"] == "fsk" or \
                r["body"] == "USA Parental Rating" and settings["at"] == "usa":
                    rating_type = settings["at"].upper()
                    rating = r["code"]
        g["rating"] = {"system": rating_type, "value": rating}

        airings.append(g)

    return airings
