import textwrap
from tkinter import Toplevel, ttk
from customtkinter import *
from typing import Callable
from utils import *
from imagetk import *

__all__ = ('MessageBox',)

class MessageBox:

    root = None

    @classmethod
    def create(cls, level: str, type_: str, message: str, yes_command: Callable[[None], None]=None, no_command: Callable[[None], None]=None):

        if (yes := not callable(yes_command)) or (no := not callable(no_command)):
            msg = (f"{'yes_command and no_command' if yes and no else 'yes_command' if yes else 'no_command'}"
                   " must be callable")
            raise TypeError(msg)

        if type_ not in ['yes_no', 'ok_cancel']:
            raise ValueError(f"type_ must be 'yes_no' or 'ok_cancel' not {type_}")
        else:
            yes, no = type_.split('_')
            yes, no = yes.capitalize(), no.capitalize()
        
        if level not in ['info', 'warning', 'error']:
            raise ValueError(f"level must be 'info', 'warning' or 'error' not {level}")
        else:
            level = level.capitalize()
        
        message = textwrap.wrap(message, width=40, fix_sentence_endings=True)

        win = Toplevel()
        cls.root = win
        win.overrideredirect(True)
        win.geometry("500x200")
        load_theme(win)
        center(win, 500, 200)
        title_frame = ttk.Frame(win, relief='flat')
        close = ttk.Button(title_frame, text="X", command=win.destroy)
        title = ttk.Label(title_frame, text=type_, font=DefFont.add(15))
        close.pack(side='right')
        title.pack(side='top')
        title_frame.grid(row=0, column=0, columnspan=2, sticky='ew')
        title_frame.rowconfigure(0, weight=1)

        icon = get_image(type_.lower()+'.png', (50, 50), True)
        CTkLabel(win, image=icon, fg_color=win["bg"], 
                 text='', height=60, width=100).grid(row=1, column=0, sticky='w', padx=20)
        CTkLabel(win, text='\n'.join(message), text_font=DefFont.add(13),
                 width=300, height=100, fg_color=None).grid(row=1, column=1, sticky='w', padx=20)

        CTkButton(win, text=yes, command=yes_command, width=100).place(relx=0.45, rely=0.8)
        CTkButton(win, text=no, command=no_command, 
                  fg_color=Color.FRAME, width=100).place(relx=0.7, rely=0.8)

        win.mainloop()
        
    @classmethod
    def info(
        cls,
        type_: str,
        message: str, 
        yes_command: Callable[[None], None]=(lambda: print('yes')), 
        no_command: Callable[[None], None]=(lambda: print('no'))
    ) -> None:
        cls.create('info', type_, message, yes_command, no_command)
    
    @classmethod
    def warning(
        cls,
        type_: str,
        message: str, 
        yes_command: Callable[[None], None]=(lambda: print('yes')), 
        no_command: Callable[[None], None]=(lambda: print('no'))
    ) -> None:
        cls.create('warning', type_, message, yes_command, no_command)
    
    @classmethod
    def error(
        cls,
        type_: str,
        message: str, 
        yes_command: Callable[[None], None]=(lambda: print('yes')), 
        no_command: Callable[[None], None]=(lambda: print('no'))
    ) -> None:
        cls.create('error', type_, message, yes_command, no_command)

if __name__ == '__main__':
    MessageBox.info('info', 'This is an info message', lambda: print('yes'))