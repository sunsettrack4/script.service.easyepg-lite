from resources.lib import epg, web


file_paths = {"included": "", "storage": ""}

my_server = web.WebServer(epg.Grabber(file_paths), file_paths)
my_server.start()