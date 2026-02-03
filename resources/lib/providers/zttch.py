from bs4 import BeautifulSoup
from datetime import datetime, timedelta, timezone
import json, re, requests, time, uuid

provider_headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36', 
    'dnt': '1', 'origin': 'https://zattoo.com', 'pragma': 'no-cache', 'referer': 'https://zattoo.com/client', 
    'sec-ch-ua': '"Not.A/Brand";v="8", "Chromium";v="114", "Google Chrome";v="114"',
    'sec-ch-ua-mobile': '?0', 'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty', 'sec-fetch-mode': 'same-origin', 
    'sec-fetch-site': 'same-origin'}


def login(data, credentials, headers):
    homepage_url = f'https://{data["domain"]}'
    login_url = f'{homepage_url}/login'
    token_url = f'{homepage_url}/token.json'

    app_token = None

    try:
        token_page = requests.get(token_url, headers=provider_headers)
        token_page.raise_for_status()
        app_token = True
    except:
        pass

    if app_token:
        try:
            token_data = token_page.json()
            app_token = token_data.get("session_token")
        except json.decoder.JSONDecodeError:
            app_token = None

    if app_token is None:
        login_page = requests.get(login_url, headers=provider_headers)

        login_page_parse = BeautifulSoup(login_page.content, 'html.parser')
        app_token_reference = login_page_parse.findAll('script')

        app_token_url = None

        if app_token_reference:
            for item in app_token_reference:
                try:
                    app_token_js_search = re.match("/app-.*", item["src"]).group(0)
                    if app_token_js_search is not None:
                        app_token_url = 'https://' + data["domain"] + app_token_js_search
                except (AttributeError, KeyError):
                    pass
                try:
                    app_token_value_search = re.match("window.appToken = '(.+?)';", item.contents[0]).group(1)
                    if app_token_value_search is not None:
                        app_token = app_token_value_search
                except (AttributeError, IndexError):
                    pass

        if app_token is None and app_token_url is None:
            return
        elif app_token is None and app_token_url is not None:
            js_page = requests.get(app_token_url, headers=provider_headers)
            js_page.raise_for_status()
            json_value_search = re.match(".*token-(.+?).json.*", str(js_page.content)).group(1)
            json_url = 'https://{}/token-{}.json'.format(data["domain"], json_value_search)
            json_page = requests.get(json_url)
            js_page.raise_for_status()
            json_data = json_page.json()
            app_token = json_data["session_token"]

    # GENERAL SESSION ID
    hello_url = 'https://{}/zapi/v3/session/hello'.format(data["domain"])
    hello_data = {'uuid': 'd7512e98-38a0-4f01-b820-5a5cf98141fe'}
    
    hello_data['app_version'] = '3.2411.0'
    hello_data['client_app_token'] = app_token

    hello_page = requests.post(hello_url, data=hello_data, headers=provider_headers)

    first_cookie = {'beaker.session.id': hello_page.cookies['beaker.session.id']}

    # LOGIN WITH CREDENTIALS
    login_page = 'https://{}/zapi/v2/account/login'.format(data["domain"])
    login_data = {'login': credentials["user"], 'password': credentials["pw"]}

    login_page = requests.post(login_page, data=login_data, headers=provider_headers,
                                    cookies=first_cookie)
        
    cookies = {"beaker.session.id": login_page.cookies['beaker.session.id']}
    
    user_data = login_page.json()

    try:
        power_id = user_data["session"]["power_guide_hash"]
        lineup_hash = user_data["session"]["lineup_hash"]
        provider_country = user_data["session"].get("service_region_country", "XX")    
    except:
        return False, {"message": "Wrong credentials"}

    if provider_country != data["country"]:
        return False, {"message": "Account country does not match with selected service country"}
        
    return True, {"cookies": cookies, "data": {"power_guide_hash": power_id, "lineup_hash": lineup_hash}}


def channels(data, session, headers={}):
    url = f'https://{data["domain"]}/zapi/v2/cached/channels/{session["session"]["data"]["power_guide_hash"]}?details=False'
    page = requests.get(url, cookies=session["session"]["cookies"], headers=provider_headers)
    data = page.json()

    chlist = {}
    for group in data["channel_groups"]:
        for channel in group["channels"]:
            if not channel["is_radio"]:
                for quality in channel["qualities"]:
                    channel_name = channel["title"]
                    channel_id = channel["cid"]
                    channel_logo = f"https://images.zattic.com/logos/{quality['logo_token']}/black/210x120.png"
                    chlist[channel_id] = {"name": channel_name, "icon": channel_logo}

    return chlist


def epg_main_links(data, channels, settings, session, headers):
    url_list = []
    today = datetime.today()

    for day in range(int(settings["days"])):
        time_start = str(int(((datetime(today.year, today.month, today.day, 6, 0, 0).replace(tzinfo=timezone.utc)
                           + timedelta(days=day))).timestamp()))
        time_end = str(int(((datetime(today.year, today.month, today.day, 6, 0, 0).replace(tzinfo=timezone.utc)
                         + timedelta(days=(day + 1)))).timestamp()))
        guide_url = f"https://{data['domain']}/zapi/v3/cached/{session['session']['data']['lineup_hash']}/guide?start={time_start}&end={time_end}"
        url_list.append({"url": guide_url, "h": provider_headers, "cc": session["session"]["cookies"]})
    
    return url_list


def epg_main_converter(item, data, channels, settings, ch_id=None, genres={}):
    item = json.loads(item)

    airings = []

    for channel in channels:
        if item["channels"].get(channel):
            for programme in item["channels"][channel]:
                g = dict()

                g["c_id"] = channel
                g["b_id"] = programme["id"]
                g["start"] = programme["s"]
                g["end"] = programme["e"]
                g["title"] = programme.get("t", "Kein Sendungstitel vorhanden")
                g["subtitle"] = programme.get("et")
                g["genres"] = programme.get("g", []) + programme.get("c", [])
                if programme.get("i_url"):
                    g["image"] = programme["i_url"].replace("480x360", "1920x1080")
                s_num = programme.get("s_no")
                if data.get("s_no_fix") and s_num and s_num >= 1970:
                    s_num = None
                e_num = programme.get("e_no")
                g["season_episode_num"] = {"season": s_num, "episode": e_num}
                if programme.get("yp_r"):
                    g["rating"] = {"system": "FSK", "value": programme["yp_r"].replace("FSK ", "")}

                airings.append(g)
                   
    return airings


def epg_advanced_links(data, session, settings, programmes, headers={}):
    url_list = []
    
    x = 0
    pre_list = []
    for i in programmes:
        pre_list.append(i)
        x = x + 1
        if x < 19:
            continue
        else:
            pre_list_string = ",".join(pre_list)
            url_list.append(
                {"url": f"https://zattoo.com/zapi/v2/cached/program/power_details/{session['session']['data']['power_guide_hash']}?program_ids={pre_list_string}",
                "h": provider_headers, "cc": session['session']['cookies']})
            pre_list = []
            x = 0
    if x != 0:
        pre_list_string = ",".join(pre_list)
        url_list.append(
            {"url": f"https://zattoo.com/zapi/v2/cached/program/power_details/{session['session']['data']['power_guide_hash']}?program_ids={pre_list_string}",
            "h": provider_headers, "cc": session['session']['cookies']})
    
    return url_list


def epg_advanced_converter(item, data, cache, settings):
    items = json.loads(cache[0])
    
    p = []

    for item in items["programs"]:
        g = dict()

        g["b_id"] = item["id"]
        g["desc"] = item.get("d")
        g["date"] = item.get("year")
        g["country"] = item.get("country")
        g["credits"] = {"director": [i["f_n"] for i in item["crew"]], "actor": [i["f_n"] for i in item["cast"]]}

        p.append(g)
    
    return p