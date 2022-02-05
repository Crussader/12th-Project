from configparser import ConfigParser
from typing import Any, Dict

import jwt
from customtkinter import get_appearance_mode

from utils import *

__all__ = ('Config',)

class Config:

    path: str = get_outer_path('config', 'config.cfg')
    config: ConfigParser = None

    @classmethod
    def _set_default(cls, config):
        mode = get_appearance_mode().lower()
        data = {
            'app': {
                'dark': True if mode == 'dark' else False,
                'cache': True,
                'save_user_info': True,
                'save_path': 'default'
            },
            'database': {
                'host': '',
                'user': '',
                'password': '',
                'database': 'main',
            },
            'users': {}
        }
        config.read_dict(data)
        with open(cls.path, "w") as f:
            config.write(f)

    @classmethod
    def load(cls, section: str = ''):
        config = ConfigParser()
        data = config.read_dict({}, cls.path)
        if not data:
            data = Config._set_default()

        cls.config = config
        if section:
            return config[section]
        return config

    @classmethod
    def add_user_config(cls, username: str, data: Dict[str, Any]):
        config = cls.load()
        if config["app"]["save_user_info"]:
            if not config.has_section('users'):
                config.add_section('users')
            
            key = random_key(5)
            token = jwt.encode(data, key, algorithm='HS256')
            token = token_encode(token, key)
            config.set('users', username, token)
        
    @classmethod
    def get_user_config(cls, username: str) -> Dict[str, Any]:
        config = cls.load()
        if config["app"]["save_user_info"]:
            token = config.get('users', username)
            key, token = token_decode(token)
            return jwt.decode(token, key)
        return {}
