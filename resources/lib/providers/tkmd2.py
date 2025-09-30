from datetime import datetime, timedelta, timezone
from urllib.parse import quote
import json, requests


def channels(data, session, headers={}):
    chlist = {}
    ch_nums = []

    channel_url = 'https://feed.entertainment.tv.theplatform.eu/f/mdeprod/mdeprod-channel-stations-main?range=1-500&lang=short-de'

    channel_page = requests.post(channel_url)

    channel_content = channel_page.json()

    for channel in channel_content["entries"]:
        if channel["dt$displayChannelNumber"] not in ch_nums:
            ch_nums.append(channel["dt$displayChannelNumber"])
            stations_link = list(channel["stations"].keys())[0]
            channel_name = channel["stations"][stations_link]["title"]
            channel_id = channel["id"].split("/")[-1]
            channel_logo = f'https://ngiss.t-online.de/iss?client=ftp22&out=webp&x=180&y=72&ar=keep&src={quote(channel["stations"][stations_link]["thumbnails"]["stationLogo"]["url"])}'
            chlist[channel_id] = {"name": channel_name, "icon": channel_logo}

    return chlist


def epg_main_links(data, channels, settings, session, headers):
    url_list = []
    today = datetime.today()

    for day in range(int(settings["days"])):
        time_start = ((datetime(today.year, today.month, today.day, 6, 0, 0).replace(tzinfo=timezone.utc)
                           + timedelta(days=day))).strftime("%Y-%m-%dT%H:%M:%S.000Z")
        time_end = ((datetime(today.year, today.month, today.day, 6, 0, 0).replace(tzinfo=timezone.utc)
                         + timedelta(days=(day + 1)))).strftime("%Y-%m-%dT%H:%M:%S.000Z")
        
        x = 0
        pre_list = []
        for i in channels:
            pre_list.append(i)
            x = x + 1
            if x < 50:
                continue
            else:
                pre_list_string = "|".join(pre_list)
                url_list.append(
                    {"url": f"https://feed.entertainment.tv.theplatform.eu/f/mdeprod/mdeprod-all-channel-schedules?byId={pre_list_string}&byListingTime={time_start}~{time_end}&byLocationId={data['location_id']}"})
                pre_list = []
                x = 0
        if x != 0:
            pre_list_string = "|".join(pre_list)
            url_list.append(
                {"url": f"https://feed.entertainment.tv.theplatform.eu/f/mdeprod/mdeprod-all-channel-schedules?byId={pre_list_string}&byListingTime={time_start}~{time_end}&byLocationId={data['location_id']}"})
    
    return url_list


def epg_main_converter(data, channels, settings, ch_id=None, genres={}):
    item = json.loads(data)

    airings = []

    for channel in item["entries"]:
        for programme in channel["listings"]:
            g = dict()

            g["c_id"] = channel["id"].split("/")[-1]
            g["b_id"] = programme["program"]["dt$originalIds"]["cmlsProgramId"] + ("_y" if programme["program"].get("dt$creditIds") else "_n")
            g["start"] = programme["startTime"] / 1000
            g["end"] = programme["endTime"] / 1000
            g["title"] = programme["program"]["title"]
            g["subtitle"] = programme["program"].get("secondaryTitle")
            g["desc"] = programme["program"].get("description")
            g["date"] = programme["program"].get("year")
            if programme["program"].get("dt$countries"):
                g["country"] = programme["program"]["dt$countries"].upper()

            s_num = programme["program"].get("tvSeasonNumber")
            e_num = programme["program"].get("tvSeasonEpisodeNumber")
            if s_num and e_num:
                g["season_episode_num"] = {"season": s_num, "episode": e_num}
            elif e_num:
                g["season_episode_num"] = {"season": 1, "episode": e_num}

            if programme["program"].get("tags"):
                genres = []
                for i in programme["program"]["tags"]:
                    if "genre" in i["scheme"]:
                        genres.append(i["title"])
                g["genres"] = genres

            airings.append(g)
    
    return airings


def epg_advanced_links(data, session, settings, programmes, headers={}):
    url_list = []
    
    for i in programmes:
        p = i.split("_")
        # BROADCAST DETAILS
        url_list.append(
            {"url": f"https://tvhubs.t-online.de/v3/ftv-web/BroadcastDetails/202888/{p[0]}", "name": i+"|+|0"})
        # CAST
        if p[1] == "y":
            url_list.append(
                {"url": f"https://tvhubs.t-online.de/v3/ftv-web/CastAndCrewLane/202894/{p[0]}/broadcast", "name": i+"|+|1"})
    
    return url_list


def epg_advanced_converter(item, data, cache, settings):
    p = json.loads(cache[0])
    g = dict()

    g["b_id"] = item

    if p["$type"] == "broadcastdetails":
        if p["content"]["contentInformation"].get("image"):
            g["image"] = p["content"]["contentInformation"]["image"]["href"]
    if p["$type"] == "personlane":
        directors = []
        actors = []
        for i in p["content"]["items"]:
            if i["role"] == "Regie":
                directors.append(i["fullName"])
            elif i["role"] in ["Besetzung", "Moderation"]:
                actors.append(i["fullName"])
        g["credits"] = {"director": directors, "actor": actors}
    
    return [g]