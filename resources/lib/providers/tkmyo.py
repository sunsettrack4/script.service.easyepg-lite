from datetime import datetime, timedelta, timezone
from uuid import uuid4
import json
import requests
import time


general_headers = \
    {
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'de-DE,de;q=0.9,en-DE;q=0.8,en;q=0.7,en-US;q=0.6',
        'bff_token': '',
        'device-density': 'xhdpi',
        'device-id': str(uuid4()),
        'device-name': 'Windows - Chrome',
        'tenant': 'tv',
        'x-call-type': 'GUEST_USER',
        'x-channel-map-id': 'null',
        'x-request-session-id': str(uuid4()),
        'x-request-tracking-id': str(uuid4()),
    }


def channels(data, session, headers={}):
    chlist = {}

    channel_url = f'https://tv-{data["country"]}-prod.yo-digital.com/{data["country"]}-bifrost/epg/channel?channelMap_id=&includeVirtualChannels=true&natco_key={data["natco_key"]}&app_language={data.get("language", data["country"])}&natco_code={data["country"]}'

    headers.update(general_headers)
    headers.update(
        {
            'app_key': data["app_key"],
            'app_version': data["app_version"],
            'x-user-agent': f'web|web|Chrome-120|{data["app_version"]}|1',
            'x-tv-flow': 'START_UP',
            'x-tv-step': 'EPG_CHANNEL'
        }
    )

    channel_page = requests.get(channel_url, timeout=5, headers=headers)

    channel_content = channel_page.json()

    for channel in channel_content["channels"]:
        channel_name = channel["title"]
        channel_id = channel["station_id"]
        channel_logo = channel["channel_logo"]
        if channel["type"] == "linear":
            chlist[channel_id] = {"name": channel_name, "icon": channel_logo}
    
    return chlist


def epg_main_links(data, channels, settings, session, headers):
    url_list = []
    today = datetime.today()

    headers.update(general_headers)
    headers.update(
        {
            'app_key': data["app_key"],
            'app_version': data["app_version"],
            'x-user-agent': f'web|web|Chrome-120|{data["app_version"]}|1',
            'x-tv-flow': 'EPG',
            'x-tv-step': 'EPG_SCHEDULES_V2'
        }
    )

    days = int(settings["days"]) if data["max_days"] >= int(settings["days"]) else data["max_days"]

    for day in range(days):
        for offset in range(0, 24, 3):
            time_start = ((datetime(today.year, today.month, today.day, 6, 0, 0).replace(tzinfo=timezone.utc)
                            + timedelta(days=day))).strftime("%Y-%m-%d")
            guide_url = f"https://tv-{data['country']}-prod.yo-digital.com/{data['country']}-bifrost/epg/channel/schedules?date={time_start}&hour_offset={str(offset)}&hour_range=3&channelMap_id=&filler=true&app_language={data.get('language', data['country'])}&natco_code={data['country']}"
            url_list.append({"url": guide_url, "h": headers})
    
    return url_list


def epg_main_converter(data, channels, settings, ch_id=None, genres={}):
    item = json.loads(data)

    airings = []

    def get_time(string_item):
        return str(datetime(*(time.strptime(string_item.split(".")[0], "%Y-%m-%dT%H:%M:%S")[0:6])).timestamp()).split(".")[0]

    for channel_id in item["channels"].keys():
        if channel_id in channels:
            for programme in item["channels"][channel_id]:
                g = dict()

                g["c_id"] = channel_id
                if programme["program_id"]:
                    g["b_id"] = programme["program_id"] + "_" + get_time(programme["start_time"])
                else:
                    g["b_id"] = None
                g["start"] = get_time(programme["start_time"])
                g["end"] = get_time(programme["end_time"])
                g["title"] = programme.get("description", "No title available")
                g["subtitle"] = programme.get("episode_name")
                g["date"] = programme.get("release_year")
                g["genres"] = [i["name"] for i in programme["genres"]] if programme.get("genres") else []

                s_num = programme.get("season_number")
                e_num = programme.get("episode_number")
                if s_num and e_num:
                    g["season_episode_num"] = {"season": s_num, "episode": e_num}

                airings.append(g)
    
    return airings


def epg_advanced_links(data, session, settings, programmes, headers={}):
    url_list = []
    
    headers.update(general_headers)
    headers.update(
        {
            'app_key': data["app_key"],
            'app_version': data["app_version"],
            'x-user-agent': f'web|web|Chrome-120|{data["app_version"]}|1',
            'x-tv-flow': 'EPG',
            'x-tv-step': 'EPG_SCHEDULES_V2'
        }
    )
    
    for i in programmes:
        if i is None:
            continue
        url_list.append(
            {"url": f"https://tv-{data['country']}-prod.yo-digital.com/{data['country']}-bifrost/details/series/{i.split('_')[0]}?natco_key={data['natco_key']}&interacted_with_nPVR=false&app_language={data.get('language', data['country'])}&natco_code={data['country']}", 
             "h": headers, "uid": i.split('_')[0], "name": i})
    
    return url_list


def epg_advanced_converter(item, data, cache, settings):
    p = json.loads(cache[0])
    
    g = dict()
    g["b_id"] = item
    g["desc"] = p.get("details", {"description": None}).get("description")
    g["image"] = p.get("poster_image_url")
    
    if p.get("roles"):
        directors = []
        actors = []

        for i in p["roles"]:
            if i["role_name"] in data["director"]:
                directors.append(i["person_name"])
            if i["role_name"] in data["actor"]:
                actors.append(i["person_name"])

        g["credits"] = {"director": directors, "actor": actors}

    if p.get("ratings"):
        g["rating"] = {"system": data["age_rating"], "value": p["ratings"]}
    
    return [g]
    