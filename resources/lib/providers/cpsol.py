from base64 import b64encode, urlsafe_b64decode
from datetime import datetime, timedelta
from hashlib import sha256
from uuid import uuid4
import hmac, json, time

try:
    from curl_cffi import requests
except:
    import requests

provider_headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'
}


def login(data, credentials, headers):
    provision_url =  "https://tvapi-hlm2.solocoo.tv/v1/provision"
    demo_url      = f"https://m7cplogin.solocoo.tv/demo"
    session_url   =  "https://tvapi-hlm2.solocoo.tv/v1/session"

    device_id = str(uuid4())

    device_info = {
        "osVersion": "Windows 10",
        "deviceModel": "Chrome",
        "deviceType": "PC",
        "deviceSerial": device_id,
        "deviceOem": "Chrome",
        "devicePrettyName": "Chrome 141.0.0.0",
        "appVersion": "12.7",
        "language": "de_AT",
        "brand": "m7cp",
        "country": data['country']
    }

    r = requests.Session()
    r.headers = provider_headers
    
    prov_data = r.post(provision_url, json=device_info).json()["session"]["provisionData"]

    m   = sha256()
    m.update(json.dumps({"provisionData": prov_data, "deviceInfo": device_info}, separators=(',', ':')).encode("utf-8"))
    c   = b64encode(m.digest()).decode("utf-8").replace("+", "-").replace("/", "_").replace("=", "")
    t   = str(int(datetime.now().timestamp()))
    h   = hmac.new(urlsafe_b64decode("OXh0-pIwu3gEXz1UiJtqLPscZQot3a0q"), f'{demo_url}{c}{t}'.encode("utf-8"), sha256)
    sig = f'Client key=web.NhFyz4KsZ54,time={t},sig={b64encode(h.digest()).decode("utf-8").replace("+", "-").replace("/", "_").replace("=", "")}'

    r.headers["Authorization"] = sig

    sso_token = r.post(demo_url, json={"provisionData": prov_data, "deviceInfo": device_info}).json()["ssoToken"]

    device_info["featureLevel"]  =  7
    device_info["memberId"]      = "0"
    device_info['ssoToken']      = sso_token
    device_info['provisionData'] = prov_data
    
    token    = r.post(session_url, json=device_info).json()["token"]

    return True, {"data": {"Authorization": f"Bearer {token}"}}


def channels(data, session, headers={}):
    chlist = {}

    channel_url = 'https://tvapi-hlm2.solocoo.tv/v1/bouquet'

    channel_page = requests.get(channel_url, timeout=5, headers=session["session"]["data"])

    channel_content = channel_page.json()

    for channel in channel_content["channels"]:
        if channel.get("onlineEpg"):
            channel_name = channel["assetInfo"]["title"].replace("(16+) ", "").replace("(18+) ", "")
            channel_id = channel["assetInfo"]["id"]
            channel_logo = channel["assetInfo"]["images"][0]["url"]
            chlist[channel_id] = {"name": channel_name, "icon": channel_logo}

    return chlist


def epg_main_links(data, channels, settings, session, headers):
    url_list = []
    today = datetime.today()
    
    days = int(settings["days"]) if int(settings["days"]) <= 9 else 9
    
    time_start = today.strftime("%Y-%m-%d")
    time_end = (today + timedelta(days=(days))).strftime("%Y-%m-%d")

    x = 0
    pre_list = []
    for i in channels:
        pre_list.append(i)
        x = x + 1
        if x < 19:
            continue
        else:
            pre_list_string = ",".join(pre_list)
            url_list.append(
                {"url": f"https://tvapi-hlm2.solocoo.tv/v1/schedule?channels={pre_list_string}&from={time_start}T06:00:00.000Z&until={time_end}T06:00:00.000Z",
                "h": session["session"]["data"]})
            pre_list = []
            x = 0
    if x != 0:
        pre_list_string = ",".join(pre_list)
        url_list.append(
            {"url": f"https://tvapi-hlm2.solocoo.tv/v1/schedule?channels={pre_list_string}&from={time_start}T06:00:00.000Z&until={time_end}T06:00:00.000Z",
             "h": session["session"]["data"]})
    
    return url_list


def epg_main_converter(item, data, channels, settings, ch_id=None, genres={}):
    item = json.loads(item)

    airings = []

    def get_time(string_item):
        return str(int(datetime(*(time.strptime(string_item, "%Y-%m-%dT%H:%M:%SZ")[0:6])).timestamp()))

    for channel in item["epg"].keys():
        for programme in item["epg"][channel]:
            g = dict()

            g["c_id"] = channel
            g["b_id"] = programme["id"]
            g["start"] = get_time(programme["params"]["start"])
            g["end"] = get_time(programme["params"]["end"])
            g["title"] = programme["title"]
            g["genres"] = [i["title"] for i in programme["params"]["genres"]] + [i["title"] for i in programme["params"]["formats"]]
            g["image"] = f'{programme["images"][0]["url"]}&w=1920&h=1080'
            if programme["params"].get("seriesSeason"):
                if ": " in g["title"]:
                    g["subtitle"] = ": ".join(programme["title"].split(": ")[1:])
                    g["title"] = g["title"].split(": ")[0]
                g["season_episode_num"] = {
                    "season": programme["params"]["seriesSeason"], 
                    "episode": programme["params"]["seriesEpisode"]}
            g["rating"] = {"system": data["age_rating"], "value": programme["params"]["age"]}

            airings.append(g)
                   
    return airings


def epg_advanced_links(data, session, settings, programmes, headers={}):
    url_list = []
    
    for i in programmes: 
        url_list.append(
            {"url": f"https://tvapi-hlm2.solocoo.tv/v1/assets/{i}",
             "h": session["session"]["data"]})
    
    return url_list


def epg_advanced_converter(item, data, cache, settings):
    p = json.loads(cache[0])
    g = dict()

    g["b_id"] = p["id"]
    g["desc"] = p["desc"]
    g["country"] = ", ".join(p["params"]["countries"])

    if p["params"]["credits"]:
        directors = []
        actors = []
        for i in p["params"]["credits"]:
            if i["role"] == "Director":
                directors.append(i["person"])
            elif i["role"] == "Actor":
                actors.append(i["person"])
        g["credits"] = {"director": directors, "actor": actors}
    
    return [g]