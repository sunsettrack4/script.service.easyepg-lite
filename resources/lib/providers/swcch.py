from datetime import datetime, timedelta, timezone
import json, requests, time


def genres():
    genre_url = "https://services.sg101.prd.sctv.ch/catalog/tv/DeGenres/genres/list/(ids=all;level=minimal)"

    genre_page = requests.get(genre_url, timeout=5)
    genre_data = genre_page.json()

    return {i["Relations"][0]["TargetIdentifier"]: i["Content"]["Description"]["Title"] for i in genre_data["Nodes"]["Items"]}

def channels(data, session, headers={}):
    chlist = {}

    channel_url = "https://services.sg101.prd.sctv.ch/portfolio/tv/channels"
    
    channel_page = requests.get(channel_url, timeout=5, headers=headers)
    channel_data = channel_page.json()

    for channel in channel_data:
        channel_name = channel["Title"]
        channel_id = channel["Identifier"]
        channel_logo = f"https://services.sg101.prd.sctv.ch/content/images/tv/channel/{channel_id}_w300.webp"
        chlist[channel_id] = {"name": channel_name, "icon": channel_logo}

    return chlist

def epg_main_links(data, channels, settings, session, headers):
    url_list = []
    today = datetime.today()
    
    channel_list = []
    selected_channels = []

    for i in channels:
        channel_list.append(i)
        if len(channel_list) == 20:
            selected_channels.append(','.join(map(str, channel_list)))
            channel_list = []
    if len(channel_list) > 0:
        selected_channels.append(','.join(map(str, channel_list)))

    for i in selected_channels:      
        for day in range(int(settings["days"])):
            time_start = str(((datetime(today.year, today.month, today.day, 6, 0, 0).replace(tzinfo=timezone.utc)
                            + timedelta(days=day))).strftime("%Y%m%d%H%M"))
            time_end = str(((datetime(today.year, today.month, today.day, 6, 0, 0).replace(tzinfo=timezone.utc)
                            + timedelta(days=(day + 1)))).strftime("%Y%m%d%H%M"))
            url_list.append(
                {"url": f"https://services.sg101.prd.sctv.ch/catalog/tv/channels/list/" \
                        f"(end={time_end};ids={i};level=enorm;start={time_start})"})
    
    return url_list


def epg_main_converter(data, channels, settings, ch_id=None, genres={}):
    item = json.loads(data)
    airings = []

    def get_time(string_item):
        return str(datetime(*(time.strptime(string_item, "%Y-%m-%dT%H:%M:%SZ")[0:6])).timestamp()).split(".")[0]

    def get_year(string_item):
        return str(datetime(*(time.strptime(string_item, "%Y-%m-%dT%H:%M:%SZ")[0:6])).year) if string_item else None

    def get_age_rating(string_item):
        return string_item.replace("+", "") if string_item else None
    
    def get_star_rating(string_item):
        return f"{string_item}/100" if string_item else None

    def get_credits(list_item):
        directors = []
        actors = []

        if list_item and len(list_item) > 0:
            for relation_item in list_item:
                if relation_item.get("Kind", "None") == "Participant":
                    name = relation_item.get("TargetNode", {"Content": {}}).get(
                        "Content", {}).get("Description", {"Fullname": None}).get("Fullname")
                    role = relation_item.get("Role")
                    if role == "Director":
                        directors.append(name)
                    if role == "Actor":
                        actors.append(name)
            return {"director": directors, "actor": actors}
        return None

    def get_genres(list_item):
        if list_item and len(list_item) > 0:
            genre_list = []
            for role_item in list_item:
                if role_item.get("Role", "None") == "Genre":
                    genre_list.append(genres.get(role_item["TargetIdentifier"]))
            return genre_list if len(genre_list) > 0 else []
        return []

    def get_image(list_item):
        if list_item and len(list_item) > 0:
            for node_item in list_item:
                if node_item.get("Kind", "None") == "Image":
                    return  f'https://services.sg101.prd.sctv.ch/content/images{node_item.get("ContentPath", "")}' \
                            f'_w1920.webp'
        return None
    
    for node in item["Nodes"]["Items"]:
        for programme in node["Content"].get("Nodes", {"Items": []})["Items"]:
            for availability in programme["Availabilities"]:
                g = dict()

                g["c_id"]               = programme["Channel"]
                g["b_id"]               = programme["Identifier"]
                g["start"]              = get_time(availability["AvailabilityStart"])
                g["end"]                = get_time(availability["AvailabilityEnd"])
                g["title"]              = programme["Content"]["Description"]["Title"]
                g["subtitle"]           = programme["Content"]["Description"].get("Subtitle")
                g["desc"]               = programme["Content"]["Description"].get("Summary")
                g["date"]               = get_year(programme["Content"]["Description"].get("ReleaseDate"))
                g["country"]            = programme["Content"]["Description"].get("Country")
                
                s_num                   = programme["Content"].get("Series", {}).get("Season")
                e_num                   = programme["Content"].get("Series", {}).get("Episode")
                g["season_episode_num"] = {"season": s_num, "episode": e_num}
                rating                  = get_age_rating(programme["Content"]["Description"].get("AgeRestrictionRating"))

                if rating:
                    g["rating"]         = {"system": "FSK", "value": rating}
                
                g["image"]              = get_image(programme["Content"].get("Nodes", {}).get("Items"))
                
                credits                 = get_credits(programme["Relations"])
                if credits:
                    g["credits"]        = credits

                star                    = get_star_rating(programme["Content"]["Description"].get("Rating"))
                if star:
                    g["star"]           = {"system": "IMDb", "value": f"{str(star)}"}

                g["genres"]             = get_genres(programme["Relations"])

                airings.append(g)

    return airings
