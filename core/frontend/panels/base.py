from tkinter import ttk, StringVar, IntVar
from typing import Callable
from core.backend.config import Config

from core.backend.imagetk import get_image
from core.backend.utils import Color, Defont, get_outer_path
from customtkinter import *


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
            self.main._set_and_run(self.main.frames[func], func)


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

        if 3 > self.level >= 1:
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
        def _set_config(option, var):
            Config.config['app'][option] = 'True' if var.get() == 1 else 'False'
            Config.config.write(f)

        with open(get_outer_path('config', 'config.cfg'), 'w') as f:
            self._transition()
            main: CTkFrame = self.main.frames['main']
            
            var1 = IntVar()
            var2 = IntVar()

            a = CTkButton(main, text_font=Defont.add(30, font='Montserrat'), height=50,
                        width=200, text="Settings", fg_color=main.fg_color, hover=False,
                        image=get_image('settings.svg', wh=0.3), compound='left')
            a.grid(row=0, column=0, padx=10, pady=10, sticky='nw')

            about = "User Settings."
            l = CTkLabel(main, text_font=Defont.add(11), height=50,
                    width=600, text=about, fg_color=main.fg_color)
            l.text_label.grid_configure(sticky='w')
            l.grid(row=2, column=0, padx=10, sticky='nw')

            CTkFrame(main, height=5).grid(row=3, column=0, columnspan=2,
                                        padx=20, pady=10, sticky='ew')
            main.grid_columnconfigure(1, weight=1)

            r=4
            for setting in ('Theme Mode', 'Cache', 'Save User Information'):

                inner = CTkFrame(main, fg_color=Color.ENTRY_COLOR)
                CTkLabel(inner, text=setting, 
                        text_font=Defont.add(15)).pack(padx=10, anchor='nw', pady=10, side='left')
                if 'Mode' in setting:
                    def _set_mode(e):
                        set_appearance_mode(e.lower())
                        color = ['light', 'dark'][AppearanceModeTracker.appearance_mode]
                        self.main.tk.call('set_theme', color)
                        self.main.state('zoomed')

                    options = ['System', 'System', 'Light', 'Dark']
                    ttk.OptionMenu(inner, StringVar(), *options,
                                    command=_set_mode).pack(padx=10, anchor='nw', pady=10, side='left')
                
                elif setting == 'Cache':
                    current = Config.config.get('app', 'cache')
                    switch = ttk.Checkbutton(inner, style='Switch.TCheckbutton', onvalue=1, offvalue=0,
                                    command=lambda: _set_config('cache', var1), variable=var1)
                    var1.set(1 if current=='True' else 0)
                    switch.pack(padx=10, pady=10, anchor='nw', side='left')
                
                elif setting == 'Save User Information':
                    current = Config.config.get('app', 'save_user_info')
                    switch = ttk.Checkbutton(inner, style='Switch.TCheckbutton', onvalue=1, offvalue=0,
                                            command=lambda: _set_config('save_user_info', var2), variable=var2)
                    var2.set(1 if current=='True' else 0)
                    switch.pack(padx=10, anchor='nw', pady=10, side='left')

                inner.grid(row=r, column=0, padx=10, pady=20, sticky='nw')

                r += 1


def transition(func):
    def wrapper(*args, **kwargs):
        self, *other = args
        try:
            Panel._transition(self.panel)
        except AttributeError:
            Panel._transition(self)

        return func(self, *other, **kwargs)
    return wrapper
