from datetime import datetime
from importlib import util
from time import sleep
import concurrent.futures, json, os, requests, sqlite3, sys

general_header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                                'Chrome/81.0.4044.138 Safari/537.36'}

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
            with open(f"{self.file_paths['included']}resources/data/json/genres.json", "r") as f:
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
        
        # Check settings / insert default values (if needed)
        if self.main["settings"].get("ut", "") == "":
            self.main["settings"]["ut"] = "04:00"
            self.save_settings()
        
        return True

    
    def save_settings(self):
        with open(f"{self.file_paths['storage']}settings.json", "w") as f:
            json.dump(self.main, f)
        return True

class SQLiteManager():
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
                        """genres = coalesce(?, genres), qualifiers = {}, advanced = {} """
                        """WHERE broadcast_id = ?""".format(provider, 1 if advanced else 0),
                        (start, end, title, subtitle, desc, image, date, country, json.dumps(star), json.dumps(rating), 
                         json.dumps(credits), json.dumps(season_episode_num), json.dumps(genres), json.dumps(qualifiers), broadcast_id))
        for channel_id, start, end, title, subtitle, desc, image, date, country, star, rating,
            credits, season_episode_num, genres, qualifiers, broadcast_id in to_be_updated]
        return

    def simple_epg_db_update(self, provider):
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

            advanced_to_be_loaded.extend([item[1] for item in new_broadcasts_items if item[1] not in old_advanced_set])
            del new_broadcasts_items, old_advanced_set

        self.confirm_update()

        self.remove_epg_db(provider, True)

        return advanced_to_be_loaded
    
    def confirm_update(self):
        self.conn.commit()
        self.c.execute("""VACUUM""")

class ProviderManager():
    
    def __init__(self, file_paths, user_db):
        self.file_paths = file_paths
        self.user_db = user_db
        self.import_data()
        self.epg_db = SQLiteManager(self.providers, file_paths["storage"])
        self.import_provider_modules()

    # PROVIDER CONFIG
    def import_data(self):
        with open(f"{self.file_paths['included']}resources/data/json/providers.json", "r") as f:
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
            return
        if self.providers[provider_name].get("auth_req"):
            auth_data = {"key": self.user_db.main["settings"].get("api_key")} if provider_name == "gntms" \
                else self.user_db.main["auth_data"].get(provider_name)
            if not auth_data:
                return False, "No key found" if self.providers[provider_name]["auth_type"] == "api_key" else "No credentials found"
            session = self.user_db.main["sessions"].get(provider_name)
            if session:
                if session.get("expiration", False) is False or session.get("expiration", 0) > datetime.timestamp():
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
            return False, str(e)
        
    # LOAD CHLIST
    def ch_loader(self, provider_name, data={}):
        data = self.providers[provider_name].get("data") if not data else data
        
        # RETRIEVE SESSION
        self.login(provider_name, data)
        session = self.user_db.main["sessions"].get(provider_name)

        try:
            ch_list = sys.modules[self.providers[provider_name].get("module", provider_name)].channels(
                data, session, general_header
            )
            return True, ch_list
        except Exception as e:
            return False, str(e)

    # MAIN DATA
    def main_downloader(self, provider_name, data=None):
        data = self.providers[provider_name].get("data") if not data else data

        # RETRIEVE CHANNELS AND PROVIDER TYPE
        if type(data) == dict and data.get("id") and "xml" in data["id"]:
            channels = [i.replace(f"{data['id']}_", "") for i in self.user_db.main["channels"].keys() if f"{data['id']}_" in i]
            xmltv = True
        else:
            channels = [i for i in self.user_db.main["channels"].keys() if "_" not in i] if provider_name == "gntms" else \
                [i.replace(f"{provider_name}_", "") for i in self.user_db.main["channels"].keys() if f"{provider_name}_" in i]
            xmltv = False

        # REFRESH PRELOAD DB
        self.epg_db.remove_epg_db(provider_name if not xmltv else data["id"], True)
        self.epg_db.create_epg_db(provider_name if not xmltv else data["id"], True)
        self.epg_cache = {}
        
        # RETRIEVE SESSION
        if not xmltv:
            self.login(provider_name)

        # URL/HEADERS/DATA LIST
        url_list = sys.modules[self.providers[provider_name].get("module", provider_name)].epg_main_links(
            data, channels, self.user_db.main["settings"],
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
        if not self.providers[provider_name].get("max_dl_threads") or \
                self.providers[provider_name]["max_dl_threads"] <= self.user_db.main["settings"]["dl_threads"]:
            max_workers = self.user_db.main["settings"]["dl_threads"] 
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
            for i in self.epg_cache.keys():
                m = sys.modules[self.providers[provider_name].get("module", provider_name)].epg_main_converter(
                    self.epg_cache[i][0], channels, self.user_db.main["settings"], self.epg_cache[i][1])
                if not "." in i:
                    self.epg_db.write_epg_db_items(provider_name  if not xmltv else data["id"],
                        [(i["c_id"], i["b_id"], i["start"], i["end"], i["title"], 
                          i.get("subtitle", ""), i.get("desc", ""), i.get("image", ""), 
                          i.get("date", ""), i.get("country", ""), i.get("star", {}), i.get("rating", {}), i.get("credits", {}),
                          i.get("season_episode_num", {}), i.get("genres", []), i.get("qualifiers", [])) for i in m], True)
            self.epg_cache = {}
            self.fl_pr = self.fl_pr + 1

        # WRITE DATA INTO REAL DB
        self.epg_db.confirm_update()
        del final_list, url_list
        self.epg_cache = {}

        # CLEAN UP
        if not self.providers[provider_name].get("adv_loader", False):
            self.epg_db.remove_epg_db(provider_name if not xmltv else data["id"], False)

        self.epg_db.create_epg_db(provider_name if not xmltv else data["id"], False)
        self.status_ext = None
        return self.epg_db.simple_epg_db_update(provider_name if not xmltv else data["id"])

    def load_main(self, provider_name, item, name):
        if self.exit or self.cancellation:
            return
        sleep(self.providers[provider_name].get("dl_delay", 0))
        try:
            if item.get("d"):
                r = requests.post(item["url"], headers=item.get("h", general_header), data=item["d"], cookies=item.get("cc", {}))
            else:
                r = requests.get(item["url"], headers=item.get("h", general_header), cookies=item.get("cc", {}))
        except:
            return provider_name, "", item.get("c"), name
        
        if str(r.status_code)[0] in ["4", "5"]:            
            return provider_name, "", item.get("c"), name
        
        return provider_name, r.content, item.get("c"), name

    def url_threads_handler(self, item):
        if self.exit or self.cancellation:
            return
        self.epg_cache[f"{'.' if item.result()[1] == '' else ''}{item.result()[3]}"] = item.result()[1], item.result()[2]
        self.l_pr = self.l_pr + 1
        self.progress = ((((self.l_pr / self.l_num) * 100) / self.fl_num / 2) + (self.fl_pr / self.fl_num) * 100 / 2) / self.pr_num + (self.pr_pr / self.pr_num * 100 / 2)
        return

    # ADVANCED DATA
    def advanced_downloader(self, provider_name, programmes):
        return True
