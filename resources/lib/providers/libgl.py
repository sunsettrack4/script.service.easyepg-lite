from datetime import datetime, timedelta, timezone
import json
import requests


def channels(data, session, headers={}):
    chlist = {}

    channel_url = f'https://spark-prod-{data["country"]}.gnp.cloud.{data["domain"]}/{data["lang_code"]}/web/linear-service/v2/channels?cityId={data["city_id"]}&language={data["lang"]}&productClass=Orion-DASH&platform=web'

    channel_page = requests.get(channel_url, timeout=5, headers=headers)

    channel_content = channel_page.json()

    for channel in channel_content:
        if not channel.get("isHidden"):
            channel_name = channel["name"]
            channel_id = channel["id"]
            channel_logo = channel.get("logo", {}).get("focused", "")
            chlist[channel_id] = {"name": channel_name, "icon": channel_logo}
    
    return chlist


def epg_main_links(data, channels, settings, session, headers):
    url_list = []
    today = datetime.today()

    days = int(settings["days"]) if int(settings["days"]) <= 7 else 7

    for day in range(days):
        for offset in range(0, 24, 6):
            time_start = ((datetime(today.year, today.month, today.day, 6, 0, 0).replace(tzinfo=timezone.utc)
                            + timedelta(days=day, hours=offset))).strftime("%Y%m%d%H%M00")
            guide_url = f"https://staticqbr-prod-{data['country']}.gnp.cloud.{data['domain']}/{data['lang_code']}/web/epg-service-lite/{data['country']}/{data['lang']}/events/segments/{time_start}"
            url_list.append({"url": guide_url})
    
    return url_list


def epg_main_converter(data, channels, settings, ch_id=None, genres={}):
    item = json.loads(data)

    airings = []

    for entry in item["entries"]:
        if entry["channelId"] in channels:
            for programme in entry["events"]:
                g = dict()

                g["c_id"] = entry["channelId"]
                g["b_id"] = programme["id"]
                g["start"] = programme["startTime"]
                g["end"] = programme["endTime"]
                g["title"] = programme["title"]

                airings.append(g)
    
    return airings


def epg_advanced_links(data, session, settings, programmes, headers={}):
    url_list = []
    
    for i in programmes:
        url_list.append(
            {"url": f"https://spark-prod-{data['country']}.gnp.cloud.{data['domain']}/{data['lang_code']}/web/linear-service/v2/replayEvent/{i}?returnLinearContent=true&forceLinearResponse=true&language={data['lang']}"})
    
    return url_list


def epg_advanced_converter(item, data, cache, settings):
    p = json.loads(cache[0])
    
    g = dict()
    g["b_id"] = p["eventId"]
    g["desc"] = p.get("longDescription")
    g["subtitle"] = p.get("episodeName")
    g["country"] = p.get("countryOfOrigin")
    g["date"] = p.get("productionDate")
    g["image"] = f'https://staticqbr-prod-{data["country"]}.gnp.cloud.{data["domain"]}/image-service/intent/{p["eventId"]}/posterTile'
    g["genres"] = p.get("genres")

    s_num = p.get("seasonNumber")
    e_num = p.get("episodeNumber")
    if s_num and e_num:
        if s_num < 100:
            g["season_episode_num"] = {"season": s_num, "episode": e_num}
    elif e_num:
        g["season_episode_num"] = {"season": 1, "episode": e_num}
    
    if len(p.get("directors", [])) > 0:
        g["credits"] = {"director": p["directors"]}
    
    if len(p.get("actors", [])) > 0:
        if g.get("credits"):
            g["credits"]["actor"] = p["actors"]
        else:
            g["credits"] = {"actor": p["actors"]}

    if p.get("minimumAge"):
        g["rating"] = {"system": "FSK", "value": p["minimumAge"]}
    
    return [g]