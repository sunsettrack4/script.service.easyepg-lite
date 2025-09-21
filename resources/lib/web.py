from resources.lib import tools
from bottle import  request, route, run, static_file
from datetime import datetime
from threading import Event
import json, os, requests, signal, traceback


stopFlag = Event()


class WebServer():
    def __init__(self, g, f):
        self.g = g
        self.f = f

    def start(self):
        init_config(self.g, self.f)
        run(host='0.0.0.0', port=4000, debug=False, quiet=True)

    def stop_kodi(self):
        # IT'S NOT THE BEST SOLUTION... BUT IT WORKS.
        if self.g.grabbing:
            self.g.cancellation = True
            self.g.pr.cancellation = True
            self.g.exit = True
            self.g.pr.exit = True
        requests.get("http://localhost:4000")

    def kill(self):
        pid = os.getpid()
        os.kill(pid, signal.SIGINT)

def init_config(v, w):
    global f, g, t
    g = v
    f = w
    t = tools.API(g.user_db.main["settings"]["api_key"], g.user_db.main["channels"], f)

def print_error(exception):
    try:
        print(exception)
    except:
        pass

# WEB PAGES
@route("/")
def index():
    return static_file("index.html", root=f"{f['included']}resources/data/html")

# API CALLS
@route("/api/key_check", method="POST")
def key_check():
    key_content = json.loads(request.body.read()).get("key", None)
    check_result = t.key_check(key_content)
    if check_result:
        if key_content:
            g.user_db.main["settings"]["api_key"] = key_content
            g.user_db.save_settings()
        return json.dumps({"success": True})
    else:
        return json.dumps({"success": False})

@route("/api/listings", method="GET")
def listings():
    return g.user_db.main["channels"]

@route("/api/settings", method="GET")
def get_settings():
    return g.user_db.main["settings"]

@route("/api/save_settings", method="POST")
def save_settings():
    if g.grabbing:
        return json.dumps({"success": False, "message": "The grabber process needs to be finished first."})
    try:
        i = json.loads(request.body.read())
        for item in i.keys():
            g.user_db.main["settings"][item] = i[item]
        g.user_db.save_settings()
        return json.dumps({"success": True})
    except Exception as e:
        print_error(traceback.format_exc())
        return json.dumps({"success": False, "message": f"Operation failed: {e}"})

@route("/api/search", method="POST")
def search():
    i = json.loads(request.body.read())
    return t.search_channel(i.get("value"), 
        request.get_header("accept-language").split(",")[0], i.get("type"))

@route("/api/lineups", method="POST")
def get_lineups():
    r = json.loads(request.body.read())
    return t.get_lineups(r.get("country"), r.get("code"))

@route("/api/lineup_channels", method="POST")
def get_lineup_channels():
    return t.get_lineup_channels(json.loads(request.body.read()).get("id"))

@route("/api/xmltv_lineups/add", method="POST")
def add_xmltv_lineup():
    values = json.loads(request.body.read())
    result = g.pr.ch_loader("xmltv", {"url": values.get("link")})
    if result[0] and len(result[1].keys()):
        l = str(int(datetime.now().timestamp()))
        g.user_db.main["xmltv"][f"xml{l}"] = {"name": values.get("name", f"XML FILE {l}"), "link": values["link"]}
        g.user_db.save_settings()
        return json.dumps({"success": True, "message": f"XMLTV added: {len(result[1].keys())} channel(s) found!"})
    return json.dumps({"success": False, "message": "The resource could not be verified."})

@route("/api/xmltv_lineups/get", method="GET")
def get_xmltv_lineups():
    return json.dumps({"success": True, "result": g.user_db.main["xmltv"]})

@route("/api/xmltv_lineups/remove", method="POST")
def remove_xmltv_lineup():    
    provider = json.loads(request.body.read()).get("id", "")
    try:
        l = len([i for i in g.user_db.main["channels"].keys() if g.user_db.main["channels"][i].get("provider_id", "") == provider])
        if l > 0:
            return json.dumps({"success": False, "message": "Please remove the affected channels first."})
        else:
            del g.user_db.main["xmltv"][provider]
            g.user_db.save_settings()
            return json.dumps({"success": True})
    except:
        return json.dumps({"success": False, "message": "The XMLTV does not exist."})

@route("/api/xmltv_lineup_channels", method="POST")
def get_xmltv_lineup_channels():
    provider = json.loads(request.body.read()).get("id", "")
    try:
        if "xml" in provider:
            result = g.pr.ch_loader("xmltv", {"url": g.user_db.main["xmltv"][provider]["link"]})
        else:
            result = g.pr.ch_loader(provider)
        
        if result[0]:
            for i in result[1].keys():
                if g.user_db.main["channels"].get(f"{provider}_{i}"):
                    result[1][i]["chExists"] = True
                else:
                    result[1][i]["chExists"] = False
                result[1][i]["provider_id"] = provider
            return json.dumps({"success": True, "result": result[1]})
        else:
            return json.dumps({"success": False, "message": f"An error occured: {str(result[1])}"})        
    except Exception as e:
        print_error(traceback.format_exc())
        return json.dumps({"success": False, "message": "Failed to load the channels."})

@route("/api/replace-id", method="POST")
def replace_channel():
    if g.grabbing:
        return json.dumps({"success": False, "message": "The grabber process needs to be finished first."})
    i = json.loads(request.body.read())
    n = json.loads(t.get_channel_info(i.get("new_id")))
    if n["success"]:
        if len(n["result"]) > 0 and n["result"][0].get("stationId") == i.get("new_id"):
            b = g.user_db.main["channels"][i.get("id")].get("tvg-id")
            del g.user_db.main["channels"][i.get("id")]
            g.user_db.main["channels"][i.get("new_id")] = n["result"][0]
            if b:
                g.user_db.main["channels"][i.get("new_id")]["tvg-id"] = b
            g.user_db.save_settings()
            return json.dumps({"success": True})
        else:
            return n

@route("/api/save_credentials", method="POST")
def save_credentials():
    if g.grabbing:
        return json.dumps({"success": False, "message": "The grabber process needs to be finished first."})
    
    file = json.loads(request.body.read())
    g.user_db.main["auth_data"][file["id"]] = {"user": file["user"], "pw": file["pw"]}
    g.user_db.save_settings()
    return json.dumps({"success": True, "message": "Credentials saved."})

@route("/api/add", method="POST")
def add_channel():
    d = dict()
    if g.grabbing:
        return json.dumps({"success": False, "message": "The grabber process needs to be finished first."})
    
    file = json.loads(request.body.read())

    try:
        if type(file) == list:
            if len(file) > 1 and file[0].get("stationId"):
                raise Exception("Lineup files are not supported.")
            elif file[0]["stationId"]:
                ids = [file[0]["stationId"]]
        else:
            ids = file["ids"]
            file = None
    except Exception as e:
        print_error(traceback.format_exc())
        return json.dumps({"success": False, "message": "The file could not be validated."})
    
    provider_id = ids[0].split("|")
    if len(provider_id) > 1:
        provider_id = provider_id[0]
    else:
        provider_id = False
    if not provider_id:
        try:
            for id in ids:
                i = json.loads(t.get_channel_info(id, file))
                if i["success"]:
                    if len(i["result"]) > 0 and i["result"][0].get("stationId") == id:
                        d[id] = i["result"][0]
        except Exception as e:
            print_error(traceback.format_exc())
            return json.dumps({"success": False, "message": "The channels could not be added."})
    else: 
        try:
            if "xml" in provider_id:
                ch_list = g.pr.ch_loader("xmltv", {"url": g.user_db.main["xmltv"][provider_id]["link"]})
            else:
                ch_list = g.pr.ch_loader(provider_id)
            if ch_list[0]:
                for id in ids:
                    if ch_list[1].get(id.split("|")[1]):
                        d[id.replace(f"{provider_id}|", f"{provider_id}_")] = \
                            {"stationId": id.replace(f"{provider_id}|", ""), "name": ch_list[1][id.split("|")[1]]["name"], "preferredImage": {"uri": ch_list[1][id.split("|")[1]].get("icon")}}
        except Exception as e:
            print_error(traceback.format_exc())
            return json.dumps({"success": False, "message": "The channels could not be added."})
    
    try:
        for cid in d.keys():
            g.user_db.main["channels"][cid] = d[cid]
        g.user_db.save_settings()
    except Exception as e:
        print_error(traceback.format_exc())
        return json.dumps({"success": False, "message": "Failed to save the channel list."})
    
    return json.dumps({"success": True})

@route("/api/remove", method="POST")
def remove_channels():
    if g.grabbing:
        return json.dumps({"success": False, "message": "The grabber process needs to be finished first."})
    try:
        ids = json.loads(request.body.read()).get("ids")
        for i in ids:
            if g.user_db.main["channels"].get(i):
                del g.user_db.main["channels"][i]
        g.user_db.save_settings()
        return json.dumps({"success": True})
    except Exception as e:
        print_error(traceback.format_exc())
        return json.dumps({"success": False, "message": f"Operation failed: {e}"})

@route("/api/check-tvgid", method="POST")
def check_tvg_id():
    try:
        if json.loads(request.body.read())["tvg-id"] in \
            [g.user_db.main["channels"][i].get("tvg-id", i) for i in g.user_db.main["channels"].keys()]:
                return json.dumps({"success": False, "message": "ID ALREADY EXISTS"})
        else:
            return json.dumps({"success": True})
    except Exception as e:
        print_error(traceback.format_exc())
        return json.dumps({"success": False, "message": f"Operation failed: {e}"})

@route("/api/add-tvgid", method="POST")
def add_tvg_id():
    if g.grabbing:
        return json.dumps({"success": False, "message": "The grabber process needs to be finished first."})
    i = json.loads(request.body.read())
    try:
        if g.user_db.main["channels"][i["id"]].get("tvg-id") and i["tvg-id"] == "":
            del g.user_db.main["channels"][i["id"]]["tvg-id"]
        else:
            g.user_db.main["channels"][i["id"]]["tvg-id"] = i["tvg-id"]
        g.user_db.save_settings()
        return json.dumps({"success": True})
    except Exception as e:
        print_error(traceback.format_exc())
        return json.dumps({"success": False, "message": f"Operation failed ({e})."})

@route("/api/channel_info", method="POST")
def get_channel_data():
    return t.get_channel_info(json.loads(request.body.read()).get("id"))

@route("/api/grabber-status", method="GET")
def grabber_status():
    return json.dumps({"success": True, "result": g.grabber_status()})

@route("/api/start-grabber", method="GET")
def start_grabber():
    g.grabbing = True
    return json.dumps({"success": True})

@route("/api/stop-grabber", method="GET")
def stop_grabber():
    g.cancellation = True
    g.pr.cancellation = True
    return json.dumps({"success": True})

@route("/download/<file_name>", method="GET")
def download_file(file_name):
    if file_name == "epg.xml" or file_name == "epg.xml.gz":
        return static_file(file_name, root=f"{f['storage']}xml/", download=file_name)
    else:
        return ""


#
# WEB FILES (CSS/JS/JSON/IMG)
#

@route("/app/data/css/<file_name>")
def provide_css(file_name):
    return static_file(file_name, root=f"{f['included']}resources/data/css")

@route("/app/data/js/<file_name>")
def provide_css(file_name):
    return static_file(file_name, root=f"{f['included']}resources/data/js")

@route("/app/data/img/<file_name>")
def provide_img(file_name):
    return static_file(file_name, root=f"{f['included']}resources/data/img")

@route("/app/data/json/<file_name>")
def provide_json(file_name):
    return static_file(file_name, root=f"{f['included']}resources/data/json")


#
# M3U PLAYLIST
#

@route("/api/playlist-m3u", method="POST")
def upload_m3u_file():
    m3u = request.body.read()
    try:
        tools.save_file(str(convert_codec(m3u)), f['storage'])
        g.user_db.main["settings"]["file"] = True
        if g.user_db.main["settings"].get("file_url"):
            del g.user_db.main["settings"]["file_url"]
        g.user_db.save_settings()
        m3u = tools.read_file(f['storage'])
        return json.dumps({"success": True, "result": convert_m3u(str(convert_codec(m3u)))})
    except Exception as e:
        print_error(traceback.format_exc())
        return json.dumps({"success": False, "message": str(e)})

@route("/api/playlist-m3u", method="GET")
def get_m3u_file():
    try:
        m3u = tools.read_file(f['storage'])
        return json.dumps({"success": True, "result": convert_m3u(str(convert_codec(m3u)))})
    except FileNotFoundError:
        return json.dumps({"success": False, "message": "No file found."})
    except Exception as e:
        print_error(traceback.format_exc())
        return json.dumps({"success": False, "message": str(e)})

@route("/api/playlist-link", method="POST")
def upload_m3u_link():
    try:
        l = json.loads(request.body.read())["link"]
        tools.save_file(str(convert_codec(load_m3u(l))), f['storage'])
        g.user_db.main["settings"]["file"] = True
        g.user_db.main["settings"]["file_url"] = l
        g.user_db.save_settings()
        m3u = tools.read_file(f['storage'])
        return json.dumps({"success": True, "result": convert_m3u(str(convert_codec(m3u)))})
    except Exception as e:
        print_error(traceback.format_exc())
        return json.dumps({"success": False, "message": str(e)})

@route("/api/playlist-link", method="GET")
def load_via_m3u_link():
    try:
        l = g.user_db.main["settings"]["file_url"]
        tools.save_file(str(convert_codec(load_m3u(l))), f['storage'])
        m3u = tools.read_file(f['storage'])
        return json.dumps({"success": True, "result": convert_m3u(str(convert_codec(m3u)))})
    except Exception as e:
        print_error(traceback.format_exc())
        return json.dumps({"success": False, "message": str(e)})

def convert_codec(text):
    if "\\x" in str(text):
        return text.decode('unicode_escape').encode('latin1').decode('utf-8')
    if "\\u" in str(text):
        return text.decode('utf-8')
    return text

def load_m3u(link):
    return requests.get(link, allow_redirects=True, timeout=3).content

def convert_m3u(file):
    ch_check = g.user_db.main["channels"]
    if "#EXTM3U" in file:
        ch_dict = dict()
        if "\n" in file:
            pre_process = file.split("#EXTM3U")[1].split("\n")
        else:
            pre_process = file.split("#EXTM3U")[1].split("\\n")
        for item in pre_process:
            item = item.replace("tvg-ID", "tvg-id")
            if "#EXTINF" in item and 'tvg-id="' in item and "," in item:
                tvg_id = item.split('tvg-id="')[1].split('"')[0]
                if tvg_id != "":
                    ch_dict[tvg_id] = {"name": item.replace(", ", ",").split(",")[1]}
            elif "#EXTINF" in item and "," in item:
                tvg_id = item.replace(", ", ",").split(",")[1]
                if tvg_id != "":
                    ch_dict[tvg_id] = {"name": tvg_id}
        for i in ch_check.keys():
            if ch_dict.get(ch_check[i].get("tvg-id", "")):
                ch_dict[ch_check[i]["tvg-id"]]["mapped"] = True
        return dict(sorted(ch_dict.items(), key=lambda t: str.casefold(t[0])))
