from customtkinter import *

from core.backend import Database
from core.backend.utils import Defont, Color
from .base import Panel, transition

__all__ = ('DoctorPanel', )

class _BaseInit:
    def __init__(self, panel):
        self.panel = panel
        self.main = panel.main
        self.db: Database = panel.main.db


class _AddUser(_BaseInit): # adding Paitent
    
    def add_user(self):
        main: CTkFrame = self.main.frames['main']

class _FindUser(_BaseInit):

    def find_user(self):
        main: CTkFrame = self.main.frames['main']

class _UpdatePaitent(_BaseInit):

    def update_paitent(self):
        main: CTkFrame = self.main.frames['main']

class DoctorPanel(Panel):
    level = 2

    def home(self):
        if self.main.current == self.main.home_button:
            self._transition()
        else:
            self.main._set_and_run(self.main.home_button, '')
            main_win = CTkFrame(self.main, width=500, height=500)
            self.main.frames['main'] = main_win
            main_win.place(relx=0.08, rely=0.13)
            self.main._expand('diagonal', main_win, 'place',
                              relwidth=0.915, relheight=0.860)
        
        question = CTkLabel(main_win, text_font=Defont.add(30, font='Montserrat'),
                            height=50, width=700, text="What would you like to do today?",
                            fg_color=main_win.fg_color)
        question.pack(pady=20)

        self.main.after(500, self._shortcut, self.main.frames['main'], 'add-user.svg',
                        '\nAdd Paitent', 'Add a Paitent to the Database', 'add_user')
        self.main.after(500, self._shortcut, self.main.frames['main'], 'find-user.svg',
                        '\nFind Paitent', 'Find Patients From the Database!', 'find_user')
        self.main.after(500, self._shortcut, self.main.frames['main'], 'update-user.svg',
                        '\nPaitent Updates', 'Update Paitents on their situation!', 'update_paitent')

    @transition
    def add_user(self):
        _AddUser(self).add_user()

    @transition
    def find_user(self):
        _FindUser(self).find_user()
    
    @transition
    def update_paitent(self):
        _UpdatePaitent(self).update_paitent()




