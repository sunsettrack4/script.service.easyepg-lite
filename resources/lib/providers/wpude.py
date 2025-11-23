from datetime import datetime, timedelta, timezone
import json, requests, time


def channels(data, session, headers={}):
    chlist = {}

    channel_url = "https://web-proxy.waipu.tv/station-config"
    
    channel_page = requests.get(channel_url, timeout=5, headers=headers)
    channel_data = channel_page.json()

    for channel in channel_data["stations"]:
        channel_name = channel["displayName"]
        channel_id = channel["id"]
        channel_logo = channel["logoTemplateUrl"].replace("${streamQuality}", channel["streamQualities"][0]).replace(
            "${shape}", "standard").replace("${resolution}", "320x180")
        chlist[channel_id] = {"name": channel_name, "icon": channel_logo}

    return chlist

def epg_main_links(data, channels, settings, session, headers):
    url_list = []
    today = datetime.today()
    
    for i in channels:
        for day in range(int(settings["days"])):
            for j in ["00", "04", "08", "12", "16", "20"]:
                time_start = str(((datetime(today.year, today.month, today.day, 6, 0, 0).replace(tzinfo=timezone.utc)
                            + timedelta(days=day))).strftime("%Y-%m-%d"))
                url_list.append(
                    {"url": f"https://epg-cache.waipu.tv/api/grid/{i}/{time_start}T{j}:00:00.000Z", "c": i})
    
    return url_list


def epg_main_converter(item, data, channels, settings, ch_id=None, genres={}):
    item = json.loads(item)
    airings = []

    def get_time(string_item):
        return str(datetime(*(time.strptime(string_item, "%Y-%m-%dT%H:%M:%SZ")[0:6])).timestamp()).split(".")[0]
    
    for programme in item:
        
        g = dict()

        g["c_id"]               = ch_id
        g["b_id"]               = programme["id"]
        g["start"]              = get_time(programme["startTime"])
        g["end"]                = get_time(programme["stopTime"])
        g["title"]              = programme["title"]
        g["subtitle"]           = programme.get("episodeTitle")
        g["image"]              = programme.get("previewImage", "").replace("${resolution}", "1920x1080")
        g["genres"]             = [programme["genre"]] if programme.get("genre") else []

        airings.append(g)

    return airings

def epg_advanced_links(data, session, settings, programmes, headers={}):
    url_list = []
    
    for i in programmes:
        url_list.append(
            {"url": f"https://epg-cache.waipu.tv/api/programs/{i}"})
    
    return url_list

def epg_advanced_converter(item, data, cache, settings):
    item = json.loads(cache[0])
    
    g = dict()
    g["b_id"] = item["id"]
    g["desc"] = item.get("textContent", {"descLong": None}).get("descLong")
    g["date"] = item.get("production", {"year": None}).get("year")
    
    countries = item.get("production", {"countries": []}).get("countries", [])
    if len(countries) > 0:
        g["country"] = ", ".join(countries)
    
    if item.get("series"):
        s_num = item["series"]["seasonNumber"] if item["series"].get("seasonNumber") else None
        e_num = item["series"]["episodeNumber"] if item["series"].get("episodeNumber") else None
        g["season_episode_num"] = {"season": s_num, "episode": e_num}
    
    if item.get("production"):
        directors = []
        actors = []

        if len(item["production"].get("crewMembers", [])) > 0:
            directors.extend([i["name"] for i in item["production"]["crewMembers"]])
        if len(item["production"].get("castMembers", [])) > 0:
            actors.extend([i["name"] for i in item["production"]["castMembers"]])

        g["credits"] = {"director": directors, "actor": actors}

    if item.get("contentMeta"):
        genres = []

        if len(item["contentMeta"].get("subGenres", [])) > 0:
            genres.extend(item["contentMeta"]["subGenres"])
        elif item["contentMeta"].get("mainGenre"):
            genres = [item["contentMeta"]["mainGenre"]]

        g["genres"] = genres

    if item.get("ageRating"):
        if item["ageRating"].get("parentalGuidance"):
            g["rating"] = {"system": "FSK", "value": item["ageRating"]["parentalGuidance"].replace("fsk-", "")}
    
    return [g]
