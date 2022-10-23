from cmath import exp
from resources.lib import tools
from bottle import  request, route, run, static_file
from threading import Event
import json, logging, os, requests, signal


logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

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
            self.g.exit = True
        requests.get("http://localhost:4000")

    def kill(self):
        pid = os.getpid()
        os.kill(pid, signal.SIGINT)

def init_config(v, w):
    global f, g, t
    g = v
    f = w
    t = tools.API(g.user_db.main["settings"]["api_key"], g.user_db.main["channels"], f)

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

@route("/api/add", method="POST")
def add_channel():
    if g.grabbing:
        return json.dumps({"success": False, "message": "The grabber process needs to be finished first."})
    ids = json.loads(request.body.read()).get("ids")
    for id in ids:
        try:       
            i = json.loads(t.get_channel_info(id))
            if i["success"]:
                if len(i["result"]) > 0 and i["result"][0].get("stationId") == id:
                    g.user_db.main["channels"][id] = i["result"][0]
                    g.user_db.save_settings()
        except:
            return json.dumps({"success": False, "message": "Not all channels could not be added."})
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
    return json.dumps({"success": True})

@route("/download/<file_name>", method="GET")
def download_file(file_name):
    if file_name == "epg.xml" or file_name == "epg.xml.gz":
        return static_file(file_name, root=f"{f['storage']}", download=file_name)
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


#
# M3U PLAYLIST
#

@route("/api/playlist-m3u", method="POST")
def upload_m3u_file():
    m3u = request.body.read()
    try:
        r = convert_m3u(str(convert_codec(m3u)))
        tools.save_file(str(convert_codec(m3u)), f['storage'])
        g.user_db.main["settings"]["file"] = True
        if g.user_db.main["settings"].get("file_url"):
            del g.user_db.main["settings"]["file_url"]
        g.user_db.save_settings()
        return json.dumps({"success": True, "result": r})
    except Exception as e:
        return json.dumps({"success": False, "message": str(e)})

@route("/api/playlist-m3u", method="GET")
def get_m3u_file():
    try:
        m3u = tools.read_file(f['storage'])
        return json.dumps({"success": True, "result": convert_m3u(str(convert_codec(m3u)))})
    except Exception as e:
        return json.dumps({"success": False, "message": str(e)})

@route("/api/playlist-link", method="POST")
def upload_m3u_link():
    try:
        l = json.loads(request.body.read())["link"]
        r = convert_m3u(str(convert_codec(load_m3u(l))))
        g.user_db.main["settings"]["file"] = True
        g.user_db.main["settings"]["file_url"] = l
        g.user_db.save_settings()
        return json.dumps({"success": True, "result": r})
    except Exception as e:
        return json.dumps({"success": False, "message": str(e)})

@route("/api/playlist-link", method="GET")
def load_via_m3u_link():
    try:
        return json.dumps({"success": True, "result": convert_m3u(str(load_m3u(g.user_db.main["settings"]["file_url"])))})
    except Exception as e:
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
            if "#EXTINF" in item and 'tvg-id="' in item and "," in item:
                tvg_id = item.split('tvg-id="')[1].split('"')[0]
                if tvg_id != "":
                    ch_dict[tvg_id] = {"name": item.replace(", ", ",").split(",")[1]}
        for i in ch_check.keys():
            if ch_dict.get(ch_check[i].get("tvg-id", "")):
                ch_dict[ch_check[i]["tvg-id"]]["mapped"] = True
        return dict(sorted(ch_dict.items(), key=lambda t: str.casefold(t[0])))
