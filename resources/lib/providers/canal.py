import json
import re, requests


def channels(data, session, headers={}):
    chlist = {}

    channel_url = f'https://hodor.canalplus.pro/api/v2/{data["myc"]}/epgGrid/{data["grid_id"]}/day/0?channelImageColor=white&discoverMode=true'

    channel_page = requests.get(channel_url, timeout=5, headers=headers)

    channel_content = channel_page.json()

    for channel in channel_content["channels"]:
        if channel.get("zapNumber"):
            channel_name = channel["name"]
            channel_id = f'{channel["zapNumber"]}_{channel["URLChannelSchedule"].split("/")[-4]}'
            channel_logo = channel["URLLogoChannel"].replace("{resolutionXY}", "178x134").replace("{imageQualityPercentage}", "80") if channel.get("URLLogoChannel") else None
            chlist[channel_id] = {"name": channel_name, "icon": channel_logo}
    
    return chlist


def epg_main_links(data, channels, settings, session, headers):
    url_list = []
    days = int(settings["days"]) if int(settings["days"]) <= 8 else 8

    for day in range(days):
        for channel in channels:
            url_list.append({"url": f'https://hodor.canalplus.pro/api/v2/{data["myc"]}/channels/{data["grid_id"]}/{channel.split("_")[1]}/broadcasts/day/{day}?channelPosition={channel.split("_")[0]}',
                             "c": channel})
    
    return url_list


def epg_main_converter(item, data, channels, settings, ch_id=None, genres={}):
    item = json.loads(item)

    airings = []

    def get_season_episode(string_item):
        for i, n in enumerate(list(string_item)):
            if not re.match(r"^[0-9]", n):
                return string_item[0:i]
        return string_item

    for t in item["timeSlices"]:   
        for programme in t["contents"]:
            g = dict()

            g["c_id"] = ch_id
            g["b_id"] = str(programme["contentID"]) + "|" + str(programme["startTime"] / 1000) + "|" + ch_id
            g["start"] = programme["startTime"] / 1000
            g["end"] = programme["endTime"] / 1000
            g["title"] = programme["title"]
            g["subtitle"] = programme.get("subtitle")

            s_num = None
            e_num = None
            if f"- {data['season']} " in g["title"]:
                s_num = get_season_episode(g["title"].split(f" - {data['season']} ")[1])
                g["title"] = g["title"].split(f" - {data['season']} ")[0]
            if g["subtitle"] and f"{data['episode']} " in g["subtitle"] and " : " in g["subtitle"]:
                e = g["subtitle"].split(" : ")
                if f"{data['episode']} " in e[0]:
                    e_num = get_season_episode(e[0].split(f"{data['episode']} ")[1].split(" (")[0])
                    if len(e) > 1:
                        g["subtitle"] = e[1]
            elif g["subtitle"] and f"{data['episode']} " in g["subtitle"] and not " : " in g["subtitle"]:
                try:
                    e_num = int(get_season_episode(g["subtitle"].split(f"{data['episode']} ")[1]))
                    g["subtitle"] = None
                except:
                    pass
            elif g["subtitle"] and re.match(r"^S[0-9] E[0-9]", g["subtitle"]):
                e_num = get_season_episode(g["subtitle"].split(" E")[1])
                g["subtitle"] = None
            g["season_episode_num"] = {"season": s_num, "episode": e_num}

            airings.append(g)
    
    return airings


def epg_advanced_links(data, session, settings, programmes, headers={}):
    url_list = []
    
    for i in programmes:
        pr = i.split("|")
        url_list.append(
            {"url": f'https://hodor.canalplus.pro/api/v2/{data["myc"]}/detail/{data["grid_id"]}/okapi/{pr[0]}.json?detailType=detailPage&objectType=unit&fromDiff=true&featureToggles=detailV5,detailV5Sport,registerProspect',
             "uid": pr[0], "name": i})
    
    return url_list


def epg_advanced_converter(item, data, cache, settings):
    pr = json.loads(cache[0])
    p = pr["detail"]

    g = dict()

    g["b_id"] = item
    if p.get("URLImageD2G"):
        g["image"] = p["URLImageD2G"].replace("{resolutionXY}", "1920x1080").replace("{imageQualityPercentage}", "100")
    g["desc"] = p.get("summary", {}).get("text")
    
    et = p["editorialTitle"].split("   ")
    if len(et) == 3:
        g["date"] = p["editorialTitle"].split("   ")[2]
    g["genres"] = [p["editorialTitle"].split("   ")[0]]

    if len(p.get("productionNationalities", [])) > 0:
        c = []
        for i in p["productionNationalities"]:
            if i["prefix"] in ["Pays: ", "Kraj : "]:
                for cc in i["productionNationalitiesList"]:
                    c.append(cc["title"])
        g["country"] = ", ".join(c)

    if len(p.get("personalities", [])) > 0:
        directors = []
        actors = []
        for i in p["personalities"]:
            if i["prefix"] == data["director"]:
                for d in i["personalitiesList"]:
                    directors.append(d["title"])
            if i["prefix"] == data["actor"]:
                for a in i["personalitiesList"]:
                    actors.append(a["title"])
        if len(directors) > 0:
            g["credits"] = {"director": directors}
        if len(actors) > 0:
            if g.get("credits"):
                g["credits"]["actor"] = actors
            else:
                g["credits"] = {"actor": actors}

        if p["technicalInfos"].get("parentalRatings"):
            val = None
            for pa in p["technicalInfos"]["parentalRatings"]:
                
                if pa["authority"] == data["age_rating"]:
                    if data["age_rating_values"].get(pa["value"]):
                        val = data["age_rating_values"][pa["value"]]
                    g["rating"] = {"system": data["age_rating"], "value": val}

    if p.get("reviews", []):
        for r in p["reviews"]:
            
            # FR ONLY
            if r["rating"]["type"] == "telerama":
                g["star"] = {"system": "Télérama", "value": f"{str(r['rating']['value'])}/3"}
                if r.get("review"):
                    g["desc"] = g.get("desc", "") + ("\n\n" if g.get("desc") else "") +  f'Critique de Télérama:\n{r["review"]}'
            elif r["rating"]["type"] == "S.":
                g["star"] = {"system": "Allociné Spectateur", "value": f"{str(r['rating']['value'])}/5"}
            elif r["rating"]["type"] == "P.":
                g["star"] = {"system": "Allociné Presse", "value": f"{str(r['rating']['value'])}/5"}
    
    return [g]