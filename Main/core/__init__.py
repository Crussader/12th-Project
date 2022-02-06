import numpy
from customtkinter import CTk, CTkLabel, CTkProgressBar

from config import *
from database import *
from defaultentry import *
from imagetk import *
from login import *
from messagebox import *
from signup import *

__all__ = [a for a in globals().keys() 
           if not a.startswith(("_", "CT", "numpy"))]


def fade_in_out(current, next, *args, **kwargs):
    next = next
    
    def fade_away():
        alpha = current.attributes("-alpha")
        if alpha > 0:
            current.attributes("-alpha", alpha-0.1)
            current.after(30, fade_away)
        else:
            current.destroy()
            nonlocal next
            next = next(*args, **kwargs)
            next.root.attributes("-alpha", 0.0)
            fade_in()
    
    def fade_in():
        alpha = current.attributes("-alpha")
        if alpha < 1:
            current.attributes("-alpha", alpha+0.1)
            current.after(30, fade_in)

    current.after(1000, fade_away)

def loading_screen(cls: Login):

    from utils import calculate, center

    # cls.root.after(1000)
    # cls.root.destroy() 
    # creating a new window while the old one is running
    # causes the gif and other labels to not even work
    # so destroying it and creating a new one is better
    # using cls.root.after(1000, cls.root.destroy)
    # still creates next window so by just waiting for 1 second
    # then destroying manually works

    win = CTk()
    win.overrideredirect(True)

    w ,h, length, posx, posy = calculate(900, 500)
    win.geometry(f"{w}x{h}")
    win.minsize(w, h)
    center(win, w, h)

    prog_bar = CTkProgressBar(win, width=length)
    prog_bar.set(0)

    loading_text=CTkLabel(win, text="Loading...", width=250, fg_color=None)
    loading_perc=CTkLabel(win, text="0%", fg_color=None)
    
    title=CTkLabel(win, text="Hospital Program", 
             text_font=("Shree Devanagari 714", 30), 
             corner_radius=8, width=330, height=48, 
             fg_color=None)
    title.pack(pady=5)

    gif=GIF("assets/basic/medi.gif", win, width=200, height=200)
    gif.start()
    gif.pack(pady=30)

    prog_bar.place(x=posx, y=posy)
    loading_text.place(x=posx-50, y=posy-50)
    loading_perc.place(x=w-150, y=posy-50)


    def run():
        operations = iter((
        "Connecting to a database...",
        "Loading Theme...",
        "Loading Fonts...",
        "Starting Program...",
        ))
        for start in numpy.arange(0, 1, .25):
            win.after(50)
            loading_text.set_text(text=next(operations))
            for num in numpy.arange(start, start+.25, 0.0025):
                prog_bar.set(num)
                loading_perc.set_text(text=f"{round(num, 2)*100}%")
                win.update()

    win.after(500) # wait for .5 seconds
    run()          # load the things
    fade_in_out(win, cls.main) # fade in and out
    win.mainloop()

# if __name__ == "__main__":
#     loading_screen(Login())
    # print([a for a in globals().values() if a != '__main__' and a])
