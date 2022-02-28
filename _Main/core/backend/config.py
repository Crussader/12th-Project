import os
from configparser import ConfigParser
from typing import Any, Dict

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
    def _set_default(cls, config: ConfigParser):
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
        
        config.read_dict(data)
    
        with open(cls.path, "w") as f:
            config.write(f)

    @classmethod
    def load(cls, section: str = "", file: str = ""):
        config = ConfigParser()
        data = config.read_dict(
            {}, (cls.path if not file else get_outer_path("config", file + ".cfg"))
        )
        if not data:
            Config._set_default(config)

        cls.config = config
        if section:
            return config[section]
        return config

    @classmethod
    def add_user_config(cls, username: str, data: Dict[str, Any]):
        config = cls.load(file="user")
        if config["app"]["save_user_info"]:
            if not config.has_section("users"):
                config.add_section("users")

            token = token_encode(data, k=10)
            config.set("users", username, token)

    @classmethod
    def get_user_config(cls, username: str) -> Dict[str, Any]:
        config = cls.load()
        if config["app"]["save_user_info"]:
            token = config.get("users", username)
            key, token = token_decode(token)
            return jwt.decode(token, key)
        return {}


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
