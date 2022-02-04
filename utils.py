import os
import random
import string
from configparser import ConfigParser
from tkinter import *
from tkinter import ttk
from typing import Any, Dict, Tuple, Union

import jwt
from customtkinter import *
from PIL import Image, ImageTk
from datetime import date

def center(win: CTk, w: int, h: int):
    winw, winh = win.winfo_screenwidth(), win.winfo_screenheight()
    posrt = (winw//2) - (w//2)
    poslt = (winh//2) - (h//2)
    win.geometry(f"{w}x{h}+{posrt}+{poslt}")

def join_paths(*args: str) -> str:
    return os.path.join(*args)

def get_outer_path(*paths, file: str=''):
    file = file or __file__
    outer = os.path.dirname(file)
    return join_paths(outer, *paths)

def calculate(x: int, y: int):
    lenght = x - 100
    posx, posy = abs(x - lenght)//2, int(y/1.25)
    return x, y, lenght, posx, posy

def load_theme(win: CTk):
    color = get_appearance_mode()
    source = join_paths('themes', "Sun-Valley-gif", 'sun-valley.tcl')
    fp=get_outer_path(source)
    win.tk.call("source", fp)
    win.tk.call("set_theme", color.lower())

def fade_in_out(current: CTk, next, panel="admin"):
    next = next
    def fade_away():
        alpha = current.attributes("-alpha")
        if alpha > 0:
            alpha -= .1
            current.attributes("-alpha", alpha)
            current.after(30, fade_away)
        else:
            current.destroy()
            nonlocal next
            next = next(panel=panel)
            next.root.attributes("-alpha", 0.0)
            fade_in()

    def fade_in():
        alpha = next.root.attributes("-alpha")
        if alpha < 1:
            alpha += .1
            next.root.attributes("-alpha", alpha)
            next.root.after(30, fade_in)

    current.after(1000, fade_away)

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

def get_image(image: str, wh=(40, 40), basic=False) -> ImageTk.PhotoImage:
    """
    Load an image from the assets folder
    """
    mid = 'basic' if basic else get_appearance_mode().lower()
    fp=get_outer_path("assets", mid, image)
    with Image.open(fp) as img:
        if wh == (0, 0):
            wh = img.size
        img = img.resize(wh)
        return ImageTk.PhotoImage(img)

def entry_insert(entry: ttk.Entry, text: str):
    """Insert text into an Entry"""
    entry.delete(0, 'end')
    entry.insert(0, text)
    entry.config(foreground='white')

# not required yet # XXX
# def add_font(cls, font_fp, size: int, private=True, enumerable=False):
#     # Taken from https://stackoverflow.com/questions/11993290/truly-custom-font-in-tkinter
#     from ctypes import windll, byref, create_unicode_buffer, create_string_buffer
#     FR_PRIVATE  = 0x10
#     FR_NOT_ENUM = 0x20
#     if isinstance(font_fp, str):
#         pathbuf = create_string_buffer(font_fp)
#         AddFontResourceEx = windll.gdi32.AddFontResourceExA
#     # elif isinstance(font_fp, unicode):
#     #     pathbuf = create_unicode_buffer(font_fp)
#     #     AddFontResourceEx = windll.gdi32.AddFontResourceExW
#     else:
#         raise TypeError('font_fp must be of type str')

#     flags = (FR_PRIVATE if private else 0) | (FR_NOT_ENUM if not enumerable else 0)
#     numFontsAdded = AddFontResourceEx(byref(pathbuf), flags, 0)
#     return bool(numFontsAdded)

def dob(frame: CTkFrame, label: str, name: str, r: int):

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
                entry_insert(year, today.year - a)
                entry_insert(month, today.month)
                entry_insert(day, today.day)
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
             fg_color=None, width=100).grid(row=0+r, column=0, padx=20)

    day = ttk.Entry(frame, width=3)
    DefaultEntryText.add(day, 'DD', name+'.day').bind()
    day.grid(row=0+r, column=1, pady=10, padx=5)

    CTkLabel(frame, text='/', text_font=('Avenir', 16),
             fg_color=None, width=10).grid(row=0+r, column=2, pady=10)

    month = ttk.Entry(frame, width=3)
    DefaultEntryText.add(month, 'MM', name+'.month').bind()
    month.grid(row=0+r, column=3, pady=10, padx=5)

    CTkLabel(frame, text='/', text_font=('Avenir', 16),
             fg_color=None, width=10).grid(row=0+r, column=4, pady=10)

    year = ttk.Entry(frame, width=5)
    DefaultEntryText.add(year, 'YYYY', name+'.year').bind()
    year.grid(row=0+r, column=5, pady=10, padx=5)

    age = ttk.Entry(frame, width=3)
    DefaultEntryText.add(age, 'Age', name+'.age').bind()
    age.grid(row=0+r, column=6, pady=10, padx=10)
    for w in (month, day):
        w.bind("<KeyRelease>", check)
    
    # return month, day

class GIF(CTkLabel):

    def __init__(self, path, master, cnf: dict={}, **kwargs):
        try:
            os.open(path, os.O_RDONLY)
        except FileNotFoundError:
            path = get_outer_path(path, file=__file__)
            try:
                os.open(path, os.O_RDONLY)
            except FileNotFoundError:
                raise FileNotFoundError(f"Could Not Resolve Path: {path}")
        self.path = path

        with Image.open(self.path) as im:
            self.max = im.n_frames
        self.images = [PhotoImage(file=self.path, format="gif -index %i" % i) 
                       for i in range(self.max)]
        super().__init__(master, cnf, **kwargs)
        self.start()

    def start(self, ind: int=0):
        frame = self.images[ind]
        self.configure(image=frame,
                       background=self.master["bg"])
        ind+=1
        if ind == self.max:
            ind=0
        self.after(45, self.start, ind)

class DefaultEntryText:

    entires: Dict[str, 'DefaultEntryText'] = {}

    @classmethod
    def add(cls, entry: ttk.Entry, default_text: str='',name: str='', mode: str='', **kwargs) -> 'DefaultEntryText':

        if entry in cls.entires.values():
            return

        if not isinstance(entry, ttk.Entry):
            raise TypeError(f"Expected {type(ttk.Entry)} but got {type(entry)}")

        name = name or entry.winfo_name()
        ret = cls(default_text, entry, mode, **kwargs)
        cls.entires[name] = ret
        return ret

    @classmethod
    def get(cls, entry_or_name) -> Union[Tuple[str, 'DefaultEntryText'], None]:

        if isinstance(entry_or_name, cls):
            for k, v in cls.entires:
                if v == entry_or_name:
                    return k, v
            return None

        elif isinstance(entry_or_name, str):
            value = cls.entires.get(entry_or_name)
            if value:
                return entry_or_name, value
            return None

    @classmethod
    def set_defaults(cls, *entries: Union[str, 'DefaultEntryText']):
        if not entries:
            for k, v in cls.entires.items():
                v.set_default()
        else:
            
            for entry in entries:
                if isinstance(entry, str):
                    cls.entires.get(entry).set_default()
                else:
                    entry.set_default()


    def __init__(self, text: str, entry: ttk.Entry, mode: str='', label=None, enter_command=None, name=None):
        self.text=text
        self.entry=entry
        self.mode=mode
        self.label=label

        if enter_command and callable(enter_command):
            if (count := enter_command.__code__.co_argcount) != 1:
                raise ValueError(f"Expected 1 argument: (got {count})")
            
        elif enter_command and (not callable(enter_command)):
            raise TypeError(f"Expected a Callable but got: {type(enter_command)}")
        
        self.enter_command = enter_command
        
        if name is not None:
            self.entires[name] = self
    
    def handle_in(self, _=''):
        if self.entry.get() == self.text:
            self.entry.delete(0, 'end')
            self.entry.configure(foreground="",
                                 show="*" if self.mode=="password" else '')
        if "invalid" in self.entry.state():
            self.entry.state(["!invalid"])
            if self.label:
                if isinstance(self.label, CTkLabel):
                    self.label.set_text(" ")
    
    def handle_out(self, _=''):
        if not self.entry.get():
            self.entry.insert(0, self.text)
            self.entry.configure(foreground="grey",show="")
    
    def handle_enter(self, _=''):
        self.enter = self.entry.get()
    
    def set_default(self):
        self.entry.delete(0, 'end')
        self.entry.insert(0, self.text)
        self.entry.config(foreground='grey', show='')
    
    def bind(self):
        self.handle_out()
        self.entry.bind("<FocusIn>", self.handle_in)
        self.entry.bind("<FocusOut>", self.handle_out)
        if self.enter_command:
            command = self.enter_command
        command = self.handle_enter
        self.entry.bind("<Return>", command)

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

