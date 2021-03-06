from functools import partial
from typing import Callable

from customtkinter import *

from core.backend.imagetk import get_image
from core.backend.utils import Color, Defont


class Panel:
    level = 0

    def __init__(self, main):
        self.main = main

    def _hover(self, frame: CTkFrame, color_in=None, color_out=None, check: Callable=None):
        color_in = color_in or Color.LABEL_BG_COLOR
        color_out = color_out or Color.FRAME_2_COLOR
        widgets = [w for w in frame.children.values()
                   if isinstance(w, (CTkButton, CTkLabel, CTkFrame))]

        def enter(_):
            self.main.after(150)
            for widget in widgets:
                widget.configure(fg_color=color_in)
            frame.config(fg_color=color_in)

        def leave(_):
            if check and check() is True:
                return

            for widget in widgets:
                widget.configure(fg_color=color_out)
            frame.config(fg_color=color_out)

        frame.bind("<Enter>", enter)
        frame.bind("<Leave>", leave)

    def _shortcut(self, master: CTkFrame, image: str, text: str, sub_text: str, func: str):
        def command():
            if isinstance(func, str):
                self.main._set_and_run(self.main.frames[func], func)
            else:
                func()

        frame = CTkFrame(master, cursor='hand2', corner_radius=30)
        CTkFrame(frame, height=50, fg_color=frame.fg_color).pack(pady=20)
        short = CTkButton(frame, text=text, fg_color=frame.fg_color,
                          compound="top", image=get_image(image),
                          hover=False, text_font=Defont.add(20, font='Montserrat'),
                          command=command)
        short.pack(pady=5, padx=20)

        CTkLabel(frame, text=sub_text, width=350, fg_color=frame.fg_color,
                 text_font=Defont.add(11, font='Montserrat'), text_color="lightgrey").pack(pady=10)

        CTkFrame(frame, height=50, fg_color=frame.fg_color).pack(pady=20)

        frame.pack(side="left", padx=110, ipadx=10)
        self._hover(frame, color_out=frame.fg_color)

    def _transition(self):
        prev: CTkFrame = self.main.frames['main']
        config = prev.place_info()

        self.main._shrink('diagonal', prev, relheight=float(config.get('relheight')),
                        relwidth=float(config.get('relwidth')))

        main = CTkFrame(self.main)
        self.main.frames['main'] = main
        main.place(relx=config.get('relx'), rely=config.get('rely'))
        self.main._expand('diagonal', main, relheight=float(config.get('relheight')),
                        relwidth=float(config.get('relwidth')), layout='place')
        
    def _load_button(self, frame, image: str, size: int, func: str, first=False):
        btn_frame = CTkFrame(frame, fg_color=Color.LABEL_BG_COLOR if first else frame.fg_color,
                             cursor='hand2')
        btn = CTkButton(btn_frame, image=get_image(image, wh=size), text='',
                        fg_color=Color.LABEL_BG_COLOR if first else frame.fg_color,
                        command=lambda: self.main._set_and_run(btn_frame, func),
                        width=100, hover=False)

        self._hover(btn_frame, color_out=frame.fg_color,
                    check=lambda: (self.main.current == btn_frame))

        btn.pack(pady=5, padx=5, side='right')
        btn_frame.pack(pady=20, padx=4)
        return btn_frame


    def home(self):
        raise NotImplementedError()

    def load_tab(self):
        tab = self.main.frames["tab"]

        home = self._load_button(tab, 'home.svg', 0.1, 'home', first=True)
        self.main.home_button = home

        if self.level >= 1:
            add_user = self._load_button(tab, 'add-user.svg', 0.11, 'add_user')
            self.main.frames['add_user'] = add_user
            if self.level > 1:
                find_user = self._load_button(tab, 'find-user.svg', 0.11, 'find_user')
                self.main.frames['find_user'] = find_user

        if self.level >= 1:
            if self.level == 1:
                users = self._load_button(tab, 'users.svg', 0.11, 'users')
                self.main.frames['users'] = users

            update_user = self._load_button(
                tab, 'update-user.svg', 0.11, 'update_paitent' if self.level > 1 else 'doctor_updates')
            self.main.frames['update_paitent' if self.level > 1 else 'doctor_updates'] = update_user

        if self.level == 3:
            delete_user = self._load_button(tab, 'remove-user.svg', 0.11, 'delete_user')
            self.main.frames['delete_user'] = delete_user

        # settings = CTkButton(tab, image=get_image("settings.svg", wh=0.11), cursor='hand2',
        #                      text='', fg_color=Color.FRAME, width=80, height=70, hover_color=Color.LABEL_BG_COLOR,
        #                      command=lambda: self.main._set_and_run(settings, "settings"))
        # settings.pack(pady=10, side='bottom')
        settings = self._load_button(tab, 'settings.svg', 0.11, 'settings')
        settings.pack_configure(side='bottom')

    def settings(self):

        self._transition()
        main: CTkFrame = self.main.frames['main']


def transition(func):
    def wrapper(*args, **kwargs):
        self, *other = args
        try:
            Panel._transition(self.panel)
        except AttributeError:
            Panel._transition(self)

        return func(self, *other, **kwargs)
    return wrapper