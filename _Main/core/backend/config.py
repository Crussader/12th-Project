import os
from configparser import ConfigParser
from typing import Any, Dict, List

import jwt
from customtkinter import get_appearance_mode
from dotenv import load_dotenv

from .utils import get_outer_path, token_decode, token_encode

__all__ = ("Config",)

load_dotenv(get_outer_path("config", ".env"))


def get_env_key(*key: str):
    key = "_".join(key)
    val = os.getenv(key)
    return val


class Config:

    path: str = get_outer_path("config", "config.cfg")
    config: ConfigParser = None

    @classmethod
    def _set_default(cls, config: ConfigParser, file: str = 'default'):
        
        if file == 'default':
            mode = get_appearance_mode().lower()
            data = {
                "app": {
                    "dark": True if mode == "dark" else False,
                    "cache": True,
                    "save_user_info": True,
                    "save_path": "default",
                },
                "database": {
                    "host": "localhost",
                    "user": "root",
                    "password": "env",
                    "database": "hospital",
                },
            }
            for k, v in data.items():
                for key, value in v.items():
                    if value == "env":
                        env_val = get_env_key(k, key)
                        data[k][key] = env_val or ''

            if data["app"]["save_user_info"] is True:
                path = os.path.join(get_outer_path("config"), "user.cfg")
                with open(path, "w"):
                    pass
            else:
                path = cls.path
            
        else:
            data = {'users' : {}}
            path = get_outer_path('config', 'user.cfg')
        
        # print(data)
        config.read_dict(data)

        try:
            with open(path, "a") as f:
                config.write(f)
        except FileNotFoundError:
            with open(path, 'w') as f:
                config.write(f)

    @classmethod
    def load(cls, section: str = "", file: str = "default"):
        config = ConfigParser()
        # print(cls.path if file == 'default' else get_outer_path("config", file + ".cfg"))

        if file == 'default':
            with open(cls.path) as f:
                config.read_file(f)
        else:
            with open(get_outer_path('config', file+'.cfg')) as f:
                config.read_file(f)

        if not config.sections():
            Config._set_default(config, file)        

        if file == 'default':
            cls.config = config

        if section:
            return config[section]
        return config

    @classmethod
    def add_user_config(cls, id: str, data: Dict[str, Any]):
        config = Config.load() if not hasattr(cls, 'config') else cls.config

        if config["app"]["save_user_info"]:
            other = Config.load(file='users')
            token = token_encode(data, k=10)
            other.set("users", id, token)

    @classmethod
    def get_user_config(cls, id: str, _config = None) -> Dict[str, Any]:
        config = Config.load() if not hasattr(cls, 'config') else cls.config
        if config.get("app", "save_user_info"):
            other = _config or Config.load('users', 'user')
            id = other.get(id)
            
        return None

    @classmethod
    def get_all_saved_users(cls) -> List[int]:
        config = Config.load() if not hasattr(cls, 'config') else cls.config
        if config.get('app', 'save_user_info'):
            other = Config.load('users', 'user')
            ids = other.get('ids')
            if ids:
                return ids.split(',')
        return []           


# User Config Structure
# {'username': '',
#  'password': '',
#  'email': '',
#  'first_name': '',
#  'last_name': '',
#  'phone': ''}
if __name__ == "__main__":
    config = Config.load()
    # print({k: {s: o for s, o in v.items()}
    #   for k, v in config.items()})
