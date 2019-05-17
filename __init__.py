#!/usr/bin/python3
from logging import basicConfig, getLogger, FileHandler, INFO, DEBUG
from requests import Session
from os import path
from json import load, dump

import config

if config.Telegram.token: from telegram import Bot, ParseMode
if config.RSS.atom_file or config.RSS.rss_file: from feedgen.feed import FeedGenerator


basicConfig(level=INFO, format='%(asctime)s|%(levelname)s\t| %(message)s', filemode='a')
log = getLogger()
if config.General.logfile:
    fh = FileHandler(config.General.logfile)
    fh.setLevel(DEBUG)
    log.addHandler(fh)
log.info("Started!")
session = Session()
# badges = {}

def loadBadges():
    if not path.exists(config.General.json_cache_file):
        with open(config.General.json_cache_file, 'w') as f: f.write("{}")
    with open(config.General.json_cache_file) as json_data:
        json = load(json_data)
        log.info("Loaded {} badges from {}".format(len(json), config.General.json_cache_file))
        return json

def saveBadges():
    if len(badges) < 1: log.error("Badges are empty, not saving!")
    with open(config.General.json_cache_file, 'w') as f:
        dump(badges, f, indent=4, sort_keys=True)
    log.info("Saved {} badges to {}".format(len(badges), config.General.json_cache_file))

def updateBadges(save=False):
    download = session.get(config.General.json_url)
    # content = download.content.decode('utf-8')
    """
    if(save):
        with open(file, "a") as f:
            f.write("\nStable,")
    """
    json = download.json()
    log.info("Loaded {} badges from {}".format(len(json), config.General.json_url))
    return json

ignore = False
badges = loadBadges()
if len(badges) < 1:
    log.warning("Local badges empty, ignoring this run!")
    ignore = True
rbadges =  updateBadges()
if len(rbadges) < 1:
    log.error("No badges returned by server, breaking!")
    exit(1)
changed = []
newbadges = badges.copy()
for badge in rbadges:
    if badge in badges:
        for field in badges[badge].keys():
            if not rbadges[badge][field] == badges[badge][field]:
                changed.append("\u26A0 Badge changed: \"{}\"\nUUID: \"{}\"\nField: {}\nFrom: \"{}\"\nTo: \"{}\"!".format(badges[badge]["title"], badge, field.upper(), badges[badge][field], rbadges[badge][field]))
    else:
        newbadges[badge] = rbadges[badge]
        changed.append(u"\u2705 New Badge: \"{}\"\nUUID: \"{}\"\nTitle: \"{}\"\nDescription: \"{}\"\nURL: \"{}\"".format(rbadges[badge]["basename"], badge, rbadges[badge]["title"], rbadges[badge]["description"], rbadges[badge]["url"]))
for badge in badges:
    if not badge in rbadges:
        changed.append(u"\U0001F5D1 Badge removed: \"{}\"\nUUID: \"{}\"".format(badges[badge]["title"], badge))
        del newbadges[badge]
badges = newbadges
if changed:
    if not ignore:
        if config.Telegram.token:
            tg_text = config.Telegram.prefix+"\n\n".join(changed).replace("\"", "`")
            tgbot = Bot(config.Telegram.token)
            for msg in [tg_text[i:i + 4069] for i in range(0, len(tg_text), 4069)]:
                try: tgbot.send_message(chat_id=config.Telegram.chat, text=msg, parse_mode=ParseMode.MARKDOWN)
                except: u"\u274C Error sending notification to Telegram!"
        if config.RSS.atom_file or config.RSS.rss_file:
            fg = FeedGenerator()
            fg.id("0")
            fg.title('TeamSpeak Badge Notifications')
            fg.author({'name': 'Bluscream'})
            fg.link(href='https://minopia.de/ts/badges', rel='alternate')
            fg.logo('https://teamspeak.com/user/themes/teamspeak/img/favicon/mstile-144x144.png')
            fg.subtitle('Feed for any TeamSpeak Badge Changes!')
            fg.link(href='https://minopia.de/ts/badges/feed.atom', rel='self')
            fg.language('en')
            i = 0
            for change in changed:
                i += 1
                fe = fg.add_entry()
                fe.id(str(i))
                fe.title(change)
                fe.link(href="http://yat.qa/ressourcen/abzeichen-badges/")
            fg.atom_file('atom.xml')  # Write the ATOM feed to a file
            fg.rss_file('rss.xml')  # Write the RSS feed to a file
    badges = rbadges; saveBadges()
    log_txt = "{} MODIFICATIONS DETECTED!\n".format(len(changed))
    log_txt += "\n\n".join(changed)
    # try: log.info(log_txt)
    # except UnicodeEncodeError:
    log.info(log_txt.encode("utf-8"))
    print(log_txt)

log.info("Finished!")