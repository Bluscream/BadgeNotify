#!/usr/bin/python3
from json import load, dump
from telegram import Bot, ParseMode
import logging
from requests import Session
from os import path
from config import *

file = "/home/blu/bots/ts/BadgeNotify/badges.json"
tg_prefix = "[New badge modifications found](https://www.minopia.de/ts/badges):\n\n\n"

logging.basicConfig(level=logging.INFO, format='%(asctime)s|%(levelname)s\t| %(message)s', filemode='a')
log = logging.getLogger()
fh = logging.FileHandler("/home/blu/bots/ts/BadgeNotify/badgenotify.log")
fh.setLevel(logging.DEBUG)
log.addHandler(fh)
log.info("Started!")
session = Session()
# badges = {}
fields = ["basename", "description", "title", "url"]

def loadBadges():
    if not path.exists(file):
        with open(file, 'w') as f: f.write("{}")
    with open(file) as json_data:
        json = load(json_data)
        log.info("Loaded {} badges from {}".format(len(json), file))
        return json

def saveBadges():
    if len(badges) < 1: log.error("Badges are empty, not saving!")
    with open(file, 'w') as f:
        dump(badges, f, indent=4, sort_keys=True)
    log.info("Saved {} badges to {}".format(len(badges), file))

def updateBadges(save=False):
    download = session.get(url)
    # content = download.content.decode('utf-8')
    """
    if(save):
        with open(file, "a") as f:
            f.write("\nStable,")
    """
    json = download.json()
    log.info("Loaded {} badges from {}".format(len(json), url))
    return json

ignore = False
badges = loadBadges()
if len(badges) < 1:
    log.warn("Local badges empty, ignoring this run!")
    ignore = True
rbadges =  updateBadges()
if len(rbadges) < 1:
    log.error("No badges returned by server, breaking!")
    exit(1)
changed = []
for badge in rbadges:
    if badge in badges:
        for field in fields:
            if not rbadges[badge][field] == badges[badge][field]:
                changed.append("⚠️ \"{}\" changed:\nField: {}\nFrom: \"{}\"\nTo: \"{}\"!".format(badge, field.upper(), badges[badge][field], rbadges[badge][field]))
    else:
        badges[badge] = rbadges[badge]
        changed.append("✅ New Badge: \"{}\"\nUUID: \"{}\"\nTitle: \"{}\"\nDescription: \"{}\"\nURL: \"{}\"".format(badges[badge]["basename"], badge, badges[badge]["title"], badges[badge]["description"], badges[badge]["url"]))
for badge in badges:
    if not badge in rbadges:
        changed.append("🗑 Badge \"{}\" was removed!")
        del badges[badge]
if changed:
    if not ignore:
        tg_text = tg_prefix+"\n\n".join(changed).replace("\"", "`")
        tgbot = Bot(tg_token)
        for msg in [tg_text[i:i + 4069] for i in range(0, len(tg_text), 4069)]:
            try: tgbot.send_message(chat_id=tg_chatid, text=msg, parse_mode=ParseMode.MARKDOWN)
            except: "❌ Error sending notification to Telegram!"
    badges = rbadges
    saveBadges()
    log_txt = "{} MODIFICATIONS DETECTED!\n".format(len(changed))
    log.info(log_txt+"\n".join(changed))
log.info("Finished!")