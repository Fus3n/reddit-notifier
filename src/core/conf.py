from configparser import RawConfigParser
import os

FILE_LOC_DIR = os.path.dirname(__file__)

ICON_FILE = "icons/icon.png"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36 Edge/105.0.1343.33"

# FILE_NAME = os.path.join(FILE_LOC_DIR, "noti_config.ini")
FILE_NAME = "noti_config.ini"

SUBREDDITS_SECTION = "subreddits"
SUBREDDIT_NAMES = "subreddit_names"

USER_SECTION = "user"
CLIENT_SECTION = "client"

USER_USERNAME = "user_name"
USER_PASS = "user_pass"

CLIENT_ID = "client_id"
CLIENT_SECRET = "client_secret"

SETTINGS_SECTION = "settings"
SETTINGS_DELAY = "repeat_delay"

def init():
    # create file if not exists
    if not os.path.exists(FILE_NAME):
        config = RawConfigParser()
        config.add_section(SUBREDDITS_SECTION)
        config.add_section(USER_SECTION)
        config.add_section(CLIENT_SECTION)
        config.add_section(SETTINGS_SECTION)
        config.set(SETTINGS_SECTION, SETTINGS_DELAY, "20")
        with open(FILE_NAME, 'w') as f:
            config.write(f)

def config():
    parser = RawConfigParser()
    parser.read(FILE_NAME)
    return parser

def set_config(section, key, value):
    parser = config()
    parser.set(section, key, value, raw=True)

def get_config(section, key, fallback=""):
    parser = config()
    return parser.get(section, key, fallback=fallback, raw=True)

def save_config(config: RawConfigParser):
    with open(FILE_NAME, 'w') as f:
        config.write(f)

def parse_subreddits(config: RawConfigParser):
    items = config.get(SUBREDDITS_SECTION, SUBREDDIT_NAMES, fallback="", raw=True)
    return [item.strip() for item in items.split(",") if item.strip() != ""]

def has_valid_config() -> bool:
    """checks and returns if file exists and or if the appropriate fields are empty or not""" 
    if not os.path.exists(FILE_NAME):
        return False
    
    parser = config()
    if parser.get(USER_SECTION, USER_USERNAME, fallback="") == "" or parser.get(USER_SECTION, USER_PASS, fallback="") == "" or parser.get(CLIENT_SECTION, CLIENT_ID, fallback="") == "" or parser.get(CLIENT_SECTION, CLIENT_SECRET, fallback="") == "":
        return False
    
    return True