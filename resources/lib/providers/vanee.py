from datetime import datetime, timedelta
import json, re, requests


main_url = "https://vantagetv.ee"

def channels(data, session, headers={}):
    chlist = {}

    channel_url = f"{main_url}/data.php"
    
    channel_page = requests.get(channel_url, timeout=5, headers=headers)
    channel_data = channel_page.json()

    for channel in channel_data["streams"]:
        channel_name = channel["name"]
        channel_id = channel["id"]
        channel_logo = f"{main_url}/{channel['thumbnail']}"
        chlist[channel_id] = {"name": channel_name, "icon": channel_logo}

    return chlist


def epg_main_links(data, channels, settings, session, headers):
    url_list = []
    
    url_list.append({"url": f"{main_url}/data.php"})
    
    return url_list


def epg_main_converter(item, data, channels, settings, ch_id=None, genres={}):
    item = json.loads(item)
    airings = []
    
    schedule_data = {}
    weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    
    # Convert schedule string item into JSON format
    for channel in item["streams"]:
        schedule = channel["schedule"].split("\n")
        schedule_data[channel["id"]] = {}

        actual_key = None

        for i in schedule:
            
            if i.replace(":", "") in weekdays:
                actual_key = i.replace(":", "")
                schedule_data[channel["id"]][actual_key] = {}

            elif i.split(" - ")[0] in weekdays:
                actual_key = [i.split(" - ")[0], i.split(" - ")[1].replace(":", "")]
                a_1 = weekdays.index(actual_key[0])
                a_2 = weekdays.index(actual_key[1])
                actual_key = weekdays[a_1:a_2+1]

            elif re.match("[0-2][0-9]:[0-9][0-9] ", i):
                t = i.split(" ")[0]
                b = " ".join(i.split(" ")[1:])
                if type(actual_key) == str:
                    schedule_data[channel["id"]][actual_key][t] = b
                elif type(actual_key) == list:
                    for w in actual_key:
                        if not schedule_data[channel["id"]].get(w):
                            schedule_data[channel["id"]][w] = {}
                        schedule_data[channel["id"]][w][t] = b
                else:
                    for w in weekdays:
                        if not schedule_data[channel["id"]].get(w):
                            schedule_data[channel["id"]][w] = {}
                        schedule_data[channel["id"]][w][t] = b

    # Create airing items based on schedule
    for c in channels:
        
        for day in range(int(settings["days"])):

            t1 = (datetime.today() + timedelta(days=day))
            t2 = (datetime.today() + timedelta(days=day+1))

            if schedule_data[c].get(weekdays[t1.weekday()]):
                for n, b in enumerate(schedule_data[c][weekdays[t1.weekday()]].keys()):
                
                    g = dict()

                    g["c_id"]               = c
                    
                    g["start"]              = str(int(t1.replace(hour=int(b.split(":")[0].replace("00", "0")), minute=int(b.split(":")[1].replace("00", "0")), second=0).timestamp()))
                    
                    if len(schedule_data[c][weekdays[t1.weekday()]].keys()) > n+1:
                        nb = list(schedule_data[c][weekdays[t1.weekday()]].keys())[n+1]
                        g["end"] = str(int(t1.replace(hour=int(nb.split(":")[0].replace("00", "0")), minute=int(nb.split(":")[1].replace("00", "0")), second=0).timestamp()))
                    else:
                        try:
                            nb = list(schedule_data[c][weekdays[t2.weekday()]].keys())[0]
                            g["end"] = str(int(t2.replace(hour=int(nb.split(":")[0].replace("00", "0")), minute=int(nb.split(":")[1].replace("00", "0")), second=0).timestamp()))
                        except KeyError:
                            nb = "23:59"
                            g["end"] = str(int(t2.replace(hour=int(nb.split(":")[0].replace("00", "0")), minute=int(nb.split(":")[1].replace("00", "0")), second=0).timestamp()))

                    g["title"]              = schedule_data[c][weekdays[t1.weekday()]][b]
                    g["genres"]             = ["Music"]

                    g["b_id"]               = f"{c}_{g['start']}"

                    airings.append(g)

    return airings