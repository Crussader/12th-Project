import numpy
from customtkinter import *

from core.backend import *
from core.frontend import *


def loading_screen(app):
    # cls.root.after(1000)
    # creating a new window while the old one is running
    # causes the gif and other labels to not even work
    # so destroying it and creating a new one is better

    # using cls.root.after(1000, cls.root.destroy)
    # still creates next window so by just waiting for 1 second
    # then destroying manually works
    from core.backend import utils as backend_utils
    from core.frontend import utils

    def calculate(x: int, y: int):
        lenght = x - 100
        posx, posy = abs(x - lenght)//2, int(y/1.25)
        return x, y, lenght, posx, posy

    def _set_database_attr():
        app.db = Database.from_config()

    def load():
        operations = {"Connecting to a Database": _set_database_attr,
                      "Loading Theme...": lambda: utils.Color.initialize_color_theme('blue'),
                      "Loading Fonts...": lambda: backend_utils.Defont.new('Montserrat.ttf'),
                      "Starting Program...": lambda: None}
        name = iter(operations.keys())
        tasks = iter(operations.values())
        for start in numpy.arange(0, 1, 0.25):
            loading_text.set_text(next(name))
            win.after(50)
            for num in numpy.arange(start, start+.25, 0.0025):
                prog_bar.set(num)
                loading_perc.set_text(f"{round(num, 2)*100}%")
                win.update()

            next(tasks)()

        # load login in
        login = Login()
        login.main = app
        utils.fade_in_out(win, login, login.login)

    win = CTk()
    win.attributes('-topmost', True)
    win.overrideredirect(True)

    w, h, length, posx, posy = calculate(900, 500)
    win.geometry(f"{w}x{h}")
    win.minsize(w, h)
    utils.center(win, w, h)

    prog_bar = CTkProgressBar(win, width=length)
    prog_bar.set(0)

    loading_text = CTkLabel(win, text="Loading...", width=250, fg_color=None)
    loading_perc = CTkLabel(win, text="0%", fg_color=None)

    title = CTkLabel(win, text="Hospital Program",
                     text_font=("Shree Devanagari 714", 30),
                     corner_radius=8, width=330, height=48,
                     fg_color=None)
    title.pack(pady=5)

    gif = GIF("assets/basic/medi.gif", win, width=200, height=200, text='')
    gif.start()
    gif.pack(pady=30)

    prog_bar.place(x=posx, y=posy)
    loading_text.place(x=posx-50, y=posy-50)
    loading_perc.place(x=w-150, y=posy-50)

    win.after(500, load)
    win.mainloop()
