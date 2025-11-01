from datetime import datetime, timedelta
import json, time

try:
    from curl_cffi import requests
except:
    import requests


channel_url = 'https://www.tv-media.at/graphql'
general_headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36",
    "Authorization": "Basic dHZtZWRpYTohMjAyMnR2bWVkaWEj", "Content-Type": "application/json"
}


def login(data, credentials, headers):

    auth_url = 'https://www.tv-media.at/api/auth/session'
    auth_session = requests.Session()
    t = auth_session.post(auth_url, timeout=5, headers=headers)
        
    return True, {"cookies": auth_session.cookies.get_dict(), "data": None}


def channels(data, session, headers={}):
    chlist = {}

    logo_url = "https://www.tv-media.at/_next/static/chunks/8080-22ec85690a3cc49e.js"

    try:
        js = str(requests.get(logo_url).content)
        string = ""
        json_string = ""
        write_json = False
        for i in js:
            if write_json:
                json_string = json_string + i
                if "}]," in json_string:
                    json_string = json.loads(json_string[:-1].replace('id', '"id"').replace('localLogo', '"localLogo"').replace('name', '"name"'))
                    break
            else:
                string = string + i
                if "let l=" in string:
                    write_json = True
                    continue

    except:
        json_string = []

    logo_dict = {i["id"]: i["localLogo"] for i in json_string}

    for i in range(1, 15):

        channel_data = {"operationName": "GetChannelsDayShowtimes",
                        "query": "query GetChannelsDayShowtimes($date: String, $page: Int!, $perPage: Int! = 10) {\n  channelEntries(date: $date, page: $page, perPage: $perPage) {\n    paginatorInfo {\n      ...PagedPagination\n      __typename\n    }\n    data {\n      channel {\n        id\n        name\n        slug\n        favorite {\n          id\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}\nfragment PagedPagination on DefaultPaginator {\n  __typename\n  currentPage\n  hasMorePages\n  lastPage\n  total\n}",
                        "variables": {
                            "date": datetime.today().strftime("%Y-%m-%d"),
                            "page": i,
                            "perPage": 10
                            }
                        }

        channel_page = requests.post(channel_url, timeout=5, json=channel_data, headers=general_headers,
                                    cookies=session["session"]["cookies"])

        channel_content = channel_page.json()

        for channel in channel_content["data"]["channelEntries"]["data"]:
            c = channel["channel"]
            channel_name = c["name"]
            channel_id = c["id"]
            channel_logo = f"https://www.tv-media.at{logo_dict[channel_id]}" if logo_dict.get(channel_id) else f"https://www.tv-media.at/assets/logos/channels/{c['slug']}-logo.svg?w=384&q=90"
            chlist[channel_id] = {"name": channel_name, "icon": channel_logo}

    return chlist


def epg_main_links(data, channels, settings, session, headers):
    url_list = []
    today = datetime.today()

    days = int(settings["days"]) if int(settings["days"]) < 8 else 8

    for i in range(1, 15):
            
        for day in range(days):

            channel_data = {"operationName": "GetChannelsDayShowtimes",
                            "query": "query GetChannelsDayShowtimes($date: String, $page: Int!, $perPage: Int! = 10) {\n  channelEntries(date: $date, page: $page, perPage: $perPage) {\n    paginatorInfo {\n      ...PagedPagination\n      __typename\n    }\n    data {\n      channel {\n        id\n        name\n        slug\n        favorite {\n          id\n          __typename\n        }\n        __typename\n      }\n      showtimes {\n        id\n        title\n        event_id\n        start\n        start_time\n        stop\n        stop_time\n        image {\n          id\n          name\n          url\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}\nfragment PagedPagination on DefaultPaginator {\n  __typename\n  currentPage\n  hasMorePages\n  lastPage\n  total\n}",
                            "variables": {
                                "date": (today + timedelta(days=day)).strftime("%Y-%m-%d"),
                                "page": i,
                                "perPage": 10
                                }
                            }
            
            url_list.append({"url": channel_url, "h": general_headers, "cc": session["session"]["cookies"], "j": channel_data})

    return url_list
            

def epg_main_converter(item, data, channels, settings, ch_id=None, genres={}):
    item = json.loads(item)

    airings = []

    for channel in item["data"]["channelEntries"]["data"]:
        
        if channel["channel"]["id"] in channels:
            
            for programme in channel["showtimes"]:

                g = dict()

                g["c_id"] = channel["channel"]["id"]
                g["b_id"] = programme["event_id"]

                g["title"] = programme["title"]

                g["start"] = str(int(datetime(*(time.strptime(programme["start"], "%Y-%m-%d %H:%M:%S")[0:6])).timestamp()))
                g["end"] = str(int(datetime(*(time.strptime(programme["stop"], "%Y-%m-%d %H:%M:%S")[0:6])).timestamp()))

                airings.append(g)

    return airings


def epg_advanced_links(data, session, settings, programmes, headers={}):
    url_list = []
    
    for i in programmes: 

        channel_data = {"operationName": "GetChannelShowtimeByEventId",
                        "query": "query GetChannelShowtimeByEventId($id: String!, $includeChannel: Boolean! = false) {\n  channelShowtimeByEventId(id: $id) {\n    __typename\n    id\n    event_id\n    summary\n    title\n    subtitle\n    start\n    stop\n    year\n    genre\n    countries\n    directors_summary\n    actors_summary\n    metadata {\n      ...MetaData\n      __typename\n    }\n    ... on TVChannelShowtime @include(if: $includeChannel) {\n      channel {\n        __typename\n        id\n        name\n        joyn_livestream\n      }\n      __typename\n    }\n    image {\n      ...FairuAsset\n      __typename\n    }\n  }\n}\nfragment MetaData on Meta {\n  __typename\n  meta_title\n  meta_description\n  google_news_title\n  redirect\n  no_index\n  no_follow\n  open_graph_image {\n    id\n    name\n    url\n    __typename\n  }\n  custom_open_graph_title\n  custom_open_graph_description\n  twitter_image {\n    id\n    name\n    url\n    __typename\n  }\n  custom_twitter_title\n  custom_twitter_description\n  twitter_description\n  open_graph_description\n}\nfragment FairuAsset on FairuAsset {\n  id\n  url\n  width\n  height\n  focal_point\n  name\n  alt\n  copyright_text\n  caption\n  __typename\n}",
                        "variables": {
                            "id": i,
                            "includeChannel": True
                            }
                        }
        
        url_list.append({"url": channel_url, "h": general_headers, "cc": session["session"]["cookies"], "j": channel_data})

    return url_list


def epg_advanced_converter(item, data, cache, settings):
    p = json.loads(cache[0])["data"]["channelShowtimeByEventId"]

    g = dict()

    g["b_id"] = p["event_id"]

    g["subtitle"] = p.get("subtitle")
    g["desc"] = p["summary"].replace("<p>", "").replace("</p>", "") if p.get("summary") else None
    g["country"] = p.get("countries")
    g["date"] = p.get("year")
    g["image"] = p["image"]["url"] if p.get("image") else None
    g["genres"] = p["genre"].split(" / ") if p.get("genre") else []

    directors = p["directors_summary"].split(",") if p.get("directors_summary") else []
    actors = p["actors_summary"].split(",") if p.get("actors_summary") else []
    g["credits"] = {"director": directors, "actor": actors}

    return [g]
