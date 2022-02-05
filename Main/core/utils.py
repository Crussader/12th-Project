import os
import random
import string
from typing import Tuple

from customtkinter import (CTk, CTkColorManager, CTkEntry, get_appearance_mode,
                           tkinter)

__all__ = ( # Functions
           'center', 'join_paths', 'get_outer_path', 
           'calculate', 'random_key', 'token_encode', 
           'token_decode', 'insert_entry', 'load_theme',
           # Constants
           'Color',
           # Classes
           'DefFont')

Color = CTkColorManager

def center(win: CTk, w: int, h: int):
    winw, winh = win.winfo_screenwidth(), win.winfo_screenheight()
    posrt = (winw//2) - (w//2)
    poslt = (winh//2) - (h//2)
    win.geometry(f"{w}x{h}+{posrt}+{poslt}")

def join_paths(*args: str) -> str:
    return os.path.join(*args)

def get_outer_path(*paths, file: str=''):

    path = join_paths(*paths)
    if os.path.exists(path):
        return path
    
    file = file or __file__
    outer = os.path.dirname(file)
    path = join_paths(outer, *paths)

    if not os.path.exists(path):

        # resolves a path by recursively walking up the tree
        # and cheecking if it exists or not
        # should be efficient since we wont have huge directory trees

        def resolve_path(outer, *paths):
            outer = os.path.dirname(outer)
            path = join_paths(outer, *paths)
            if os.path.exists(path):
                return path
            return resolve_path(outer, *paths)
   
        path = resolve_path(outer, *paths)

    return path

def load_theme(win: CTk):
    color = get_appearance_mode()
    source = join_paths('themes', "Sun-Valley-gif", 'sun-valley.tcl')
    fp=get_outer_path(source)
    try:
        win.tk.call("source", fp)
    except tkinter.TclError:
        pass
    win.tk.call("set_theme", color.lower())

def calculate(x: int, y: int):
    lenght = x - 100
    posx, posy = abs(x - lenght)//2, int(y/1.25)
    return x, y, lenght, posx, posy

def random_key(k: int):
    """Generate a Random Key of lenght K"""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=k))

def token_encode(token: str, key: str) -> str:
    """Store the Secret within the Token"""
    token = token.split('.')
    i = random.randrange(0, len(token)-1)
    token.insert(i, key)
    return '.'.join([str(i), *token])

def token_decode(token: str) -> Tuple[str, str]:

    token = token.split('.')
    return (token.pop(int(token.pop(0))), 
            '.'.join(token))

def insert_entry(entry: CTkEntry, text: str):
    """Insert text into an Entry"""
    entry.delete(0, 'end')
    entry.insert(0, text)
    entry.config(foreground='white')

class DefFont:

    font = ("Avenir", )

    @classmethod
    def add(cls, size: int, extra: str=''):
        if not isinstance(extra, str):
            raise ValueError("extra must be a string")

        return cls.font + (size, ) if not extra else cls.font + (size, extra)
