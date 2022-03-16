from tkinter import ttk
from typing import Dict, Union

import tksvg
from customtkinter import *
from numpy import arange

from core import *
from core.backend.utils import *
from core.frontend.utils import *

__version__ = "0.7"


class App(CTk):
    APPNAME = "Caduceus Hospital"
    frames: Dict[str, CTkFrame] = {}
    current = None
    home_button = None
    panel: Union[UserPanel, AdminPanel, DoctorPanel] = None
    db = None
    user: User = None

    def __init__(self, panel):

        self.panel = panel(self)

    def _set_and_run(self, frame: CTkFrame, func: str):

        frame.configure(fg_color=Color.LABEL_BG_COLOR)
        if self.current:
            self.after(10)
            self.frames['selected'].destroy()
            tab = self.frames['tab']
            self.current.configure(fg_color=tab.fg_color)
            for ch in self.current.winfo_children():
                if isinstance(ch, CTkButton):
                    ch.configure(fg_color=tab.fg_color)

        selected = CTkFrame(frame, fg_color=Color.MAIN_COLOR,
                            height=30, width=5)
        self.frames['selected'] = selected
        selected.pack(side='left', padx=3,
                      anchor='center', pady=10)

        for ch in frame.winfo_children():
            if isinstance(ch, CTkButton):
                ch.configure(fg_color=Color.LABEL_BG_COLOR)

        if func:
            func = getattr(
                (self.panel if func != 'home' else self), func, None)
            if func:
                func()
        
        self.current = frame

    def _expand(self, direction: str, frame: CTkFrame, layout: str = 'pack', delay: int = 1, **kw):
        if layout == 'pack':
            max = kw['max']

            def pack_diagonal(i: int):
                cnf = frame.pack_info()
                cnf['ipady'] = i
                cnf['ipadx'] = i
                frame.pack_configure(**cnf)
                if i <= max:
                    self.after(delay, pack_diagonal, i+1)

            def pack_vertical(i: int):
                cnf = frame.pack_info()
                cnf['ipady'] = i
                frame.pack_configure(**cnf)
                if i <= max:
                    self.after(delay, pack_vertical, i+1)

            if direction in ['vertical', 'diagonal']:
                func = locals().get('_'.join(('pack', direction)))
                func(0)

        elif layout == 'place':
            relheight, relwidth = kw['relheight'], kw.get('relwidth')
            counter_h = iter(arange(0, relheight, step=0.02225))
            if relwidth:
                counter_w = iter(arange(0, relwidth, step=0.02225))

            def place_diagonal(h, w):
                cnf = frame.place_info()
                cnf['relheight'] = h
                cnf['relwidth'] = w
                frame.place_configure(**cnf)
                if h <= relheight and w <= relwidth:
                    try:
                        h = next(counter_h)
                    except StopIteration:
                        h = relheight
                    try:
                        w = next(counter_w)
                    except StopIteration:
                        w = relwidth
                    self.after(delay, place_diagonal, h, w)

            def place_vertical(h: float, w=None):
                cnf = frame.place_info()
                cnf['relheight'] = h
                frame.place_configure(**cnf)
                if h <= relheight:
                    try:
                        h = next(counter_h)
                    except StopIteration:
                        h = relheight
                    self.after(delay, place_vertical, h)

            if direction in ['vertical', 'diagonal']:
                func = locals().get('_'.join(('place', direction)))
                func(0.0, 0.0)

    def _shrink(self, direction: str, frame: CTkFrame, **kw):
        relheight, relwidth = kw['relheight'], kw.get('relwidth')
        counter_h = iter(arange(relheight, 0, step=-0.02225))
        if relwidth:
            counter_w = iter(arange(relwidth, 0, step=-0.02225))

        cnf = frame.place_info()

        def place_diagonal(h, w):
            cnf['relheight'] = h
            cnf['relwidth'] = w
            frame.place_configure(**cnf)

            if h <= relheight and w <= relwidth:
                try:
                    h = next(counter_h)
                except StopIteration:
                    h = relheight
                try:
                    w = next(counter_w)
                except StopIteration:
                    w = relwidth
                self.after(1, place_diagonal, h, w)
            elif h > relheight and w > relwidth:
                frame.destroy()

        def place_vertical(h: float, w=None):
            cnf = frame.place_info()
            cnf['relheight'] = h
            frame.place_configure(**cnf)
            if h <= relheight:
                try:
                    h = next(counter_h)
                except StopIteration:
                    h = relheight
                self.after(1, place_vertical, h)

        if direction in ['vertical', 'diagonal']:
            func = locals().get('_'.join(['place', direction]))
            func(0.0, 0.0)

    def load_window(self):

        super().__init__(self.APPNAME)
        self.iconphoto(True, get_image('icon.png', basic=True))
        self.title(self.APPNAME)

        load_theme(self)
        tksvg.load(self)
        self.resizable(None, None)
        self.state('zoomed')

        tab = CTkFrame(self, width=100)
        self.frames['tab'] = tab

        logo = get_image('icon.png', basic=True)
        logo_l = CTkLabel(tab, image=logo, width=100, height=50,
                          fg_color=None)
        logo_l.image = logo
        logo_l.pack(pady=15, padx=5)

        CTkLabel(tab, text=self.APPNAME.split()[0], text_color=Color.CHECKBOX_LINES_COLOR,
                 text_font=Defont.add(12), width=100, fg_color=None).pack()

        ttk.Separator(tab).pack(fill='x', padx=5, pady=15)

        CTkFrame(tab, fg_color=tab.fg_color, width=70,
                 height=125).pack(pady=5)  # seperator

        CTkLabel(tab, text=f'V {__version__}', text_color=Color.LABEL_BG_COLOR,
                 fg_color=None, width=50, text_font=Defont.add(10)).pack(side='bottom', pady=10)
        self.panel.load_tab()

        tab.pack(anchor='w', side="left", pady=10, padx=10)

        top = CTkFrame(self, width=400, height=100)
        self.frames['top'] = top

        profile = CTkFrame(top, fg_color=top.fg_color)
        pfp = CTkButton(profile, image=get_image('user.svg', wh=0.1), text_font=Defont.add(12),
                        width=100, height=70, hover_color=top.fg_color,
                        fg_color=top.fg_color, text=self.user.name.title(), compound='right',
                        cursor='hand2')
        pfp.pack(side='right')
        profile.pack(pady=20, padx=10, side='right', anchor='ne')
        top.pack(side='right', anchor='ne', padx=10, pady=10)

        self._expand('vertical', tab, max=600)
        self.home = self.panel.home
        self.home()

        self.mainloop()

def main():
    loading_screen(App)

if __name__ == '__main__':
    main()
