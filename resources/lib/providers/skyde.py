from datetime import datetime, timedelta, timezone
import json, re, requests


general_header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/141.0.0.0 Safari/537.36',
                  'x-requested-with': 'XMLHttpRequest',
                  'accept': 'application/json, text/javascript, */*; q=0.01',
                  'content-type': 'application/json'}


def channels(data, session, headers={}):
    country = data['country']
    channel_url = f"https://www.sky.{country}/sgtvg/service/getChannelList"
    data = json.dumps({"dom": "de", "s": 0, "feed": 1})
    
    channel_page = requests.post(channel_url, timeout=5, data=data, headers=general_header)
    channel_data = channel_page.json()

    chlist = {}

    for channel in channel_data["cl"]:
        channel_name = channel["cn"]
        channel_id = str(channel["ci"])
        channel_logo = f"https://www.sky.{country}{channel.get('clu', '/static/img/sky-logo.png')}"
        chlist[channel_id] = {"name": channel_name, "icon": channel_logo}

    return chlist


def epg_main_links(data, channels, settings, session, headers):
    days = int(settings["days"]) if int(settings["days"]) < 10 else 10
    url_list = []
    today = datetime.today()
    
    channel_list = []
    selected_channels = []

    for i in channels:
        channel_list.append(int(i))
        if len(channel_list) == 20:
            selected_channels.append(channel_list)
            channel_list = []
    if len(channel_list) > 0:
        selected_channels.append(channel_list)

    for i in selected_channels:      
        for day in range(days):
            time_start = int(((datetime(today.year, today.month, today.day, 6, 0, 0).replace(tzinfo=timezone.utc)
                            + timedelta(days=day))).timestamp()) * 1000
            
            url_list.append({"url": f"https://www.sky.{data['country']}/sgtvg/service/getBroadcastsForGrid",
                "h": general_header, "d": json.dumps({"cil": i, "d": time_start})})
    
    return url_list


def epg_main_converter(item, data, channels, settings, ch_id=None, genres={}):
    item = json.loads(item)

    airings = []

    def get_age_rating(string_item):
        return string_item.replace("ab ", "").replace(" Jahren", "").replace(" Jahre", "") if string_item else None
    
    def get_image(string_item):
        return f'https://www.sky.{data["country"]}{string_item.replace("_s.jpg", "_l.jpg")}' if string_item else None
    
    for channel in item["cl"]:
        for programme in channel["el"]:
            if programme.get("et"):

                g = dict()

                g["c_id"] = channel["ci"]
                g["b_id"] = f'{programme["ei"]}_{channel["ci"]}'
                g["start"] = programme["bsdt"] / 1000
                g["end"] = programme["bedt"] / 1000
                g["title"] = programme["et"]
                g["subtitle"] = programme.get("epit")
                g["date"] = programme.get("yop")
                g["country"] = programme.get("cop")
                g["image"] = get_image(programme.get("pu"))
                
                s_num = programme.get("sn")
                e_num = programme.get("en")
                g["season_episode_num"] = {"season": s_num, "episode": e_num}

                if programme.get("fsk"):
                    g["rating"] = {"system": "FSK", "value": get_age_rating(programme["fsk"])}

                if programme.get("ec"):
                    g["genres"] = [programme["ec"]]

                airings.append(g)

    return airings


def epg_advanced_links(data, session, settings, programmes, headers={}):
    url_list = []
    
    for i in programmes: 
        a = i.split("_")   
        url_list.append({"url": f"https://www.sky.{data['country']}/sgtvg/service/getBroadcastDetail",
            "name": i, "d": json.dumps({"ei": int(a[0]), "ci": int(a[1]), "sto": 10}), "h": general_header})

    return url_list


def epg_advanced_converter(item, data, cache, settings):
    p = json.loads(cache[0])["event"]

    def get_credits(string_item_1, string_item_2):
        directors = []
        actors = []

        if string_item_1:
            directors.extend([i[1:] if i[0] == " " else i for i in string_item_1.split(",")])
        if string_item_2:
            actors.extend([re.search(r"(.*) \(", i[1:] if i[0] == " " else i).group(1) if " (" in i else i[1:] if i[0] == " " else i for i in string_item_2.split(",")])
            
        return {"director": directors, "actor": actors}
    
    g = dict()
    g["b_id"] = item
    g["desc"] = p.get("desc")
    g["credits"] = get_credits(p.get("c", {}).get("cd"), p.get("c", {}).get("ca"))    

    return [g]
