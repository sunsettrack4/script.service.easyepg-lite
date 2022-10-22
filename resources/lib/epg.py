from resources.lib import tools
from datetime import datetime
from threading import Thread
from time import sleep
import concurrent.futures, gzip, json, os, shutil, traceback
import xmltodict


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
            with open(f"{self.file_paths['included']}app/data/json/genres.json", "r") as f:
                self.genres = json.load(f)
        except:
            self.genres = dict()

        # Init default settings
        if "channels" not in self.main:
            self.main["channels"] = {}
        if "settings" not in self.main:
            self.main["settings"] = {"api_key": None, "days": "7", "rm": "none", "is": "Md", "it": "16x9", "at": "fsk", "rate": "0", "ut": "04:00", "ag": "no", "file": False, "dl_threads": 1, "pn_max": 50000}
        return True
    
    def save_settings(self):
        with open(f"{self.file_paths['storage']}settings.json", "w") as f:
            json.dump(self.main, f)
        return True

class Grabber():
    def __init__(self, file_paths):
        self.user_db = UserData(file_paths)
        self.file_paths = file_paths

        self.grabbing = False
        self.status = "Idle"
        self.progress = 100

        self.file_available = False
        self.file_created = "Never"
        if os.path.exists(f"{file_paths['storage']}epg.xml"):
            self.file_available = True
            self.file_created = datetime.fromtimestamp(os.path.getmtime(f"{self.file_paths['storage']}epg.xml")).strftime('%Y-%m-%d %H:%M:%S')
        
        self.started = False
        self.cancellation = False
        self.exit = False

        # AUTO START UP
        start_up = False
        start_dt = f'{datetime.now().year}{datetime.now().month}{datetime.now().day}'
        if self.user_db.main["settings"]["ag"] == "yes":
            start_up = True
        if self.user_db.main["settings"]["ag"] == "out" and self.file_available and \
            int(self.user_db.main["settings"]["rate"]) * 3600 + os.path.getmtime(f"{self.file_paths['storage']}epg.xml") <= datetime.strptime(f'{start_dt} {self.user_db.main["settings"]["ut"]}', "%Y%m%d %H:%M").timestamp():
                start_up = True
        if self.user_db.main["settings"]["ag"] == "out" and not self.file_available:
            start_up = True

        self.thread = Thread(target=self.epg_process, args=(start_up, start_dt,))
        self.thread.start()

    def grabber_status(self):
        return {"grabbing": self.grabbing, "status": self.status, "progress": self.progress, "file_available": self.file_available, "file_created": self.file_created}

    def epg_process(self, start_up, start_dt):
        if start_up:
            self.grabbing = True

        while True:
            if self.grabbing and not self.started:
                self.started = True
                self.grabber_process()
            else:
                if self.exit:
                    break
                if int(self.user_db.main["settings"]["rate"]) != 0 and \
                    (int(self.user_db.main["settings"]["rate"]) * 3600 + datetime.strptime(f'{start_dt} {self.user_db.main["settings"]["ut"]}', "%Y%m%d %H:%M").timestamp()) < datetime.now().timestamp():
                        self.grabbing = True
                        start_dt = f'{datetime.now().year}{datetime.now().month}{datetime.now().day}'
                sleep(1)

    def load_airings(self, channel):
        if self.cancellation or self.exit:
            return
        return tools.API.grab_channel(self, channel, self.user_db.main["settings"]), channel

    def cache_airings(self, data):
        if self.cancellation or self.exit:
            return
        data = data.result()
        with open(f"{self.file_paths['storage']}cache/epg_cache/{data[1]}", "w") as f:
            f.write(json.dumps(data[0]))
        self.worker = self.worker + 1
        self.progress = (self.worker / len(self.user_db.main["channels"])) * 100 / 2

    def grabber_process(self):
        try:
            self.progress = 0
            self.worker = 0

            # PREPARING FILES/DIRECTORIES
            if not os.path.exists(f"{self.file_paths['storage']}cache/epg_cache"):
                os.mkdir(f"{self.file_paths['storage']}cache/epg_cache")
            else:
                shutil.rmtree(f"{self.file_paths['storage']}cache/epg_cache", ignore_errors=True)
                os.mkdir(f"{self.file_paths['storage']}cache/epg_cache")

            if os.path.exists(f"{self.file_paths['storage']}test.xml"):
                os.remove(f"{self.file_paths['storage']}test.xml")

            # DOWNLOAD FILES
            self.status = "Downloading EPG data..."
            
            executor = concurrent.futures.ThreadPoolExecutor(max_workers=self.user_db.main["settings"]["dl_threads"])
            {executor.submit(self.load_airings, channel).add_done_callback(self.cache_airings) for channel in self.user_db.main["channels"]}
            executor.shutdown(wait=True)

            if self.cancellation or self.exit:
                raise Exception("Process stopped.")

            # CREATE XML
            self.status = "Creating EPG file..."
            self.worker = 0
            self.basic_value = 1 / len(self.user_db.main["channels"])

            with open(f"{self.file_paths['storage']}test.xml", "a+", encoding="UTF-8") as file:

                # GENERAL INFO
                file.write('<?xml version="1.0" encoding="UTF-8"?>\n')
                file.write(f'<!-- EPG XMLTV FILE CREATED BY THE EASYEPG PROJECT - '
                        f'(c) {datetime.today().year} Jan-Luca Neumann -->\n')
                file.write(f'<!-- created on {str(datetime.today()).split(".")[0]} -->\n')
                file.write('<tv>\n')

                # CHANNEL LIST
                ch = {"channel": []}
                for channel in self.user_db.main["channels"].keys():
                    c_data = self.user_db.main["channels"][channel]
                    image = c_data.get("preferredImage", {"uri": None})["uri"]
                    lang = c_data["bcastLangs"][0].lower()
                    if "-" in lang:
                        lang = lang.split("-")[1]
                    ch_part = {"@id": c_data.get("tvg-id", channel), "display-name": {"@lang": lang, "#text": c_data["name"]}}
                    if image:
                        ch_part["icon"] = {"@src": image}
                    ch["channel"].append(ch_part)
                file.write(xmltodict.unparse(ch, pretty=True, encoding="UTF-8", full_document=False))

                # PROGRAMMES
                pr = {"programme": []}
                pn = 0
                for channel in self.user_db.main["channels"].keys():
                    c_data = self.user_db.main["channels"][channel]
                    lang = c_data["bcastLangs"][0].lower()
                    if "-" in lang:
                        lang = lang.split("-")[1]
                    with open(f"{self.file_paths['storage']}cache/epg_cache/{channel}", "r") as f:
                        data = json.loads(f.read())
                        inner_value = len(data)
                        inner_worker = 0

                        for i in data:
                            if self.cancellation or self.exit:
                                raise Exception("Process stopped.")

                            # DEFINE PARAMS
                            p = i["program"]
                            start = i["startTime"].replace("T", "").replace("Z", ":00 +0000").replace("-", "").replace(":", "")
                            end = i["endTime"].replace("T", "").replace("Z", ":00 +0000").replace("-", "").replace(":", "")
                            image = p.get("preferredImage", {"uri": None})["uri"]
                            title = p["title"]
                            subtitle = p.get("episodeTitle", p.get("eventTitle"))
                            desc = p.get("longDescription", p.get("shortDescription"))
                            date = datetime.strptime(p["origAirDate"], "%Y-%m-%d").strftime("%Y") if p.get("origAirDate", False) else None
                            star = p.get("qualityRating", {"value": None})["value"]
                            director = p.get("directors", [])
                            actor = p.get("topCast", [])
                            episode_num = p.get("episodeNum")
                            season_num = p.get("seasonNum")
                            categories = p.get("genres", [])
                            rating = None
                            rating_type = None

                            # DEFINE AGE RATING
                            for r in p.get("ratings", []):
                                if r["body"] == "Freiwillige Selbstkontrolle der Filmwirtschaft" and self.user_db.main["settings"]["at"] == "fsk" or \
                                    r["body"] == "USA Parental Rating" and self.user_db.main["settings"]["at"] == "usa":
                                        rating = r["code"]
                                        rating_type = self.user_db.main["settings"]["at"].upper()
                            
                            # PROGRAM
                            program = {"@start": start, "@stop": end, "@channel": c_data.get("tvg-id", channel)}

                            # ICON
                            if image is not None and image != "":
                                program["icon"] = {"@src": image}

                            # TITLE
                            if title is not None and title != "":
                                program["title"] = {"@lang": lang, "#text": title}
                            else:
                                program["title"] = {"@lang": lang, "#text": "No programme title available"}

                            # SUBTITLE
                            if subtitle is not None and subtitle != "":
                                program["sub-title"] = {"@lang": lang, "#text": subtitle}

                            # DESC
                            if desc is not None and desc != "":

                                # RATING MAPPER
                                if self.user_db.main["settings"]["rm"] == "add-info" or \
                                    self.user_db.main["settings"]["rm"] == "add-info-cast":
                                    desc_line = ""
                                    if date is not None and date != "":
                                        if desc_line != "":
                                            desc_line = f"{desc_line} {date}"
                                        else:
                                            desc_line = f"{date}"
                                    if (episode_num is not None and episode_num != "") and \
                                        (season_num is not None and season_num != ""):
                                        if desc_line != "":
                                            desc_line = f"{desc_line} ● S{season_num} E{episode_num}"
                                        else:
                                            desc_line = f"S{season_num} E{episode_num}"
                                    elif season_num is not None and season_num != "":
                                        if desc_line != "":
                                            desc_line = f"{desc_line} ● S{season_num}"
                                        else:
                                            desc_line = f"S{season_num}"
                                    elif episode_num is not None and episode_num != "":
                                        if desc_line != "":
                                            desc_line = f"{desc_line} ● E{episode_num}"
                                        else:
                                            desc_line = f"E{episode_num}"
                                    if rating is not None and rating != "":
                                        if desc_line != "":
                                            desc_line = f"{desc_line} ● {rating_type if rating_type is not None else 'Age'}: {rating}"
                                        else:
                                            desc_line = f"{rating_type if rating_type is not None else 'Age:'} {rating}"
                                    if star is not None and star != "":
                                        if float(star) >= 3.5:
                                            star_desc_line = "★★★★"
                                        elif 2.5 <= float(star) < 3.5:
                                            star_desc_line = "★★★☆"
                                        elif 1.5 <= float(star) < 2.5:
                                            star_desc_line = "★★☆☆"
                                        elif 0.5 <= float(star) < 1.5:
                                            star_desc_line = "★☆☆☆"
                                        else:
                                            star_desc_line = "☆☆☆☆"
                                        if desc_line != "":
                                            desc_line = f"{desc_line} ● TMS Rating: {star_desc_line}"
                                        else:
                                            desc_line = f"TMS Rating: {star_desc_line}"
                                    if desc_line != "":
                                        desc = f"{desc_line}\n{desc}"

                                # SHOW CREDITS IN DESCRIPTION
                                if self.user_db.main["settings"]["rm"] == "add-cast" or \
                                    self.user_db.main["settings"]["rm"] == "add-info-cast":

                                    cast_line = ""
                                    director_line = ""
                                    actor_line = ""

                                    # DIRECTORS
                                    if len(director) > 0:
                                        for item in director:
                                            if director_line != "":
                                                director_line = f"{director_line}\n{item}"
                                            else:
                                                director_line = item

                                    # ACTORS
                                    if len(actor) > 0:
                                        for item in actor:
                                            if actor_line != "":
                                                actor_line = f"{actor_line}\n{item}"
                                            else:
                                                actor_line = item

                                    # CAST LINE TO BE SHOWN IN DESCRIPTION
                                    if director_line != "" and actor_line != "":
                                        cast_line = f"Director(s):\n\n{director_line}\n\nActor(s):\n\n{actor_line}"
                                    elif director_line != "":
                                        cast_line = f"Director(s):\n\n{director_line}"
                                    elif actor_line != "":
                                        cast_line = f"Actor(s):\n\n{actor_line}"

                                    if cast_line != "":
                                        desc = f"{desc}\n\n{cast_line}"

                                program["desc"] = {"@lang": lang, "#text": desc}

                            # CREDITS
                            if (len(director) > 0 or len(actor) > 0) and \
                                (self.user_db.main["settings"]["rm"] != "none" or self.user_db.main["settings"]["rm"] != "add-info"):
                                program["credits"] = {"director": [], "actor": []}

                                for item in director:
                                    program["credits"]["director"].append({"#text": item})
                                for item in actor:
                                    program["credits"]["actor"].append({"#text": item})

                            # DATE
                            if date is not None and date != "":
                                program["date"] = {"#text": date}

                            # CATEGORIES
                            genres = []
                            mapped_genres = []
                            if len(categories) > 0:
                                program["category"] = []
                            for i in categories:
                                g = i
                                if g not in genres:
                                    genres.append(g)
                                    genre = self.user_db.genres.get("genres", {}).get(g)
                                    if genre and genre not in mapped_genres:
                                        mapped_genres.append(genre)
                                        program["category"].append({"@lang": "en", "#text": genre})
                                    elif not genre:
                                        program["category"].append({"@lang": "en", "#text": g})
                            del genres, mapped_genres

                            # EPISODE
                            if (season_num is not None and season_num != "") \
                                    or (episode_num is not None and episode_num != ""):
                                if season_num is None:
                                    season_num = 1
                                if episode_num is None:
                                    episode_num = 1
                                program["episode-num"] = {"@system": "xmltv_ns", 
                                    "#text": f"{int(season_num) - 1} . {int(episode_num) - 1} . "}

                            # AGE RATING
                            if rating is not None and rating != "":
                                program["rating"] = {"@system": rating_type, "value": {"#text": rating}}

                            # STAR RATING
                            if star is not None and star != "":
                                program["star-rating"] = {"@system": "TMS", "value": {"#text": f"{star}/4"}}

                            pr["programme"].append(program)
                            pn = pn + 1
                            
                            inner_worker = inner_worker + 1
                            self.progress = (inner_worker / inner_value) * self.basic_value + self.worker + 50

                            if pn == self.user_db.main["settings"]["pn_max"]:
                                file.write(xmltodict.unparse(pr, pretty=True, encoding="UTF-8", full_document=False))
                                pn = 0
                                pr["programme"] = []
                    
                    self.worker = self.worker + (100 * self.basic_value / 2)
                
                if len(pr["programme"]) > 0:
                    file.write(xmltodict.unparse(pr, pretty=True, encoding="UTF-8", full_document=False))
                
                file.write('</tv>\n')
            
            if os.path.exists(f"{self.file_paths['storage']}epg.xml"):
                os.remove(f"{self.file_paths['storage']}epg.xml")
            os.rename(f"{self.file_paths['storage']}test.xml", f"{self.file_paths['storage']}epg.xml")

            self.status = "Creating compressed file..."
            with open(f"{self.file_paths['storage']}epg.xml", 'rb') as f_in, gzip.open(f"{self.file_paths['storage']}epg.xml.gz", 'wb') as f_out:
                f_out.writelines(f_in)

            self.file_available = True
            self.file_created = datetime.fromtimestamp(os.path.getmtime(f"{self.file_paths['storage']}epg.xml")).strftime('%Y-%m-%d %H:%M:%S')

            self.status = "File created successfully!"
            self.progress = 100
            self.grabbing = False
            self.started = False
            sleep(5)
            self.status = "Idle"

        except Exception:
            
            with open(f"{self.file_paths['storage']}grabber_error_log.txt", "a+") as log:
                log.write(f"--- ERROR LOG: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ---\n")
                traceback.print_exc(file=log)
                log.write(f"--- ERROR LOG END ---\n\n")

            self.grabbing = False
            self.started = False
            self.cancellation = False
            self.progress = 100
            self.status = "An error occurred. Please check the 'grabber_error_log.txt' file."
            sleep(5)
            self.status = "Idle"
    