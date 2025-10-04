from datetime import datetime, timedelta, timezone
import json, time

def epg_main_links(data, channels, settings, session, headers):
    url_list = []
    today = datetime.today()

    days = int(settings["days"]) if int(settings["days"]) < 10 else 9
    
    for day in range(days):
        time_start = ((datetime(today.year, today.month, today.day, 6, 0, 0).replace(tzinfo=timezone.utc)
                           + timedelta(days=day))).strftime("%Y-%m-%dT06:00:00.000Z")
        time_end = ((datetime(today.year, today.month, today.day, 5, 59, 0).replace(tzinfo=timezone.utc)
                         + timedelta(days=(day + 1)))).strftime("%Y-%m-%dT05:59:00.000Z")
        
        x = 0
        pre_list = []
        for i in channels:
            pre_list.append(i)
            x = x + 1
            if x < 20:
                continue
            else:
                pre_list_string = ",".join(pre_list)
                url_list.append(
                    {"url": f"https://www.tvtv.us/api/v1/lineup/USA-FL67387-X/grid/{time_start}/{time_end}/{pre_list_string}",
                    "h": headers, "c": pre_list_string})
                pre_list = []
                x = 0
        if x != 0:
            pre_list_string = ",".join(pre_list)
            url_list.append(
                {"url": f"https://www.tvtv.us/api/v1/lineup/USA-FL67387-X/grid/{time_start}/{time_end}/{pre_list_string}",
                "h": headers, "c": pre_list_string})
    
    return url_list

def epg_main_converter(item, data, channels, settings, ch_id=None, genres={}):
    item = json.loads(item)
    airings = []
    
    ch_list = ch_id.split(",")
    
    for n, ch in enumerate(item):

        for programme in ch:
        
            g = dict()

            g["c_id"]               = ch_list[n]
            g["start"]              = str(int(datetime(*(time.strptime(programme["startTime"], "%Y-%m-%dT%H:%MZ")[0:6])).timestamp()))
            g["end"]                = str(int((datetime(*(time.strptime(programme["startTime"], "%Y-%m-%dT%H:%MZ")[0:6])) + timedelta(minutes=programme["duration"])).timestamp()))
            g["title"]              = programme["title"]
            g["subtitle"]           = programme.get("subtitle")
            g["b_id"]               = f'{programme["programId"]}_{g["start"]}_{g["end"]}_{g["c_id"]}'

            airings.append(g)

    return airings
