from datetime import datetime, timedelta
from importlib import util
from time import sleep
import concurrent.futures, json, os, sqlite3, subprocess, sys, traceback

try: 
    from curl_cffi import requests
except:
    import requests

from platform import system

if "Windows" in system() and os.path.isfile("curl.exe"):
    curl = "curl.exe"
elif "Linux" in system() and os.path.isfile("curl"):
    curl = f"./curl"
    try:
        os.chmod("curl", 0o775)
    except:
        print("fatal: wrong permissions on easyepg folder.")
else:
    curl = "curl"

general_header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                                'Chrome/140.0.0.0 Safari/537.36'}

class UserData():
    def __init__(self, file_paths):
        self.file_paths = file_paths
        self.create_cache()
        self.import_data()

    def create_cache(self):
        if not os.path.exists(f"{self.file_paths['storage']}cache"):
            os.mkdir(f"{self.file_paths['storage']}cache")

    def import_data(self):
        try:
            with open(f"{self.file_paths['storage']}settings.json", "r") as f:
                self.main = json.load(f)
        except:
            self.main = dict()

        try:
            with open(f"{self.file_paths['included']}resources/data/json/genres.json", "r", encoding="UTF-8") as f:
                self.genres = json.load(f)
        except:
            self.genres = dict()

        # Init default settings
        if "channels" not in self.main:
            self.main["channels"] = {}
        if "settings" not in self.main:
            self.main["settings"] = {"api_key": None, "days": "7", "rm": "none", "is": "Md", "it": "16x9", "at": "fsk", "rate": "0", "ut": "04:00", "ag": "no", "file": False, "dl_threads": 1, "pn_max": 50000}
        if "auth_data" not in self.main:
            self.main["auth_data"] = {}
        if "sessions" not in self.main:
            self.main["sessions"] = {}
        if "xmltv" not in self.main:
            self.main["xmltv"] = {}
        if "provider_settings" not in self.main:
            self.main["provider_settings"] = {}
        
        # Check settings / insert default values (if needed)
        if self.main["settings"].get("ut", "") == "":
            self.main["settings"]["ut"] = "04:00"
            self.save_settings()
        
        return True

    
    def save_settings(self):
        with open(f"{self.file_paths['storage']}settings.json", "w") as f:
            json.dump(self.main, f)
        return True

class SQLiteEPGManager():
    def __init__(self, config, file_path):
        self.config = config
        self.file_path = file_path
        self.init_db()

    def init_db(self):
        self.conn = sqlite3.connect(f"{self.file_path}epg.db", check_same_thread=False)
        self.c = self.conn.cursor()
        return

    def create_epg_db(self, provider, pre_load):
        self.c.execute("""CREATE TABLE IF NOT EXISTS {}"""
                       """(channel_id TEXT, broadcast_id TEXT PRIMARY KEY, start INTEGER, end INTEGER,"""
                       """ title TEXT, subtitle TEXT, desc TEXT, image TEXT, date TEXT, country TEXT,"""
                       """ star TEXT, rating TEXT, credits TEXT, season_episode_num TEXT,"""
                       """ genres TEXT, qualifiers TEXT, advanced INTEGER, db_link TEXT)""".format(f"pre_{provider}" if pre_load else provider))
        self.confirm_update()
        return
    
    def remove_epg_db(self, provider, pre_load):
        try:
            self.c.execute("""DROP TABLE {}""".format(f"pre_{provider}" if pre_load else provider))
            self.confirm_update()
        except:
            pass
        return

    def retrieve_epg_db_items(self, provider, channel):
        self.c.execute("""SELECT channel_id, broadcast_id, start, end, title, subtitle, desc, """
                        """image, date, country, star, rating, credits, season_episode_num, genres, qualifiers, advanced"""
                        """ FROM {} WHERE channel_id = ? ORDER BY start ASC""".format(provider),
                       (channel,))
        return self.c.fetchall()
    
    def write_epg_db_items(self, provider, to_be_added, pre_load):
        [self.c.execute("""INSERT OR REPLACE INTO {} """
                        """(channel_id, broadcast_id, start, end, title, subtitle, desc, """
                        """image, date, country, star, rating, credits, season_episode_num, genres, qualifiers, advanced, db_link)"""
                        """VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""".format(f"pre_{provider}" if pre_load else provider),
                        (channel_id, broadcast_id, start, end, title, subtitle, desc, 
                         image, date, country, json.dumps(star), json.dumps(rating), json.dumps(credits), 
                         json.dumps(season_episode_num), json.dumps(genres), json.dumps(qualifiers), 0, None))
        for channel_id, broadcast_id, start, end, title, subtitle, desc, image, date,
            country, star, rating, credits, season_episode_num, genres, qualifiers in to_be_added]
        return
    
    def remove_epg_db_items(self, provider, to_be_removed):
        [self.c.execute("""DELETE FROM {} WHERE broadcast_id = ?""".format(provider), [broadcast_id]) 
        for broadcast_id in to_be_removed]
        return

    def update_epg_db_items(self, provider, to_be_updated, advanced):
        [self.c.execute("""UPDATE {} SET start = coalesce(?, start), end = coalesce(?, end), """
                        """title = coalesce(?, title), subtitle = coalesce(?, subtitle), """
                        """desc = coalesce(?, desc), image = coalesce(?, image), """
                        """date = coalesce(?, date), country = coalesce(?, country), star = coalesce(?, star), rating = coalesce(?, rating), """
                        """credits = coalesce(?, credits), season_episode_num = coalesce(?, season_episode_num), """
                        """genres = coalesce(?, genres), qualifiers = coalesce(?, qualifiers), advanced = {} """
                        """WHERE broadcast_id = ?""".format(provider, 1 if advanced else 0),
                        (start, end, title, subtitle, desc, image, date, country, 
                         json.dumps(star) if star != "{}" else None, json.dumps(rating) if rating != "{}" else None,
                         json.dumps(credits) if credits != "{}" else None, json.dumps(season_episode_num) if season_episode_num != "{}" else None, 
                         json.dumps(genres) if genres != "[]" else None, json.dumps(qualifiers) if qualifiers != "[]" else None, broadcast_id))
        for channel_id, broadcast_id, start, end, title, subtitle, desc, image, date, country, star, rating,
            credits, season_episode_num, genres, qualifiers in to_be_updated]
        return

    def simple_epg_db_update(self, provider, days):
        self.c.execute("""SELECT channel_id from {}""".format(f"pre_{provider}"))
        new_channels = [item[0] for item in self.c.fetchall()]

        self.c.execute("""SELECT channel_id from {}""".format(provider))
        old_channels = [item[0] for item in self.c.fetchall()]

        channel_set = set(list(dict.fromkeys(new_channels + old_channels)))
        del new_channels, old_channels

        ch_list = []
        channel_queries = []
        for i in channel_set:
            ch_list.append(f"'{i}'")
            if len(ch_list) == self.config["xmltv" if "xml" in provider else provider].get("max_ch_queries", 100):
                channel_queries.append(', '.join(map(str, ch_list)))
                ch_list = []
        if len(ch_list) > 0:
            channel_queries.append(', '.join(map(str, ch_list)))
        
        channel_set = set(channel_queries)
        del channel_queries

        advanced_to_be_loaded = []

        for channel in channel_set:
            self.c.execute("""SELECT broadcast_id FROM {} WHERE channel_id IN ({})""".format(f"pre_{provider}", channel))
            new_set = set([item[0] for item in self.c.fetchall()])

            self.c.execute("""SELECT broadcast_id FROM {} WHERE advanced = 0 AND channel_id IN ({})""".format(provider, channel))
            cached_broadcasts = [item[0] for item in self.c.fetchall()]

            self.c.execute("""SELECT broadcast_id FROM {} WHERE advanced = 1 AND channel_id IN ({})""".format(provider, channel))
            cached_advanced_broadcasts = [item[0] for item in self.c.fetchall()]

            self.remove_epg_db_items(provider, [item for item in cached_broadcasts + cached_advanced_broadcasts if item not in new_set])
            del new_set

            old_main_set = set(cached_broadcasts)
            old_advanced_set = set(cached_advanced_broadcasts)
            old_set = set(cached_broadcasts + cached_advanced_broadcasts)
            del cached_broadcasts, cached_advanced_broadcasts

            self.c.execute("""SELECT channel_id, broadcast_id, start, end, title, subtitle, """
                            """desc, image, date, country, star, rating, credits, season_episode_num, genres, qualifiers """
                            """FROM {} WHERE channel_id IN ({})""".format(f"pre_{provider}", channel))
            new_broadcasts_items = [item for item in self.c.fetchall()]

            self.update_epg_db_items(provider, [item for item in new_broadcasts_items if item[1] in old_main_set], False)
            del old_main_set

            self.update_epg_db_items(provider, [item for item in new_broadcasts_items if item[1] in old_advanced_set], True)
            
            self.write_epg_db_items(provider, [item for item in new_broadcasts_items if item[1] not in old_set], False)
            del old_set

            today = datetime.today()
            max_time = int((datetime(today.year, today.month, today.day, 6, 0, 0) + timedelta(days=days)).timestamp())
            advanced_to_be_loaded.extend([item[1] for item in new_broadcasts_items if item[1] not in old_advanced_set and item[2] <= max_time] if days > 0 else [])
            del new_broadcasts_items, old_advanced_set

        self.confirm_update()

        self.remove_epg_db(provider, True)

        return advanced_to_be_loaded
    
    def confirm_update(self):
        self.conn.commit()
        self.c.execute("""VACUUM""")

class SQLiteChannelManager():

    def __init__(self, config, file_path):
        self.ch_config = config
        self.ch_file_path = file_path
        self.init_ch_db()
        # self.load_cache()

    def init_ch_db(self):
        self.ch_conn = sqlite3.connect(f"{self.ch_file_path}resources/data/db/channels.db", check_same_thread=False)
        self.ch_c = self.ch_conn.cursor()
        self.create_channel_db()
        return
    
    def get_channel(self, station_id):
        self.ch_c.execute("""SELECT config FROM channels WHERE channel_id = '{}'""".format(station_id))
        return [item for item in self.ch_c.fetchall()]
    
    def search_channel(self, search_query):
        self.ch_c.execute("""SELECT * FROM channels WHERE channel_name LIKE '{}%'""".format(search_query))
        return [item for item in self.ch_c.fetchall()]
    
    def load_cache(self):
        for file in os.listdir(f"{self.ch_file_path}cache"):
            if "station_" in file or "station-" in file:
                with open(f"{self.ch_file_path}cache/{file}", "r", encoding="UTF-8") as f:
                    try:
                        self.update_channel_db("station", "Gracenote TMS", json.load(f))
                    except:
                        pass
    
    def create_channel_db(self):
        self.ch_c.execute("""CREATE TABLE IF NOT EXISTS channels"""
                       """(channel_id TEXT PRIMARY KEY, channel_name TEXT, provider_name TEXT, provider_id TEXT, country TEXT, config TEXT)""")
        self.confirm_ch_update()
        return
    
    def update_channel_db(self, file_type, provider_name, ch_list):
        if file_type == "lineup":
            self.remove_channel_db_items(provider_name)
            [ch_list[channel].update({"stationId": channel}) for channel in ch_list.keys()]
            [self.ch_c.execute("""INSERT OR REPLACE INTO channels """
                            """(channel_id, channel_name, provider_name, provider_id, country, config) """
                            """VALUES (?, ?, ?, ?, ?, ?)""",
                            (f'{provider_name}_{channel}', ch_list[channel]["name"], 
                             self.ch_config[provider_name]["name"], provider_name,
                             self.ch_config[provider_name]["country"], json.dumps(ch_list[channel])))
            for channel in ch_list.keys()]
        if file_type == "station":
            station = ch_list[0]
            self.ch_c.execute("""INSERT OR REPLACE INTO channels """
                            """(channel_id, channel_name, provider_name, provider_id, country, config) """
                            """VALUES (?, ?, ?, ?, ?, ?)""",
                            (station["stationId"], station["name"], "Gracenote TMS", "gntms", None, json.dumps(ch_list[0])))
        self.confirm_ch_update()
        return
    
    def remove_channel_db_items(self, provider):
        self.ch_c.execute("""DELETE FROM channels WHERE provider_id = '{}'""".format(provider))
        return
    
    def confirm_ch_update(self):
        self.ch_conn.commit()
        self.ch_c.execute("""VACUUM""")

class ProviderManager():
    
    def __init__(self, file_paths, user_db):
        self.file_paths = file_paths
        self.user_db = user_db
        self.import_data()
        self.epg_db = SQLiteEPGManager(self.providers, file_paths["storage"])
        self.channel_db = SQLiteChannelManager(self.providers, file_paths["included"])
        self.import_provider_modules()
        self.error_cache = []

    # ERROR LOG
    def print_error_cache(self, provider):
        try:
            if len(self.error_cache) > 0:
                with open(f"{self.file_paths['storage']}grabber_error_log.txt", "a+") as log:
                    log.write(f"--- {provider.upper()} WARNING LOG: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ---\n")
                    for i in self.error_cache:
                        log.write(i+"\n")
                    log.write(f"--- {provider.upper()} WARNING LOG END ---\n\n")
        except:
            pass
        self.error_cache = []

    # PROVIDER CONFIG
    def import_data(self):
        with open(f"{self.file_paths['included']}resources/data/json/providers.json", "r", encoding="UTF-8") as f:
            self.providers = json.load(f)
        return

    # PROVIDER MODULES        
    def import_provider_modules(self):
        modules = []
        [modules.append(self.providers[i].get("module", i)) for i in self.providers.keys()
         if self.providers[i].get("module", i) not in modules]
        for i in modules:
            spec = util.spec_from_file_location(i, f"{self.file_paths['included']}resources/lib/providers/{i}.py")
            module = util.module_from_spec(spec)
            sys.modules[i] = module
            spec.loader.exec_module(module)
        return

    # PROVIDER LOGIN
    def login(self, provider_name, data=None):
        data = self.providers[provider_name].get("data") if not data else data
        auth_data = {}

        if not self.providers[provider_name].get("login_req"):
            return True
        if self.providers[provider_name].get("auth_req"):
            auth_data = {"key": self.user_db.main["settings"].get("api_key")} if provider_name == "gntms" \
                else self.user_db.main["auth_data"].get(provider_name)
            if not auth_data:
                return False, "No key found" if self.providers[provider_name].get("auth_type", "") == "api_key" else "No credentials found"
            session = self.user_db.main["sessions"].get(provider_name)
            if session:
                if session.get("expiration", False) is False or session.get("expiration", 0) > datetime.now().timestamp():
                    if provider_name != "gntms" or self.user_db.main["sessions"].get(provider_name)["session"]["key"] == auth_data["key"]:
                        return True
   
        try:          
            session = sys.modules[self.providers[provider_name].get("module", provider_name)].login(
                data, auth_data, general_header)
            if not session[0]:
                return False, session[1]["message"]
            exp = (datetime.now().timestamp() + self.providers[provider_name]["exp"]) if self.providers[provider_name].get("exp") else False
            self.user_db.main["sessions"][provider_name] = {"session": session[1], "expiration": exp}
            self.user_db.save_settings()
            return True
        except Exception as e:
            if len(self.error_cache) <= 50:
                self.error_cache.append(f"{provider_name}: Login module error - {str(traceback.format_exc())}")
            return False, "Login module error"
        
    # LOAD CHLIST
    def ch_loader(self, provider_name, data={}):
        try:
            with open(f"{self.file_paths['storage']}cache/lineup_{provider_name}.json", "r") as file:
                f = json.load(file)
            if f["date"] == datetime.today().strftime("%Y%m%d"):
                return True, f["ch_list"]
        except:
            pass
        data = self.providers[provider_name].get("data") if not data else data
        
        # RETRIEVE SESSION
        msg = self.login(provider_name, data)
        if type(msg) == tuple and not msg[0]:
            return False, msg[1]
        
        session = self.user_db.main["sessions"].get(provider_name)

        try:
            ch_list = sys.modules[self.providers[provider_name].get("module", provider_name)].channels(
                data, session, general_header
            )
            try:
                if provider_name != "xmltv":
                    with open(f"{self.file_paths['storage']}cache/lineup_{provider_name}.json", "w") as file:
                        json.dump({"date": datetime.today().strftime("%Y%m%d"), "ch_list": ch_list}, file)
                    # self.channel_db.update_channel_db("lineup", provider_name, ch_list)
            except:
                pass
            return True, ch_list
        except Exception as e:
            return False, str(e)

    # MAIN DATA
    def main_downloader(self, provider_name, data=None):
        data = self.providers[provider_name].get("data") if not data else data
        provider = "gntms" if provider_name == "tvtms" else provider_name
        settings = {**self.user_db.main["settings"], **self.user_db.main["provider_settings"].get(provider, {})}

        if provider_name == "tvtms":
            self.retry_tms = []

        # RETRIEVE CHANNELS AND PROVIDER TYPE
        if type(data) == dict and data.get("id") and "xml" in data["id"]:
            channels = [i.replace(f"{data['id']}_", "") for i in self.user_db.main["channels"].keys() if f"{data['id']}_" in i]
            xmltv = True
        else:
            channels = [i for i in self.user_db.main["channels"].keys() if "_" not in i] if provider == "gntms" else \
                [i.replace(f"{provider}_", "") for i in self.user_db.main["channels"].keys() if f"{provider}_" in i]
            xmltv = False

        # REFRESH PRELOAD DB
        self.epg_db.remove_epg_db(provider if not xmltv else data["id"], True)
        self.epg_db.create_epg_db(provider if not xmltv else data["id"], True)
        self.epg_cache = {}
        
        # RETRIEVE SESSION
        if not xmltv:
            if not self.login(provider_name):
                self.print_error_cache(provider_name)
                return []

        # URL/HEADERS/DATA LIST
        url_list = sys.modules[self.providers[provider_name].get("module", provider_name)].epg_main_links(
            data, channels, settings,
            self.user_db.main["sessions"].get(provider_name), general_header)
        
        # MAX NUMBER OF DOWNLOADS/CONVERSIONS PER BLOCK
        final_list = []
        url_list_part = []
        
        for i in url_list:
            url_list_part.append(i)
            if len(url_list_part) == self.providers[provider_name].get("max_dl_num", 50):
                final_list.append(url_list_part)
                url_list_part = []
        if len(url_list_part) > 0:
            final_list.append(url_list_part)
        
        self.fl_num = len(final_list)
        self.fl_pr = 0
        
        # MAX NUMBER OF THREADS WITHIN THE BLOCK
        if os.name != "nt":
            max_workers = 1
        elif not self.providers[provider_name].get("max_dl_threads") or \
                self.providers[provider_name]["max_dl_threads"] <= settings["dl_threads"]:
            max_workers = settings["dl_threads"] 
        else:
            max_workers = self.providers[provider_name]["max_dl_threads"]
        
        # SENDING DL BLOCKS WITH SELECTED NUMBER OF THREADS
        for url_list in final_list:
            self.l_pr = 0
            self.l_num = len(url_list)
            
            executor = concurrent.futures.ThreadPoolExecutor(max_workers=max_workers)
            {executor.submit(self.load_main, provider_name, item, item.get("n", str(index))).add_done_callback(self.url_threads_handler) for index, item in enumerate(url_list)}
            executor.shutdown(wait=True)

            # WRITE PRELOAD EPG DATA INTO DB
            gen = {}
            if self.providers[provider_name].get("main_custom_genres"):
                gen = sys.modules[self.providers[provider_name].get("module", provider_name)].genres()

            for i in self.epg_cache.keys():
                if not "###" in i:
                    m = sys.modules[self.providers[provider_name].get("module", provider_name)].epg_main_converter(
                        self.epg_cache[i][0], data, channels, settings, self.epg_cache[i][1], gen)
                
                    self.epg_db.write_epg_db_items(provider if not xmltv else data["id"],
                        [(i["c_id"], i["b_id"], i["start"], i["end"], i["title"], 
                          i.get("subtitle"), i.get("desc"), i.get("image"), 
                          i.get("date"), i.get("country"), i.get("star", {}), i.get("rating", {}), i.get("credits", {}),
                          i.get("season_episode_num", {}), i.get("genres", []), i.get("qualifiers", [])) for i in m], True)
            self.epg_cache = {}
            self.fl_pr = self.fl_pr + 1

        # WRITE DATA INTO REAL DB
        self.epg_db.confirm_update()
        del final_list, url_list
        self.epg_cache = {}

        # CLEAN UP
        if not self.providers[provider_name].get("adv_loader", False):
            self.epg_db.remove_epg_db(provider if not xmltv else data["id"], False)

        self.epg_db.create_epg_db(provider if not xmltv else data["id"], False)
        self.status_ext = None
        self.pr_pr = self.pr_pr + 1
        self.print_error_cache(provider_name)
        return self.epg_db.simple_epg_db_update(provider if not xmltv else data["id"], settings.get("adv_days", 14))
    
    def getProcessOutput(self, cmd):
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, close_fds=True, shell=True)
        process.wait(4)
        data, err = process.communicate()
        if process.returncode == 0:
            return data.decode('utf-8')        
        return

    def load_main(self, provider_name, item, name, tms_retry=False):
        if self.exit or self.cancellation:
            return
        if tms_retry:
            sleep(3)
            if tms_retry % 2 == 0:
                item["url"] = item["tms2"]
            else:
                item["url"] = item["tms3"]
            del item["tms"], item["d"]
        else:
            sleep(self.providers[provider_name].get("dl_delay", 0))
        x = 0
        while True:
            try:
                if item.get("tms"):
                    gh = "; ".join(f"{i}: {general_header[i]}" for i in general_header.keys())
                    r = self.getProcessOutput(f'{curl} -s -m {item.get("t", self.providers[provider_name].get("timeout", 60))} "{item["tms"]}" -H "{item["h"] if item.get("h") else gh}"{(" --data-raw "+item["d"]) if item.get("d") else ""}')
                elif item.get("d"):
                    r = requests.post(item["url"], headers=item.get("h", general_header), data=item["d"], cookies=item.get("cc", {}), timeout=item.get("t", self.providers[provider_name].get("timeout", 60)))
                elif item.get("j"):
                    r = requests.post(item["url"], headers=item.get("h", general_header), json=item["j"], cookies=item.get("cc", {}), timeout=item.get("t", self.providers[provider_name].get("timeout", 60)))
                else:
                    r = requests.get(item["url"], headers=item.get("h", general_header), cookies=item.get("cc", {}), timeout=item.get("t", self.providers[provider_name].get("timeout", 60)))
                break
            except:
                if item.get("tms"):
                    return provider_name, "", item.get("c"), name
                x = x + 1
                if x < 5:
                    sleep(3)
                    continue
                else:
                    if len(self.error_cache) <= 50:
                        self.error_cache.append(f"{provider_name}: Connection error for {str(item['url'])} - closed.")
                    return provider_name, "", item.get("c"), name
        
        if item.get("tms") and not r:
            return provider_name, "", item.get("c"), name
        elif not item.get("tms") and str(r.status_code)[0] in ["4", "5"]:
            if len(self.error_cache) <= 50:
                if self.providers[provider_name].get("ignore_error_codes", []) and r.status_code in self.providers[provider_name]["ignore_error_codes"]:
                    pass
                else:
                    self.error_cache.append(f"{provider_name}: HTTP error {str(r.status_code)} for {str(r.url)} - {str(r.content)}")
            return provider_name, "", item.get("c"), name
        
        return provider_name, r if item.get("tms") else r.content, item.get("c"), name

    def url_threads_handler(self, item):
        if self.exit or self.cancellation:
            return
        if item.result()[0] == "tvtms" and item.result()[1] == "":
            self.retry_tms.append(item.result()[3])
            return
        self.epg_cache[f"{'###' if item.result()[1] == '' else ''}{item.result()[3]}"] = item.result()[1], item.result()[2]
        self.l_pr = self.l_pr + 1
        self.progress = ((((self.l_pr / self.l_num) * 100) / self.fl_num / 2) + (self.fl_pr / self.fl_num) * 100 / 2) / self.pr_num + (self.pr_pr / self.pr_num * 100 / 2)
        return

    # ADVANCED DATA
    def advanced_downloader(self, provider_name, programmes, data=None):
        if len(programmes) == 0:
            return True
        
        data = self.providers[provider_name].get("data") if not data else data
        provider = "gntms" if provider_name == "tvtms" else provider_name
        settings = {**self.user_db.main["settings"], **self.user_db.main["provider_settings"].get(provider, {})}
        
        # RETRIEVE SESSION
        if not self.login(provider_name, data):
            self.print_error_cache(provider_name)
            return False
        
        session = self.user_db.main["sessions"].get(provider_name)

        url_params = sys.modules[self.providers[provider_name].get("module", provider_name)].epg_advanced_links(
            data, session, settings, programmes, general_header)
        
        # SET MAX NUMBER OF FILE DOWNLOADS
        if settings.get("adv_files"):
            try:
                url_params = url_params[:settings["adv_files"]]
            except:
                pass
        
        # DUPLICATE CHECKER - REQUIRED FOR SHARED MOVIE/SERIES DATA (UNIQUE ID REQUIRED IN URL LIST)
        u = {}
        if self.providers[provider_name].get("duplicate_check_req"):
            url_params_new = []
            for i in url_params:
                if u.get(i["uid"]):
                    u[i["uid"]].append(i["name"])
                else:
                    u[i["uid"]] = [i["name"]]
                    url_params_new.append(i)
            u = {u[i][0]: [x for c, x in enumerate(u[i]) if c != 0] for i in u.keys()}
            url_params = url_params_new
        
        self.params_len = len(url_params)
        self.params_part_len = 0

        # MULTIPLE STEPS
        url_params_new = []
        final_list = []
        for i in url_params:
            url_params_new.append(i)
            if len(url_params_new) == self.providers[provider_name].get("advanced_max_dl_num", 50):
                final_list.append(url_params_new)
                url_params_new = []
        if len(url_params_new) > 0:
            final_list.append(url_params_new)
        del url_params, url_params_new

        self.fl_num = len(final_list)
        self.fl_pr = 0

        # SET MAX DURATION FOR GRABBER DOWNLOAD
        max_time = int((datetime.now() + timedelta(minutes=int(settings["adv_duration"]))).timestamp()) if settings.get("adv_duration") else None

        for grabber_param in final_list:
            
            # MAX TIME REACHED
            if max_time and int(datetime.now().timestamp()) > max_time:
                self.fl_pr = self.fl_pr + 1
                continue

            self.l_pr = 0
            self.l_num = len(grabber_param)

            if len(self.epg_cache) > 0:
                self.epg_cache = {}

            if os.name != "nt":
                max_workers = settings.get("adv_threads", 1)
            else:
                max_workers = settings.get("adv_threads", self.providers[provider_name].get("advanced_download_threads", 10))

            if provider_name == "tvtms":
                self.retry_tms = []
            
            executor = concurrent.futures.ThreadPoolExecutor(
                max_workers=max_workers)
            {executor.submit(self.load_main, provider_name, item, item.get("name", str(index))).add_done_callback(self.url_threads_handler) for index, item in enumerate(grabber_param)}
            executor.shutdown(wait=True)
            del executor

            # TMS RETRY
            if provider_name == "tvtms":
                new_grabber_param = [item for item in grabber_param if item["name"] in self.retry_tms]
                max_workers = 1

                executor = concurrent.futures.ThreadPoolExecutor(
                    max_workers=max_workers)
                {executor.submit(self.load_main, provider_name, item, item.get("name", str(index)), index+1).add_done_callback(self.url_threads_handler) for index, item in enumerate(new_grabber_param)}
                executor.shutdown(wait=True)
                del executor

            def duplicator(dup_ids, broadcast_list):
                x = list(broadcast_list[0])  # BROADCAST LIST CONTAINS 1 ELEMENT ONLY
                for item in dup_ids:
                    x[-1] = item
                    broadcast_list.append(tuple(x))
                return broadcast_list

            for i in self.epg_cache.keys():
                if not "###" in i:
                    m = sys.modules[self.providers[provider_name].get("module", provider_name)].epg_advanced_converter(
                        i, self.epg_db.config[provider_name].get("data"), self.epg_cache[i],
                        settings)
                    
                    if self.providers[provider_name].get("multi_update"):
                        for j in m:
                            j["b_id"] = j["b_id"].split("|+|")[0]

                    if len(u) > 0 and u.get(i):  # INSERT DETAILS FOR BROADCASTS WITH IDENTICAL DATA
                        self.epg_db.update_epg_db_items(provider, duplicator(u[i], 
                            [(i.get("c_id"), i["b_id"], i.get("start"), i.get("end"), i.get("title"), 
                                i.get("subtitle"), i.get("desc"), i.get("image"), 
                                i.get("date"), i.get("country"), json.dumps(i.get("star", {})), json.dumps(i.get("rating", {})), json.dumps(i.get("credits", {})),
                                json.dumps(i.get("season_episode_num", {})), json.dumps(i.get("genres", [])), json.dumps(i.get("qualifiers", []))) for i in m]), True)
                    else:
                        self.epg_db.update_epg_db_items(provider,
                            [(i.get("c_id"), i["b_id"], i.get("start"), i.get("end"), i.get("title"), 
                                i.get("subtitle"), i.get("desc"), i.get("image"), 
                                i.get("date"), i.get("country"), json.dumps(i.get("star", {})), json.dumps(i.get("rating", {})), json.dumps(i.get("credits", {})),
                                json.dumps(i.get("season_episode_num", {})), json.dumps(i.get("genres", [])), json.dumps(i.get("qualifiers", []))) for i in m], True)
            
            self.epg_cache = {}

            self.params_part_len = self.params_part_len + self.providers[provider_name].get("advanced_max_dl_num", 50) \
                if (self.params_len - self.params_part_len) > self.providers[provider_name].get("advanced_max_dl_num", 50) else self.params_len
            
            self.fl_pr = self.fl_pr + 1

        self.epg_db.confirm_update()
        del final_list
        self.epg_cache = {}

        self.status_ext = None
        self.pr_pr = self.pr_pr + 1
        self.print_error_cache(provider_name)
        return True

