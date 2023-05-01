from resources.lib import db, epg, web


file_paths = {"included": "", "storage": ""}

us = db.UserData(file_paths)
pr = db.ProviderManager(file_paths, us)

my_server = web.WebServer(epg.Grabber(file_paths, pr, us), file_paths)
my_server.start()