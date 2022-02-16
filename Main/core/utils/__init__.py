import os
import random
import string
from datetime import date
from threading import Thread
from tkinter import ttk, IntVar
from typing import Any, Dict, List, Tuple, Union


import jwt
from customtkinter import *

from ..defaultentry import DefaultEntryText

__all__ = (  # Functions
    'center', 'join_paths', 'get_outer_path',
    'calculate', 'random_key', 'token_encode',
    'token_decode', 'insert_entry', 'load_theme',
    'dob','run_threaded', 'gender',
    # Constants
    'Color',
    # Classes
    'Defont')

Color = CTkColorManager
threads: List[Thread] = []



def center(win: CTk, w: int, h: int):
    winw, winh = win.winfo_screenwidth(), win.winfo_screenheight()
    posrt = (winw//2) - (w//2)
    poslt = (winh//2) - (h//2)
    win.geometry(f"{w}x{h}+{posrt}+{poslt}")


def join_paths(*args: str) -> str:
    return os.path.join(*args)


def get_outer_path(*paths, file: str = '', retry: int = 10):

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

        def resolve_path(outer, *paths, prev = None):
            nonlocal retry
            if 0 <= retry:
                retry -= 1
                outer = os.path.dirname(outer)
                path = join_paths(outer, *paths)

                if os.path.exists(path):
                    return path

                return resolve_path(outer, *paths, prev=path)
            else:
                raise FileNotFoundError("Could not Resolve path")
        
        path = resolve_path(outer, *paths)
                
    return path


def load_theme(win: CTk):
    # source = join_paths('themes', "Sun-Valley-gif", 'sun-valley.tcl')
    fp = get_outer_path('themes', 'Sun-Valley-gif', 'sun-valley.tcl')
    try:
        win.tk.call("source", fp)
    except tkinter.TclError:
        pass
    win.tk.call("set_theme", get_appearance_mode().lower())
    set_appearance_mode(get_appearance_mode().lower())


def calculate(x: int, y: int):
    lenght = x - 100
    posx, posy = abs(x - lenght)//2, int(y/1.25)
    return x, y, lenght, posx, posy


def random_key(k: int):
    """Generate a Random Key of lenght K"""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=k))


def token_encode(token: Union[str, dict], key: str = None, k: int = 5) -> str:
    """Store the Secret within the Token"""

    if isinstance(token, dict):
        if (key is not None) and (not isinstance(key, str)):
            raise TypeError("key must be a string")

        if key is None:
            key = random_key(k)

        token = jwt.encode(token, key)

    token = token.split('.')
    i = random.randrange(0, len(token)-1)
    token.insert(i, key)
    return '.'.join([str(i), *token])


def token_decode(token: str, full=False) -> Union[Tuple[str, str], Dict[str, Any]]:

    token = token.split('.')
    key, token = (token.pop(int(token.pop(0))),
                  '.'.join(token))
    if full:
        token_ = jwt.decode(token, key, algorithms=["HS256"])
        token_.update({'_key': key, '_token': token})
        return token_
    return key, token


def insert_entry(entry: CTkEntry, text: str):
    """Insert text into an Entry"""
    entry.delete(0, 'end')
    entry.insert(0, text)
    entry.config(foreground='white')

def dob(frame: CTkFrame, label: str, name: str, r: int):

    # @run_threaded
    def check(_):
        try:
            y = int(year.get())
            if len(year.get()) > 4:
                DefaultEntryText.set_default('signup.age.year')
        except ValueError:
            y = 0
        
        try:
            m = int(month.get())
            if m > 12:
                DefaultEntryText.set_default('signup.age.month')
        except ValueError:
            m = 0

        try:
            d = int(day.get())
            if d > 31:
                DefaultEntryText.set_default('signup.age.day')
        except ValueError:
            d = 0

        try:
            a = int(age.get())
            if a < 110:
                today = date.today()
                insert_entry(year, today.year - a)
                insert_entry(month, today.month)
                insert_entry(day, today.day)
        except ValueError:
            a = 0

        if (y and m and d):
            today = date.today()
            a = (today.year-y) - ((today.month, today.day) < (m, d))
            if a < 110:
                age.delete(0, 'end')
                age.insert(0, str(a))
                age.config(foreground='white')

    CTkLabel(frame, text=label, text_font=('Avenir', 16),
             fg_color=None, width=170).grid(row=0+r, column=0, padx=10)

    day = ttk.Entry(frame, width=3)
    DefaultEntryText.add(day, 'DD', name+'.day').bind()
    day.grid(row=0+r, column=1, pady=10, padx=5)

    CTkLabel(frame, text='/', text_font=('Avenir', 16),
             fg_color=None, width=10).grid(row=0+r, column=2, pady=10)

    month = ttk.Entry(frame, width=4)
    DefaultEntryText.add(month, 'MM', name+'.month').bind()
    month.grid(row=0+r, column=3, pady=10, padx=5)

    CTkLabel(frame, text='/', text_font=('Avenir', 16),
             fg_color=None, width=10).grid(row=0+r, column=4, pady=10)

    year = ttk.Entry(frame, width=4)
    DefaultEntryText.add(year, 'YYYY', name+'.year').bind()
    year.grid(row=0+r, column=5, pady=10, padx=5)

    age = ttk.Entry(frame, width=4)
    DefaultEntryText.add(age, 'Age', name+'.age').bind()
    age.grid(row=0+r, column=6, pady=10, padx=15)
    for w in (day, month, year, age):
        w.bind("<KeyRelease>", check)

def gender(frame: CTkFrame, r: int, fg):
    style = ttk.Style(frame)
    style.configure(
        'black.TRadiobutton',
        background=Color.ENTRY[AppearanceModeTracker.appearance_mode]
    )
    gender = IntVar()
    male = ttk.Radiobutton(frame, text='Male', variable=gender, value=1, style='black.TRadiobutton')
    male.grid(row=0+r, column=1, pady=10, padx=5)

    female = ttk.Radiobutton(frame, text='Female', variable=gender, value=2, style='black.TRadiobutton')
    female.grid(row=0+r, column=2, pady=10, padx=5)

    other = ttk.Radiobutton(frame, text='Other', variable=gender, value=3, style='black.TRadiobutton')
    other.grid(row=0+r, column=3, pady=10, padx=5)
    return gender


def run_threaded(func):
    
    def inner(*args, **kwargs):
        thread = Thread(target=func, args=args, kwargs=kwargs)
        threads.append(thread)
        thread.start()
    return inner    

class Defont:

    font = ("Avenir", )

    @classmethod
    def add(cls, size: int, extra: str = ''):
        if not isinstance(extra, str):
            raise ValueError("extra must be a string")

        return cls.font + (size, ) if not extra else cls.font + (size, extra)
