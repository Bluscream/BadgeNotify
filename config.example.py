import os
server = os.name == 'posix'

class General:
    json_url = "http://minopia.de/ts/badges/json.php"
    json_cache_file = "badges.json"
    logfile = "badgenotify.log"

class Telegram:
    token = ""
    chat = 0
    prefix = "[New badge modifications found](https://www.minopia.de/ts/badges):\n\n\n"

class RSS:
    atom_file = ""
    rss_file = ""
