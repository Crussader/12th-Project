from datetime import date

from customtkinter import *
from tkinter import ttk, TclError, IntVar

from ..backend.utils import Color, get_outer_path
from .defaultentry import DefaultEntryText

def center(win: CTk, w: int, h: int):
    winw, winh = win.winfo_screenwidth(), win.winfo_screenheight()
    posrt = (winw // 2) - (w // 2)
    poslt = (winh // 2) - (h // 2)
    win.geometry(f"{w}x{h}+{posrt}+{poslt}")

def insert_entry(entry: CTkEntry, text: str):
    """Insert text into an Entry"""
    entry.delete(0, "end")
    entry.insert(0, text)
    entry.config(foreground=Color.TEXT)


def load_theme(win: CTk):
    fp = get_outer_path('assets', "themes", "Sun-Valley-gif", "sun-valley.tcl")
    try:
        win.tk.call("source", fp)
    except TclError:
        pass
    win.tk.call("set_theme", get_appearance_mode().lower())


def dob(frame: CTkFrame, label: str, name: str, r: int):

    # @run_threaded
    def check(_):
        try:
            y = int(year.get())
            if len(year.get()) > 4:
                DefaultEntryText.set_default("signup.age.year")
        except ValueError:
            y = 0

        try:
            m = int(month.get())
            if m > 12:
                DefaultEntryText.set_default("signup.age.month")
        except ValueError:
            m = 0

        try:
            d = int(day.get())
            if d > 31:
                DefaultEntryText.set_default("signup.age.day")
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

        if y and m and d:
            today = date.today()
            a = (today.year - y) - ((today.month, today.day) < (m, d))
            if a < 110:
                age.delete(0, "end")
                age.insert(0, str(a))
                age.config(foreground="white")

    CTkLabel(
        frame, text=label, text_font=("Avenir", 16), fg_color=None, width=170
    ).grid(row=0 + r, column=0, padx=10)

    day = ttk.Entry(frame, width=3)
    DefaultEntryText.add(day, "DD", name + ".day").bind()
    day.grid(row=0 + r, column=1, pady=10, padx=5)

    CTkLabel(frame, text="/", text_font=("Avenir", 16), fg_color=None, width=10).grid(
        row=0 + r, column=2, pady=10
    )

    month = ttk.Entry(frame, width=4)
    DefaultEntryText.add(month, "MM", name + ".month").bind()
    month.grid(row=0 + r, column=3, pady=10, padx=5)

    CTkLabel(frame, text="/", text_font=("Avenir", 16), fg_color=None, width=10).grid(
        row=0 + r, column=4, pady=10
    )

    year = ttk.Entry(frame, width=4)
    DefaultEntryText.add(year, "YYYY", name + ".year").bind()
    year.grid(row=0 + r, column=5, pady=10, padx=5)

    age = ttk.Entry(frame, width=4)
    DefaultEntryText.add(age, "Age", name + ".age").bind()
    age.grid(row=0 + r, column=6, pady=10, padx=15)
    for w in (day, month, year, age):
        w.bind("<KeyRelease>", check)


def gender(frame: CTkFrame, r: int, fg):
    style = ttk.Style(frame)
    style.configure(
        "black.TRadiobutton",
        background=Color.ENTRY[AppearanceModeTracker.appearance_mode],
    )
    gender = IntVar()
    male = ttk.Radiobutton(
        frame, text="Male", variable=gender, value=1, style="black.TRadiobutton"
    )
    male.grid(row=0 + r, column=1, pady=10, padx=5)

    female = ttk.Radiobutton(
        frame, text="Female", variable=gender, value=2, style="black.TRadiobutton"
    )
    female.grid(row=0 + r, column=2, pady=10, padx=5)

    other = ttk.Radiobutton(
        frame, text="Other", variable=gender, value=3, style="black.TRadiobutton"
    )
    other.grid(row=0 + r, column=3, pady=10, padx=5)
    return gender
