from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import json, string, time

try:
    from curl_cffi import requests
except:
    import requests


regional =  \
    {
        "N3": 
            [
                {"name": "NDR Hamburg", "id": "N3_HH", "remove": "HH: ", "exclude": ["MV: ", "NI: ", "SH: ", "HB: "]},
                {"name": "NDR Mecklenburg-Vorpommern", "id": "N3_MV", "remove": "MV: ", "exclude": ["HH: ", "NI: ", "SH: ", "HB: "]},
                {"name": "NDR Niedersachsen", "id": "N3_NI", "remove": "NI: ", "exclude": ["MV: ", "HH: ", "SH: ", "HB: "]},
                {"name": "NDR Schleswig-Holstein", "id": "N3_SH", "remove": "SH: ", "exclude": ["MV: ", "NI: ", "HH: ", "HB: "]},
                {"name": "radio bremen", "id": "N3_HB", "remove": "HB: ", "exclude": ["MV: ", "NI: ", "SH: ", "HH: "]}
            ],

        "SWR":
            [
                {"name": "SWR BW", "id": "SWR_BW", "remove": "BW: ", "exclude": ["RP: ", "SR: "]},
                {"name": "SWR RP", "id": "SWR_RP", "remove": "RP: ", "exclude": ["BW: ", "SR: "]},
                {"name": "SR", "id": "SWR_SR", "remove": "SR: ", "exclude": ["RP: ", "BW: "]}
            ],

        "MDR":
            [
                {"name": "MDR Sachsen", "id": "MDR_Sachsen", "remove": "Sachsen: ", "exclude": ["ST: ", "TH: "]},
                {"name": "MDR Sachsen-Anhalt", "id": "MDR_ST", "remove": "ST: ", "exclude": ["Sachsen: ", "TH: "]},
                {"name": "MDR Thüringen", "id": "MDR_TH", "remove": "TH: ", "exclude": ["ST: ", "Sachsen: "]}
            ],

        "RBB":
            [
                {"name": "rbb Berlin", "id": "RBB_Berlin", "remove": "Berlin: ", "exclude": ["BB: "]},
                {"name": "rbb Brandenburg", "id": "RBB_BB", "remove": "BB: ", "exclude": ["Berlin: "]}
            ]
    }

def channels(data, session, headers={}):
    chlist = {}

    channel_url = f'https://www.{data["domain"]}/tv-programm/'

    channel_page = requests.get(channel_url, timeout=5)

    channels_parse = BeautifulSoup(channel_page.content, 'html.parser')
    channel_list = channels_parse.findAll('select', {"id": "ChannelsRedirect"})[0].findAll("option")
    
    for channel in channel_list:
        if channel.get("data-trackingpoint"):
            channel_name = channel["label"]
            channel_id = json.loads(channel["data-trackingpoint"])["channel"]
            channel_logo = f'https://a2.{data["domain"]}/images/tv/sender/mini/{channel_id.lower()}.webp'
            if regional.get(channel_id):
                for n in regional[channel_id]:
                    chlist[n["id"]] = {"name": n["name"], "icon": channel_logo}
            else:
                chlist[channel_id] = {"name": channel_name, "icon": channel_logo}
       
    return chlist


def epg_main_links(data, channels, settings, session, headers):
    url_list = []

    for day in range(int(settings["days"])):
        date = (datetime.today() + timedelta(days=day)).strftime("%Y-%m-%d")
        regional_channels = []
        for channel in channels:
            if channel.split("_")[0] in regional_channels:
                continue
            if regional.get(channel.split("_")[0]):
                regional_channels = channel.split("_")[0]
                channel = channel.split("_")[0]
            for page in range(1,3,1):
                url_list.append({"url": f"https://www.{data['domain']}/tv-programm/sendungen/?order=channel&date={date}&page={page}&channel={channel}",
                                 "c": channel})
    
    return url_list


def epg_main_converter(item, data, channels, settings, ch_id=None, genres={}):
    item = BeautifulSoup(item, 'html.parser')
    selected_regionals = [c for c in channels if ch_id in c.split("_")[0]]

    airings = []

    table = item.findAll("table", {"class": "info-table"})[0].findAll("tr", {"class": "hover"})

    for row in table:
        g = dict()

        columns = row.findAll("td")
        
        times = columns[1].find("div").find("strong").get_text().split(" - ")
        date  = columns[1].find("div").find("span").get_text()[3:]
        
        year    = str(datetime.now().year + 1) if datetime.now().month == 12 and date[3:4] == "01" else str(datetime.now().year)
        date_sw = 1 if ((int(times[0][0:1]) > int(times[1][0:1])) or times[0] == times[1]) else 0

        g["start"] = int(datetime(*(time.strptime(f'{date}{year} {times[0]}', "%d.%m.%Y %H:%M")[0:6])).timestamp())
        g["end"]   = int((datetime(*(time.strptime(f'{date}{year} {times[1]}', "%d.%m.%Y %H:%M")[0:6])) + timedelta(days=date_sw)).timestamp())
        
        g["title"] = columns[2].find("span", {"class": ""}).find("a").find("strong").get_text()

        g["genres"] = [columns[3].find("span").get_text()]

        if regional.get(ch_id):
            for s in selected_regionals:
                d = dict()
                d["b_id"]  = s + "|" + columns[2].find("span", {"class": ""}).find("a")["href"].split("/")[-1].replace(".html", "")
                d["c_id"]  = s
                for i in g.keys():
                    d[i] = g[i]

                for t in regional[ch_id]:
                    if t["id"] == s and t["remove"] in d["title"]:
                        d["title"] = d["title"].replace(t["remove"], "")
                        airings.append(d)
                    elif t["id"] == s:
                        x = False
                        for j in t["exclude"]:
                            if j in d["title"]:
                                x = True
                                continue
                        if not x:
                            airings.append(d)

        else:
            g["b_id"]  = columns[2].find("span", {"class": ""}).find("a")["href"].split("/")[-1].replace(".html", "")
            g["c_id"]  = ch_id

            airings.append(g)

    return airings


def epg_advanced_links(data, session, settings, programmes, headers={}):
    url_list = []
    
    for i in programmes:
        if len(i.split("|")) > 1:
            url_list.append(
                {"url": f"https://www.{data['domain']}/tv-programm/sendung/{i.split('|')[1]}.html",
                "name": i, "uid": i.split("|")[1]})
        else:
            url_list.append(
                {"url": f"https://www.{data['domain']}/tv-programm/sendung/{i}.html",
                "name": i, "uid": i})
    
    return url_list


def epg_advanced_converter(item, data, cache, settings):
    
    def correct_num(string_item):
        try:
            return int(string_item), None
        except:
            if string_item[-1].isalpha():
                alphabet = string.ascii_lowercase
                return int(string_item[:-1]), alphabet.find(string_item[-1])+1
            else:
                return None, None
    
    p = BeautifulSoup(cache[0], 'html.parser')
    
    g = dict()
    g["b_id"] = item

    t  = p.find("h1", {"class": "headline--article"}).get_text()
    et = p.find("h2", {"class": "broadcast-info"})
    if et and f"Mehr zu {t}" not in et:
        g["subtitle"] = et.get_text()
    
    desc = p.find("section", {"class": "broadcast-detail__description"})
    if desc:
        d_sections = desc.findAll("p")
        g["desc"] = "\n\n".join([d.get_text() for d in d_sections])

    img = p.find("section", {"class": "broadcast-detail__stage"}).find("img")
    if img:
        g["image"] = img["src"]

    star = p.find("div", {"class": "content-rating__imdb-rating__rating-value"})
    if star:
        g["star"] = {"system": "IMDb", "value": f"{str(star.get_text().replace(',', '.'))}/10"}

    age = p.find("span", {"class": "children-age"})
    if age:
        g["rating"] = {"system": "FSK", "value": age.get_text().replace("FSK ", "")}

    series = p.find("section", {"class": "serial-info"})
    if series:
        s_num = None
        e_num = None
        p_num = None

        se_info = series.find("span").get_text().split(", ")
        if "Staffel " in se_info[0]:
            s_num = se_info[0].replace("Staffel ", "")
        if len(se_info) == 1 and "Folge " in se_info[0]:
            e_num, p_num = correct_num(se_info[0].replace("Folge ", ""))
        elif len(se_info) > 1 and "Folge " in se_info[1]:
            e_num_fix = se_info[1].replace("Folge ", "").split("/")[0].split("+")[0].split(";")[0].split(",")[0].split("-")[0]
            if "." in e_num_fix: e_num_fix = e_num_fix.split(".")[1]
            e_num, p_num = correct_num(e_num_fix)

        g["season_episode_num"] = {"season": s_num, "episode": e_num, "part": p_num}

    directors = []
    actors = []

    def_list = p.findAll("div", {"class": "definition-list"})
    for i in def_list:
        headlines = i.findAll("p", {"class": "headline"})
        list_items = i.findAll("dl")

        for n, h in enumerate(headlines):
            if h.get_text() == "Infos":
                for m, j in enumerate(list_items[n].findAll("dt")):
                    if j.get_text() == "Land":
                        g["country"] = list_items[n].findAll("dd")[m].get_text()
                    if j.get_text() == "Jahr":
                        g["date"] = int(list_items[n].findAll("dd")[m].get_text()[:4])

            if h.get_text() == "Crew":
                for m, j in enumerate(list_items[n].findAll("dt")):
                    if j.get_text().replace("\n", "").replace("\r", "").replace("  ", "") in ["Regie", "Drehbuch"]:
                        director = list_items[n].findAll("dd")[m].get_text().replace("\n", "").replace("\r", "").replace("  ", "")
                        director = director[:-1] if director[-1] == " " else director
                        if director not in directors:
                            directors.append(director)

            if h.get_text() == "Cast":
                for actor in list_items[n].findAll("dd"):
                    a = actor.get_text().replace("\n", "").replace("\r", "").replace("  ", "")
                    a = a[:-1] if a[-1] == " " else a
                    actors.append(a)

    g["credits"] = {"director": directors, "actor": actors}

    return [g]
