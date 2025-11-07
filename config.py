import configparser
import os

CONFIG_FILE = 'config.ini'

def load_all_config():
    if not os.path.exists(CONFIG_FILE):
        raise FileNotFoundError(f"File {CONFIG_FILE} not found.")
        
    config = configparser.ConfigParser(interpolation=None)
    config.read(CONFIG_FILE)
    
    try:
        username = config['LASTFM_USER']['username']
        password = config['LASTFM_USER']['password']
        if not username or not password:
             raise ValueError("Username or password in [LASTFM_USER] is empty.")
        user_credentials = (username, password)
    except KeyError:
        raise KeyError("Section [LASTFM_USER] not found in config.ini.")

    try:
        api_keys = {
            'discogs_token': config['API_KEYS']['discogs_app_token'],
            'lastfm_key': config['API_KEYS']['lastfm_app_key'],
            'lastfm_secret': config['API_KEYS']['lastfm_app_secret']
        }
        if not all(api_keys.values()):
            raise ValueError("One or more API keys in [API_KEYS] are empty.")
    except KeyError:
        raise KeyError("Section [API_KEYS] or required keys not found in config.ini.")
        
    return user_credentials, api_keys