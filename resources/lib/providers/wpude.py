from datetime import datetime, timedelta, timezone
import json, requests, time, uuid


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


def epg_main_converter(data, channels, settings, ch_id=None, genres={}):
    item = json.loads(data)
    airings = []

    def get_time(string_item):
        return str(datetime.strptime(string_item, "%Y-%m-%dT%H:%M:%SZ").timestamp()).split(".")[0]
    
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
