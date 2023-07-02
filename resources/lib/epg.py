from datetime import datetime
from threading import Thread
from time import sleep
import gzip, json, os, shutil, traceback
import xmltodict


class Grabber():
    def __init__(self, file_paths, provider_manager, user_db):
        self.user_db = user_db
        self.pr = provider_manager
        self.file_paths = file_paths

        self.grabbing = False
        self.status = "Idle"
        self.pr.progress = 100

        if os.path.exists(f"{self.file_paths['storage']}grabber_error_log_old.txt"):
            os.remove(f"{self.file_paths['storage']}grabber_error_log_old.txt")
        if os.path.exists(f"{self.file_paths['storage']}grabber_error_log.txt"):
            os.rename(f"{self.file_paths['storage']}grabber_error_log.txt", f"{self.file_paths['storage']}grabber_error_log_old.txt")

        self.file_available = False
        self.file_created = "Never"

        if not os.path.isdir(f"{file_paths['storage']}xml"):
            os.mkdir(f"{file_paths['storage']}xml")
        if os.path.exists(f"{file_paths['storage']}xml/epg.xml"):
            self.file_available = True
            self.file_created = datetime.fromtimestamp(os.path.getmtime(f"{self.file_paths['storage']}xml/epg.xml")).strftime('%Y-%m-%d %H:%M:%S')
        
        self.started = False
        self.cancellation = False
        self.exit = False

        # AUTO START UP
        start_up = False
        start_dt = f'{datetime.now().strftime("%Y%m%d")}'
        if self.user_db.main["settings"]["ag"] == "yes":
            start_up = True
        if self.user_db.main["settings"]["ag"] == "out" and self.file_available and \
            int(self.user_db.main["settings"]["rate"]) * 3600 + os.path.getmtime(f"{self.file_paths['storage']}xml/epg.xml") <= datetime.strptime(f'{start_dt} {self.user_db.main["settings"]["ut"]}', "%Y%m%d %H:%M").timestamp():
                start_up = True
        if self.user_db.main["settings"]["ag"] == "out" and not self.file_available:
            start_up = True

        self.thread = Thread(target=self.epg_process, args=(start_up, start_dt,))
        self.thread.start()

    def grabber_status(self):
        return {"grabbing": self.grabbing, "status": self.status, "progress": self.pr.progress, "file_available": self.file_available, "file_created": self.file_created}

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
                        start_dt = f'{datetime.now().strftime("%Y%m%d")}'
                sleep(1)

    def grabber_process(self):
        try:
            self.pr.progress = 0
            self.pr.worker = 0
            self.pr.cancellation = self.cancellation
            self.pr.exit = self.exit
            missing_genres = []

            # PREPARING FILES/DIRECTORIES
            if not os.path.exists(f"{self.file_paths['storage']}cache/epg_cache"):
                os.mkdir(f"{self.file_paths['storage']}cache/epg_cache")
            else:
                shutil.rmtree(f"{self.file_paths['storage']}cache/epg_cache", ignore_errors=True)
                os.mkdir(f"{self.file_paths['storage']}cache/epg_cache")

            if os.path.exists(f"{self.file_paths['storage']}xml/test.xml"):
                os.remove(f"{self.file_paths['storage']}xml/test.xml")

            # DOWNLOAD FILES
            self.status = "Downloading EPG data..."

            if len(self.user_db.main["channels"]) == 0:
                raise Exception("Please add your channels first before starting the grabber process.")
            
            # Check Provider List
            pr_check = []
            for ch in self.user_db.main["channels"].keys():
                a = ch.split("_")  # web/xml
                if len(a) > 1:
                    if a[0] not in pr_check:
                        pr_check.append(a[0])
                else:
                    try:
                        a = int(ch)  # tms id
                        if "gntms" not in pr_check:
                            pr_check.append("gntms")
                    except:
                        pass
            
            self.pr.pr_num = len(pr_check)
            self.pr.pr_pr = 0
            for provider in pr_check:
                if "xml" in provider:
                    data = {"link": self.user_db.main["xmltv"][provider]["link"], "id": provider}
                    self.pr.main_downloader("xmltv", data)
                elif self.pr.providers[provider].get("adv_loader"):
                    self.pr.advanced_downloader(provider, self.pr.main_downloader(provider))
                else:
                    self.pr.main_downloader(provider)
                self.pr.pr_pr = self.pr.pr_pr + 1

            if self.cancellation or self.exit:
                raise Exception("Process stopped.")

            # CREATE XML
            self.status = "Creating EPG file..."
            self.worker = 0
            self.basic_value = 1 / len(self.user_db.main["channels"])

            with open(f"{self.file_paths['storage']}xml/test.xml", "a+", encoding="UTF-8") as file:

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
                    if len(channel.split("_")) == 1:
                        lang = c_data["bcastLangs"][0].lower()
                        if "-" in lang:
                            lang = lang.split("-")[1]
                    else:
                        lang = "en"
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
                    if len(channel.split("_")) == 1:
                        lang = c_data["bcastLangs"][0].lower()
                        if "-" in lang:
                            lang = lang.split("-")[1]
                    else:
                        lang = "en"

                    results = self.pr.epg_db.retrieve_epg_db_items("gntms" if len(channel.split("_")) == 1 
                                                                   else channel.split("_")[0], self.user_db.main["channels"][channel]["stationId"])

                    inner_value = len(results)
                    inner_worker = 0
                    
                    for (channel_id, broadcast_id, start, end, title, subtitle, desc, image, 
                         date, country, star, rating, credits, season_episode_num, genres, qualifiers, advanced) \
                            in results:

                            if self.cancellation or self.exit:
                                raise Exception("Process stopped.")

                            # DEFINE PARAMS
                            start = datetime.fromtimestamp(float(start)).strftime("%Y%m%d%H%M%S +0000")
                            end = datetime.fromtimestamp(float(end)).strftime("%Y%m%d%H%M%S +0000")
                            star = json.loads(json.loads(star)) if type(star) == str else {}
                            star_value = star.get("value")
                            star_rating = star.get("system", "")
                            credits = json.loads(json.loads(credits)) if type(credits) == str else {}
                            director = credits.get("director", [])
                            actor = credits.get("actor", [])
                            series_data = json.loads(json.loads(season_episode_num)) if type(season_episode_num) == str else {}
                            episode_num = series_data.get("episode")
                            season_num = series_data.get("season")
                            categories = json.loads(json.loads(genres)) if type(genres) == str else []
                            age_rating = json.loads(json.loads(rating)) if type(rating) == str else {}
                            rating = age_rating.get("value")
                            rating_type = age_rating.get("system")
                            
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
                                    if country is not None and country != "":
                                        if desc_line != "":
                                            desc_line = f"{desc_line} {country}"
                                        else:
                                            desc_line = f"{country}"
                                    if date is not None and date != "":
                                        if desc_line != "":
                                            desc_line = f"{desc_line} {date[0:4]}"
                                        else:
                                            desc_line = f"{date[0:4]}"
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
                                    if star_value is not None and star_value != "" and len(star_value.split("/")) > 1:
                                        current_star_num = float(star_value.split("/")[0])
                                        max_star_num = float(star_value.split("/")[1])
                                        balance = current_star_num / max_star_num
                                        if float(balance) >= 0.8:
                                            star_desc_line = "★★★★★"
                                        elif 0.6 <= float(balance) < 0.8:
                                            star_desc_line = "★★★★☆"
                                        elif 0.4 <= float(balance) < 0.6:
                                            star_desc_line = "★★★☆☆"
                                        elif 0.2 <= float(balance) < 0.4:
                                            star_desc_line = "★★☆☆☆"
                                        else:
                                            star_desc_line = "★☆☆☆☆"
                                        if desc_line != "":
                                            desc_line = f"{desc_line} ● {star_rating if star_rating != '' else 'Star'} Rating: {star_desc_line}"
                                        else:
                                            desc_line = f"{star_rating if star_rating != '' else 'Star'} Rating: {star_desc_line}"
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

                            # COUNTRY
                            if country is not None and country != "":
                                program["country"] = {"#text": country}

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
                                        if g not in missing_genres:
                                            missing_genres.append(g)
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
                                if rating_type is not None and rating_type != "":
                                    program["rating"] = {"@system": rating_type, "value": {"#text": rating}}
                                else:
                                    program["rating"] = {"value": {"#text": rating}}

                            # STAR RATING
                            if star_value is not None and star_value != "":
                                if star_rating != "":
                                    program["star-rating"] = {"@system": star_rating, "value": {"#text": star_value}}
                                else:
                                    program["star-rating"] = {"value": {"#text": star_value}}

                           # QUALIFIERS
                            if 'New' in qualifiers:
                                program["new"]={""}
                            if 'Live' in qualifiers:
                                program["live"]={""}
                            if 'Premiere' in qualifiers:
                                program["premiere"]={"Premiere"}
                                
                            pr["programme"].append(program)
                            pn = pn + 1
                            
                            inner_worker = inner_worker + 1
                            self.pr.progress = (inner_worker / inner_value) * self.basic_value + self.worker + 50
    
                            if pn == self.user_db.main["settings"]["pn_max"]:                                
                                file.write(xmltodict.unparse(pr, pretty=True, encoding="UTF-8", full_document=False))
 
                                pn = 0
                                pr["programme"] = []
                                
                    self.worker = self.worker + (100 * self.basic_value / 2)
               
                if len(pr["programme"]) > 0:
                    file.write(xmltodict.unparse(pr, pretty=True, encoding="UTF-8", full_document=False))
                
                file.write('</tv>\n')
            
            if os.path.exists(f"{self.file_paths['storage']}xml/epg.xml"):
                os.remove(f"{self.file_paths['storage']}xml/epg.xml")
            os.rename(f"{self.file_paths['storage']}xml/test.xml", f"{self.file_paths['storage']}xml/epg.xml")
            
            replacements = {'<new></new>':'<new />', '<live></live>':'<live />'}

            with open(f"{self.file_paths['storage']}xml/epg.xml") as infile, open(f"{self.file_paths['storage']}xml/epg_new.xml", 'w') as outfile:
                for line in infile:
                   for src, target in replacements.items():
                       line = line.replace(src, target)
                   outfile.write(line)
                   
            if os.path.exists(f"{self.file_paths['storage']}xml/epg.xml"):
                os.remove(f"{self.file_paths['storage']}xml/epg.xml")
            os.rename(f"{self.file_paths['storage']}xml/epg_new.xml", f"{self.file_paths['storage']}xml/epg.xml")           

            self.status = "Creating compressed file..."
            with open(f"{self.file_paths['storage']}xml/epg.xml", 'rb') as f_in, gzip.open(f"{self.file_paths['storage']}xml/epg.xml.gz", 'wb') as f_out:
                f_out.writelines(f_in)

            self.file_available = True
            self.file_created = datetime.fromtimestamp(os.path.getmtime(f"{self.file_paths['storage']}xml/epg.xml")).strftime('%Y-%m-%d %H:%M:%S')

            try:
                print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}: File created successfully!")
                if len(missing_genres) > 0:
                    try:
                        with open(f"{self.file_paths['storage']}missing_genres.txt", "w") as log:
                            print("\n--- MISSING EIT MAPPINGS ---\n")
                            log.write("--- MISSING EIT MAPPINGS ---\n")
                            for i in missing_genres:
                                print(i)
                                log.write(f"* {i}\n")
                            print("----------------------------\n\n")
                            log.write("----------------------------\n")
                    except:
                        pass
            except:
                pass
            
            del missing_genres
            self.status = "File created successfully!"
            self.pr.progress = 100
            self.grabbing = False
            self.started = False
            sleep(5)
            self.status = "Idle"

        except Exception as e:
            
            if str(e) != "Process stopped.":
                with open(f"{self.file_paths['storage']}grabber_error_log.txt", "a+") as log:
                    log.write(f"--- ERROR LOG: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ---\n")
                    traceback.print_exc(file=log)
                    log.write(f"--- ERROR LOG END ---\n\n")
                
                try:
                    print(traceback.format_exc())
                except:
                    pass

            self.grabbing = False
            self.started = False
            self.cancellation = False
            self.pr.progress = 100
            if str(e) == "Process stopped.":
                self.status = "Process stopped."
            else:
                self.status = "An error occurred. Please check the log file."
            sleep(5)
            self.status = "Idle"
    
