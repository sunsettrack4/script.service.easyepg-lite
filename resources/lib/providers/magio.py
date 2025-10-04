from datetime import datetime, timedelta, timezone
import json, requests


def login(data, credentials, headers):
    login_url = f'https://{data["country"]}go.magio.tv/v2/auth/init?dsid=Netscape&deviceName=Web%20Browser&deviceType=OTT_WIN&osVersion=0.0.0&appVersion=4.0.27&language=EN'

    token = requests.post(login_url, timeout=5, headers=headers).json()["token"]["accessToken"]

    h = {"Authorization": f"Bearer {token}"}
    
    return True, {"headers": h, "data": None}

def channels(data, session, headers={}):
    chlist = {}

    channel_url = f'https://{data["country"]}go.magio.tv/television/channelsBrief?list=live'

    headers.update(session["session"]["headers"])

    channel_page = requests.get(channel_url, timeout=5, headers=headers)

    channel_content = channel_page.json()

    for channel in channel_content["items"]:
        channel_name = channel["name"]
        channel_id = str(channel["channelId"])
        channel_logo = channel["logoUrl"]
        chlist[channel_id] = {"name": channel_name, "icon": channel_logo}

    return chlist

def epg_main_links(data, channels, settings, session, headers):
    url_list = []
    headers.update(session["session"]["headers"])
    today = datetime.today()

    for day in range(int(settings["days"])):
        time_start = ((datetime(today.year, today.month, today.day, 6, 0, 0).replace(tzinfo=timezone.utc)
                           + timedelta(days=day))).strftime("%Y-%m-%dT%H:%M:%S")
        time_end = ((datetime(today.year, today.month, today.day, 5, 59, 0).replace(tzinfo=timezone.utc)
                         + timedelta(days=(day + 1)))).strftime("%Y-%m-%dT%H:%M:%S")
        guide_url = f"https://{data['country']}go.magio.tv/v2/television/epg?filter=endTime=ge={time_start}.000Z;startTime=le={time_end}.999Z&limit=200&offset=0&list=LIVE&lang=EN"
        url_list.append({"url": guide_url, "d": None, "h": session["session"]["headers"], "cc": None})
    
    return url_list

def epg_main_converter(item, data, channels, settings, ch_id=None, genres={}):
    item = json.loads(item)

    airings = []

    for item in item["items"]:
        if str(item["channel"]["channelId"]) in channels:
            for programme in item["programs"]:
                g = dict()

                g["c_id"] = str(programme["channel"]["id"])
                g["b_id"] = str(programme["scheduleId"])
                g["start"] = programme["startTimeUTC"] / 1000
                g["end"] = programme["endTimeUTC"] / 1000
                g["title"] = programme["program"]["title"]
                g["subtitle"] = programme["program"]["episodeTitle"]
                g["desc"] = programme["program"]["description"]
                g["rating"] = {"system": "Age rating", "value": programme["program"]["programValue"]["parentalRating"]}
                g["image"] = programme["program"]["images"][0] if len(programme["program"]["images"]) > 0 else None
                g["genres"] = [programme["program"]["programCategory"]["desc"]] if programme["program"].get("programCategory") else []

                airings.append(g)
                   
    return airings


def epg_advanced_links(data, session, settings, programmes, headers={}):
    url_list = []
    
    for i in programmes:
        url_list.append(
            {"url": f"https://{data['country']}go.magio.tv/v2/television/detail?scheduleId={i}&lang=EN",
             "h": session["session"]["headers"]})
    
    return url_list


def epg_advanced_converter(item, data, cache, settings):
    p = json.loads(cache[0])
    
    g = dict()
    g["b_id"] = p["schedule"]["scheduleId"]

    s_num = p["schedule"]["program"]["programValue"].get("seasonNumber")
    e_num = p["schedule"]["program"]["programValue"].get("episodeId")
    if s_num and e_num:
        g["season_episode_num"] = {"season": s_num, "episode": e_num}
    elif e_num:
        g["season_episode_num"] = {"season": 1, "episode": e_num}
    
    if len(p["schedule"]["program"]["programRole"]["directors"]) > 0:
        g["credits"] = {"director": [i["fullName"] for i in p["schedule"]["program"]["programRole"]["directors"] if " min" not in i["fullName"]]}
    
    if len(p["schedule"]["program"]["programRole"]["actors"]) > 0:
        if g.get("credits"):
            g["credits"]["actor"] = [i["fullName"] for i in p["schedule"]["program"]["programRole"]["actors"]]
        else:
            g["credits"] = {"actor": [i["fullName"] for i in p["schedule"]["program"]["programRole"]["actors"]]}

    try:
        g["date"] = int(p["schedule"]["program"]["programValue"].get("creationYear"))
    except:
        pass
    
    return [g]