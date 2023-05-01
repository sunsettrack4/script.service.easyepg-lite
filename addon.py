from resources.lib import db, epg, web
from os import mkdir
from threading import Thread
import xbmc, xbmcvfs, xbmcaddon

__addon__       = xbmcaddon.Addon(id='script.service.easyepg-lite')
__addondir__    = xbmcvfs.translatePath(__addon__.getAddonInfo('profile'))
__addonpath__   = xbmcvfs.translatePath(__addon__.getAddonInfo('path'))

file_paths = {"included": __addonpath__, "storage": __addondir__}

# CREATE ADDON_DATA FOLDER
try:
    mkdir(file_paths["storage"])
except FileExistsError:
    pass

us = db.UserData(file_paths)
pr = db.ProviderManager(file_paths, us)

my_server = web.WebServer(epg.Grabber(file_paths, pr, us), file_paths)

# START SERVER (+ STOP SERVER BEFORE CLOSING KODI)
def check_for_quit_event():
    monitor = xbmc.Monitor()
    while not monitor.abortRequested():
        if monitor.waitForAbort(1):
            break
    my_server.stop_kodi()


monitor_kodi = Thread(target=check_for_quit_event)
monitor_kodi.start()
my_server.start()
monitor_kodi.join()
