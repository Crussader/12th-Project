import textwrap
from tkinter import Toplevel, ttk
from typing import Callable

from customtkinter import *

from ..backend.utils import Defont, Color
from ..backend.imagetk import get_image
from .utils import *

__all__ = ('MessageBox',)

NONE_COMMAND = (lambda: None)

class MessageBox:

    root = None

    @classmethod
    def command(cls, command):
        def inner():
            cls.root.destroy()
            command()
        return inner

    @classmethod
    def create(cls, level: str, type_: str, message: str, yes_command: Callable[[None], None] = None, no_command: Callable[[None], None] = None):

        if (yes := not callable(yes_command)) or (no := not callable(no_command)):
            msg = (f"{'yes_command and no_command' if yes and no else 'yes_command' if yes else 'no_command'}"
                   " must be callable")
            raise TypeError(msg)

        if type_ not in ['yes_no', 'ok_cancel']:
            raise ValueError(
                f"type_ must be 'yes_no' or 'ok_cancel' not {type_}")
        else:
            yes, no = type_.split('_')
            yes, no = yes.capitalize(), no.capitalize()

        if level not in ['info', 'warning', 'error']:
            raise ValueError(
                f"level must be 'info', 'warning' or 'error' not {level}")
        else:
            level = level.capitalize()

        message = textwrap.wrap(message, width=40, fix_sentence_endings=True)

        win = Toplevel()
        win.attributes('-topmost', True)
        win.overrideredirect(True)
        cls.root = win
        
        win.geometry("600x200")
        center(win, 600, 200)

        title_frame = ttk.Frame(win, relief='flat')
        close = ttk.Button(title_frame, text="X", command=win.destroy)
        title = ttk.Label(title_frame, text=level, font=Defont.add(15))
        close.pack(side='right', anchor='ne')
        title.pack(side='top', anchor='n')
        title_frame.grid(row=0, column=1, columnspan=2, sticky='ew')
        title_frame.grid_columnconfigure(1, weight=1)

        icon = get_image(level.lower()+'.png', (50, 50), basic=True)
        CTkLabel(win, image=icon, fg_color=win["bg"],
                 text='', height=60, width=100).grid(row=1, column=0, sticky='w', padx=20)
        CTkLabel(win, text='\n'.join(message), text_font=Defont.add(13),
                 width=400, height=100, fg_color=None).grid(row=1, column=1, sticky='w', padx=20)

        CTkButton(win, text=yes, command=cls.command(yes_command),
                  width=100).place(relx=0.45, rely=0.8)
        CTkButton(win, text=no, command=cls.command(no_command),
                  fg_color=Color.FRAME, width=100).place(relx=0.7, rely=0.8)

        win.mainloop()

    @classmethod
    def info(
        cls,
        type_: str,
        message: str,
        yes_command: Callable[[None], None] = NONE_COMMAND,
        no_command: Callable[[None], None] = NONE_COMMAND
    ) -> Toplevel:
        return cls.create('info', type_, message, yes_command, no_command)

    @classmethod
    def warning(
        cls,
        type_: str,
        message: str,
        yes_command: Callable[[None], None] = NONE_COMMAND,
        no_command: Callable[[None], None] = NONE_COMMAND
    ) -> Toplevel:
        return cls.create('warning', type_, message, yes_command, no_command)

    @classmethod
    def error(
        cls,
        type_: str,
        message: str,
        yes_command: Callable[[None], None] = NONE_COMMAND,
        no_command: Callable[[None], None] = NONE_COMMAND
    ) -> Toplevel:
        return cls.create('error', type_, message, yes_command, no_command)

    @classmethod
    def ask_input(
        cls,
        message: str
    ) -> Toplevel:

        win = Toplevel()
        win.attributes('-topmost', True)
        win.overrideredirect(True)
        cls.root = win
        
        win.geometry("600x200")
        center(win, 600, 200)

        title_frame = ttk.Frame(win, relief='flat')
        close = ttk.Button(title_frame, text="X", command=win.destroy)
        title = ttk.Label(title_frame, text='Question', font=Defont.add(15))
        close.pack(side='right', anchor='ne')
        title.pack(side='top', anchor='n')
        title_frame.grid(row=0, column=1, columnspan=2, sticky='ew')
        title_frame.grid_columnconfigure(1, weight=1)

        icon = get_image('question.svg', wh=0.12)
        CTkLabel(win, image=icon, fg_color=win["bg"],
                 text='', height=60, width=100).grid(row=1, column=0, sticky='w', padx=20)
        