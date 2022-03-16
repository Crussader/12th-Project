import os
import random
import string
from datetime import date
from threading import Thread, current_thread
from typing import Any, Dict, Tuple, Union

import jwt
from customtkinter import *

__all__ = (  
    # Functions
    "get_outer_path",
    "calculate",
    "random_key",
    "token_encode",
    "token_decode",
    "get_age",
    "chunk",
    # Constants
    "Color",
    # Classes
    "Defont",
    "ThreadPool"
)

Color = CTkThemeManager

def chunk(iter, at: int = 10):

    for i in range(0, len(iter), at):
        yield iter[i: i+at]


def get_outer_path(*paths, file: str = __file__, retry: int = 10):
    
    path = os.path.join(*paths)
    if os.path.exists(path):
        return path


    file = file or __file__
    outer = os.path.dirname(file)
    path = os.path.join(outer, *paths)
    if not os.path.exists(path):

        # resolves a path by recursively walking up the tree
        # and cheecking if it exists or not
        # should be efficient since we wont have huge directory trees

        def resolve_path(outer, *paths):
            nonlocal retry
            if 0 <= retry:
                retry -= 1
                outer = os.path.dirname(outer)
                path = os.path.join(outer, *paths)
                if os.path.exists(path):
                    return path
                
                return resolve_path(outer, *paths)
            else:
                path = os.path.join(outer, *paths)
                raise FileNotFoundError("Could not Resolve path, %s" % path)

        path = resolve_path(outer, *paths)

    return path


def calculate(x: int, y: int):
    lenght = x - 100
    posx, posy = abs(x - lenght) // 2, int(y / 1.25)
    return x, y, lenght, posx, posy


def random_key(k: int):
    """Generate a Random Key of lenght K"""
    return "".join(random.choices(string.ascii_letters + string.digits, k=k))


def token_encode(token: Union[str, dict], key: str = None, k: int = 5) -> str:
    """Store the Secret within the Token"""

    if isinstance(token, dict):
        if (key is not None) and (not isinstance(key, str)):
            raise TypeError("key must be a string")

        if key is None:
            key = random_key(k)

        token = jwt.encode(token, key)

    token = token.split(".")
    i = random.randrange(0, len(token) - 1)
    token.insert(i, key)
    return ".".join([str(i), *token])


def token_decode(token: str, full=False) -> Union[Tuple[str, str], Dict[str, Any]]:

    token = token.split(".")
    key, token = (token.pop(int(token.pop(0))), ".".join(token))
    if full:
        token_ = jwt.decode(token, key, algorithms=["HS256"])
        token_.update({"_key": key, "_token": token})
        return token_
    return key, token

def get_age(dob):
    today = date.today()
    return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))

def rand_id(k=10):
    return int(''.join(random.choices(string.digits, k=k))[:k])

class ThreadPool:

    threads: Dict[str, Thread] = {}
    results: Dict[str, Any] = {}
    _is_checking = False

    @classmethod
    def run_threaded(cls):
        def wrapper(func):
            def inner(*args, **kwargs):
                t = Thread(target=func, args=args, 
                           kwargs=kwargs)
                cls.threads[t.name] = t
                t.start()
                return t.name
            return inner
        return wrapper
    
    @classmethod
    def get(cls, t: str):
        thread = cls.threads.get(t)
        if thread:
            return thread if thread.is_alive() else None
        return None

    @classmethod
    def wait_result(cls, t: str):
        while True:
            res = cls.results.get(t)
            if res:
                break
        del cls.results[t]
        return res
        
    @classmethod
    def add(cls, other: Any):
        thread = current_thread()
        cls.results[thread.name] = other


class Defont:
    fonts = ("Avenir", )

    @classmethod
    def add(cls, size: int, extra: str = "", font: str=''):
        if not isinstance(extra, str):
            raise ValueError("extra must be a string")

        if font:
            font = (cls.fonts[cls.fonts.index(font)], )
        else:
            font = (cls.fonts[-1], )
        return font + (size,) if not extra else font + (size, extra)

    @classmethod
    def new(cls, font: str):
        import pyglet

        pyglet.font.add_file(get_outer_path('assets', 'fonts', font))
        cls.fonts += (font.split('.')[0], )
        return cls


# check_threads()
