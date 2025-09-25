from datetime import datetime, timedelta, timezone
import json, time, uuid

try:
    from curl_cffi import requests
except:
    import requests


def login(data, credentials, headers):
    x = 0
    while x < 120:
        mac = str(uuid.uuid4())
        ter = str(uuid.uuid4())

        auth_url = 'https://api.prod.sngtv.magentatv.de/EPG/JSON/Authenticate'
        auth_data = '{"areaid":"1","cnonce":"c4b11948545fb3089720dd8b12c81f8e","mac":"'+mac+'","preSharedKeyID":"NGTV000001","subnetId":"4901","templatename":"NGTV","terminalid":"'+ter+'","terminaltype":"WEB-MTV","terminalvendor":"WebTV","timezone":"UTC","usergroup":"-1","userType":3,"utcEnable":1}'
        auth_session = requests.Session()
        t = auth_session.post(auth_url, timeout=5, data=auth_data, headers=headers)
        
        if t.json().get("retcode", "0") == "-2":
            time.sleep(0.1)
            x = x + 1
            continue
        else:
            break
        
    return True, {"cookies": auth_session.cookies.get_dict(), "data": None}

def channels(data, session, headers={}):
    chlist = {}

    channel_url = 'https://api.prod.sngtv.magentatv.de/EPG/JSON/AllChannel'
    channel_data = '{"properties":[{"name":"logicalChannel",' \
                   '"include":"/channellist/logicalChannel/contentId,/channellist/logicalChannel/type,' \
                   '/channellist/logicalChannel/name,/channellist/logicalChannel/chanNo,' \
                   '/channellist/logicalChannel/pictures/picture/imageType,/channellist/logicalChannel/pictures/' \
                   'picture/href,/channellist/logicalChannel/foreignsn,/channellist/logicalChannel/externalCode,' \
                   '/channellist/logicalChannel/sysChanNo,' \
                   '/channellist/logicalChannel/physicalChannels/physicalChannel/mediaId,' \
                   '/channellist/logicalChannel/physicalChannels/physicalChannel/fileFormat,' \
                   '/channellist/logicalChannel/physicalChannels/physicalChannel/definition"}],' \
                   '"metaDataVer":"Channel/1.1","channelNamespace":"2",' \
                   '"filterlist":[{"key":"IsHide","value":"-1"}],"returnSatChannel":0}'

    headers.update({"X_csrftoken": session["session"]["cookies"]["CSRFSESSION"]})

    channel_page = requests.post(channel_url, timeout=5, data=channel_data, headers=headers,
                                 cookies=session["session"]["cookies"])

    channel_content = channel_page.json()

    for channel in channel_content["channellist"]:
        channel_name = channel["name"]
        channel_id = channel["contentId"]
        channel_logo = ""
        for image in channel["pictures"]:
            if image['imageType'] == "15":
                channel_logo = image['href']
        chlist[channel_id] = {"name": channel_name, "icon": channel_logo}

    return chlist

def epg_main_links(data, channels, settings, session, headers):
    url_list = []
    headers.update({"X_csrftoken": session["session"]["cookies"]["CSRFSESSION"]})
    today = datetime.today()

    for day in range(int(settings["days"])):
        time_start = ((datetime(today.year, today.month, today.day, 6, 0, 0).replace(tzinfo=timezone.utc)
                           + timedelta(days=day))).strftime("%Y%m%d%H%M%S")
        time_end = ((datetime(today.year, today.month, today.day, 5, 59, 0).replace(tzinfo=timezone.utc)
                         + timedelta(days=(day + 1)))).strftime("%Y%m%d%H%M%S")
        guide_url = "https://api.prod.sngtv.magentatv.de/EPG/JSON/PlayBillList"
        guide_data = f'{{"type":2,"isFiltrate":0,"orderType":4,"isFillProgram":1,"channelNamespace":"2","offset":0,' \
                     f'"count":-1,"properties":[{{"name":"playbill","include":"subName,id,name,starttime,endtime,' \
                     f'channelid,ratingid,genres,introduce,cast,genres,country,pictures,producedate,' \
                     f'seasonNum,subNum"}}],' \
                     f'"endtime":"{time_end}","begintime":"{time_start}"}}'
        url_list.append({"url": guide_url, "d": guide_data, "h": headers, "cc": session["session"]["cookies"]})
    
    return url_list

def epg_main_converter(data, channels, settings, ch_id=None, genres={}):
    item = json.loads(data)

    airings = []

    def get_time(string_item):
        return str(datetime(*(time.strptime(string_item.replace(" UTC+00:00", ""), "%Y-%m-%d %H:%M:%S")[0:6])).timestamp()).split(".")[0]

    def get_year(string_item):
        return str(datetime(*(time.strptime(string_item, "%Y-%m-%d")[0:6])).year) if string_item else None

    def get_country(string_item):
        return string_item.upper() if string_item else None

    def get_age_rating(string_item):
        if string_item != "-1":
            return string_item
        return None

    def get_image(list_item):
        if list_item and len(list_item) > 0:
            resolutions = ["1920", "1440", "1280", "960", "720", "480", "360", "180"]
            for resolution in resolutions:
                for image in list_item:
                    if image.get("resolution", ["0", "0"])[0] == resolution:
                        return image.get("href", None)
        return None

    def get_genres(string_item):
        genres = []
        genre_items = string_item.split(",") if string_item else []
        for i in genre_items:
            genres.append(i)
        return genres if len(genres) > 0 else []

    def get_credits(dict_item):
        directors = []
        actors = []
        producers = []
        if dict_item:
            if dict_item.get("director"):
                directors.extend([i for i in dict_item["director"].split(",")]) 
            if dict_item.get("producer"):
                producers.extend([i for i in dict_item["producer"].split(",")])
            if dict_item.get("actor"):
                actors.extend([i for i in dict_item["actor"].split(",")])
        return {"director": directors, "actor": actors, "producer": producers}
    
    if not item.get("playbilllist"):
        raise Exception(f"Playbilllist is unavailable - content: '{str(item)}'")

    for programme in item["playbilllist"]:
        if programme["channelid"] in channels:
            g = dict()

            g["c_id"] = programme["channelid"]
            g["b_id"] = programme["id"]
            g["start"] = get_time(programme["starttime"])
            g["end"] = get_time(programme["endtime"])
            g["title"] = programme.get("name", "Kein Sendungstitel vorhanden")
            g["subtitle"] = programme.get("subName")
            g["desc"] = programme.get("introduce")
            g["date"] = get_year(programme.get("producedate"))
            g["country"] = get_country(programme.get("country"))
            s_num = programme.get("seasonNum")
            e_num = programme.get("subNum")
            g["season_episode_num"] = {"season": s_num, "episode": e_num}
            g["rating"] = {"system": "FSK", "value": get_age_rating(programme["ratingid"])}
            g["image"] = get_image(programme.get("pictures"))
            g["credits"] = get_credits(programme["cast"])
            g["genres"] = get_genres(programme.get("genres"))

            airings.append(g)
                   
    return airings
