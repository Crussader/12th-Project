from functools import partial
from typing import Callable

from customtkinter import *

from ...backend.imagetk import get_image
from ...backend.utils import Color, Defont


class Panel:
    level = 0

    def __init__(self, main):
        self.main = main

    def __eq__(self, __o: object) -> bool:
        if not isinstance(__o, int):
            raise TypeError(
                f"{type(__o)} can not be compared with {self.__class__.__name__}")

        return self.level == __o

    def __ne__(self, __o: object) -> bool:
        if not isinstance(__o, int):
            raise TypeError(
                f"{type(__o)} can not be compared with {self.__class__.__name__}")

        return self.level != __o

    def __ge__(self, __o: int) -> bool:
        if not isinstance(__o, int):
            raise TypeError(
                f"{type(__o)} can not be compared with {self.__class__.__name__}")

        return __o >= self.level

    def __gt__(self, __o: int) -> bool:
        if not isinstance(__o, int):
            raise TypeError(
                f"{type(__o)} can not be compared with {self.__class__.__name__}")

        return __o > self.level

    def __le__(self, __o: int) -> bool:
        if not isinstance(__o, int):
            raise TypeError(
                f"{type(__o)} can not be compared with {self.__class__.__name__}")

        return __o <= self.level

    def __lt__(self, __o: int) -> bool:
        if not isinstance(__o, int):
            raise TypeError(
                f"{type(__o)} can not be compared with {self.__class__.__name__}")

        return __o < self.level

    def _hover(self, frame: CTkFrame, color_in=Color.LABEL_BG, color_out=Color.FRAME_2, check: Callable=None):
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
        frame = CTkFrame(master, cursor='hand2', corner_radius=30)

        CTkFrame(frame, height=50, fg_color=Color.FRAME_2).pack(pady=20)

        short = CTkButton(frame, text=text, fg_color=Color.FRAME_2,
                          compound="top", image=get_image(image),
                          hover=False, text_font=Defont.add(20, font='Montserrat'),
                          command=lambda: getattr(self, func)())
        short.pack(pady=5, padx=20)

        CTkLabel(frame, text=sub_text, width=350, fg_color=Color.FRAME_2,
                 text_font=Defont.add(11, font='Montserrat'), text_color="lightgrey").pack(pady=10)

        CTkFrame(frame, height=50, fg_color=Color.FRAME_2).pack(pady=20)

        frame.pack(side="left", padx=110, ipadx=10)
        self._hover(frame)

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
        btn_frame = CTkFrame(frame, fg_color=Color.LABEL_BG if first else Color.FRAME,
                             cursor='hand2')
        btn = CTkButton(btn_frame, image=get_image(image, wh=size), text='',
                        fg_color=Color.LABEL_BG if first else Color.FRAME,
                        command=lambda: self.main._set_and_run(btn_frame, func),
                        width=100, hover=False)

        self._hover(btn_frame, color_out=Color.FRAME,
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

        if self >= 1:
            add_user = self._load_button(tab, 'add-user.svg', 0.11, 'add_user')

            if self > 1:
                find_user = CTkButton(tab, image=get_image("find-user.svg", wh=0.11), cursor='hand2',
                                      text='', fg_color=Color.FRAME, width=80, height=70, hover_color=Color.LABEL_BG,
                                      command=lambda: self.main._set_and_run(find_user, "find_user"))
                find_user.pack(pady=20)

        if self >= 1:
            if self == 1:
                users = self._load_button(tab, 'users.svg', 0.11, 'users')

            update_user = self._load_button(
                tab, 'update-user.svg', 0.11, 'update_user')

        if self == 3:
            delete_user = CTkButton(tab, image=get_image("remove-user.svg", wh=0.11), cursor='hand2',
                                    text='', fg_color=Color.FRAME, width=80, height=70, hover_color=Color.LABEL_BG,
                                    command=lambda: self.main._set_and_run(delete_user, "delete_user"))
            delete_user.pack(pady=20)

        # settings = CTkButton(tab, image=get_image("settings.svg", wh=0.11), cursor='hand2',
        #                      text='', fg_color=Color.FRAME, width=80, height=70, hover_color=Color.LABEL_BG,
        #                      command=lambda: self.main._set_and_run(settings, "settings"))
        # settings.pack(pady=10, side='bottom')
        settings = self._load_button(tab, 'settings.svg', 0.11, 'settings')
        settings.pack_configure(side='bottom')
