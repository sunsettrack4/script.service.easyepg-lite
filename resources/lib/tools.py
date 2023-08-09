from datetime import datetime, timedelta
import json, os, requests


general_header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'}

class API():
    def __init__(self, key, channels, file_paths):
        self.key = key
        self.channels = channels
        self.file_paths = file_paths

    def grab_channel(self, channel_id, settings):
        time_start = datetime.now().strftime("%Y-%m-%dT06:00Z")
        time_end = (datetime.now() + timedelta(int(settings["days"]))).strftime("%Y-%m-%dT06:00Z")
        
        url = f"http://data.tmsapi.com/v1.1/stations/{channel_id}/airings?startDateTime={time_start}&endDateTime={time_end}&imageSize={settings['is']}&imageAspectTV={settings['it']}&api_key={settings['api_key']}"
        
        try:
            return json.loads(requests.get(url, headers=general_header).content)
        except:
            return {}
            
    def key_check(self, new_key):
        url = f"http://data.tmsapi.com/v1.1/stations/10359?lineupId=USA-TX42500-X&api_key={str(new_key) if new_key is not None else str(self.key)}"

        try:
            s = json.loads(requests.get(url, headers=general_header).content)
            if new_key is not None:
                self.key = new_key
            return True
        except (json.JSONDecodeError, requests.HTTPError):
            return False

    def search_channel(self, value, lang, f_type):
        if f_type == "chid":
            c = json.loads(self.get_channel_info(value))
            if c["success"]:
                n = {"hitCount": 1, "hits": [{"station": c["result"][0]}]}
            else:
                n = {"hitCount": 0, "hits": []}
            return json.dumps({"success": True, "result": n})

        f_type = "name" if f_type == "chname" else "callsign"

        url = f"https://data.tmsapi.com/v1.1/stations/search?q={value}&limit=100&queryFields={f_type}" \
              f"&api_key={self.key}"

        try:
            s = requests.get(url, headers=general_header)
            a = []
            r = json.loads(s.content)
            for i in r["hits"]:
                if i["station"].get("stationId"):
                    if self.channels.get(i["station"]["stationId"]):
                        i["station"]["chExists"] = True
                    else:
                        i["station"]["chExists"] = False
                    if i["station"].get("bcastLangs") and i["station"]["bcastLangs"][0] in (lang.split("-")[0], lang) and value.lower() == i["station"]["name"].lower():
                        a.insert(0, i)
                    elif not i["station"].get("bcastLangs"):
                        i["station"]["bcastLangs"] = ["NONE"]
                        a.append(i)
                    else:
                        a.append(i)
            return json.dumps({"success": True, "result": {"hitCount": r["hitCount"], "hits": a}})
        except (json.JSONDecodeError, requests.HTTPError):
            return json.dumps({"success": False, 
                "message": s.headers.get("X-Mashery-Error-Code", str(s.status_code))})
        except:
            return json.dumps({"success": False, "message": "Connection error."})

    def get_channel_info(self, value):
        if os.path.exists(f"{self.file_paths['storage']}cache/station_{value}.json"):
            with open(f"{self.file_paths['storage']}cache/station_{value}.json", "r") as f:
                i = json.load(f)
                if self.channels.get(i[0]["stationId"]):
                    i[0]["chExists"] = True
                else:
                    i[0]["chExists"] = False
                return json.dumps({"success": True, "result": i})
        
        url = f"https://data.tmsapi.com/v1.1/stations/{value}?imageSize=Md" \
              f"&api_key={self.key}"

        try:
            s = requests.get(url, headers=general_header)
            r = json.loads(s.content)
            if type(r) != list and r.get("errorCode"):
                return json.dumps({"success": False, "message": f"Channel not found (Code: {r['errorCode']})."})
            else:
                with open(f"{self.file_paths['storage']}cache/station_{value}.json", "w") as f:
                    json.dump(r, f)
                for n, i in enumerate(r):
                    if self.channels.get(i["stationId"]):
                        r[n]["chExists"] = True
                    else:
                        r[n]["chExists"] = False
                return json.dumps({"success": True, "result": r})
        except (json.JSONDecodeError, requests.HTTPError):
            return json.dumps({"success": False, 
                "message": s.headers.get("X-Mashery-Error-Code", str(s.status_code))})
        except:
            return json.dumps({"success": False, "message": "Connection error."})

    def get_lineups(self, country, code):
        url = f"https://data.tmsapi.com/v1.1/lineups?country={country.upper()}&postalCode={code}" \
              f"&api_key={self.key}"
        
        try:
            s = requests.get(url, headers=general_header)
            r = json.loads(s.content)
            if type(r) != list and r.get("errorCode"):
                return json.dumps({"success": False, "message": f"Lineups not found (Code: {r['errorCode']})."})
            else:
                return json.dumps({"success": True, "result": r})
        except (json.JSONDecodeError, requests.HTTPError):
            return json.dumps({"success": False, 
                "message": s.headers.get("X-Mashery-Error-Code", str(s.status_code))})
        except:
            return json.dumps({"success": False, "message": "Connection error."})

    def get_lineup_channels(self, id):
        url = f"https://data.tmsapi.com/v1.1/lineups/{id}/channels?imageSize=Md&enhancedCallSign=true" \
              f"&api_key={self.key}"

        try:
            s = requests.get(url, headers=general_header)

            r = json.loads(s.content)
            if type(r) != list and r.get("errorCode"):
                return json.dumps({"success": False, "message": f"Lineup channels not found (Code: {r['errorCode']})."})
            else:
                for n, i in enumerate(r):
                    if self.channels.get(i["stationId"]):
                        r[n]["chExists"] = True
                    else:
                        r[n]["chExists"] = False
                return json.dumps({"success": True, "result": {i["stationId"]: i for i in r}})
        except (json.JSONDecodeError, requests.HTTPError):
            return json.dumps({"success": False, 
                "message": s.headers.get("X-Mashery-Error-Code", str(s.status_code))})
        except:
            return json.dumps({"success": False, "message": "Connection error."})


def save_file(file, path):
    with open(f"{path}playlist.m3u", "w") as f:
        f.write(file)
    return True

def read_file(path):
    with open(f"{path}playlist.m3u", "r") as f:
        return f.read()
