from utils import * 
from tkinter import ttk 
from customtkinter import CTkLabel, CTkButton, CTkFrame, CTk

from messagebox import MessageBox
from defaultentry import DefaultEntryText
from imagetk import *

__all__ = ('Login',)

class Login:

    def __init__(self):

        self.root = None
        self.main = None
    
    def set_invalid(self, entry):
        entry.state(["invalid", "!disabled"])

    def check(self, username: ttk.Entry, password: ttk.Entry):
        username.state(["disabled"])
        password.state(["disabled"])
        self.main.mysql.cursor.execute("bselect * from login where NAME = %s", (username.get(),))
        result = self.main.mysql.cursor.fetchall()
        user_ = username.get()
        pass_ = password.get()
        if result:
            for name, _pass, admin in result:
                if user_ and pass_:
                    if user_ != name:
                        self.set_invalid(username)
                    if pass_ != _pass:
                        self.set_invalid(password)
                    username.bell()
                    break
        else:
            self.set_invalid(username)
            MessageBox.info('ok_cancel', ("Username or Email was not Found in the Database."
                            "\nWould you like to Sign Up?"))

    def clear(self, *names):
        DefaultEntryText.set_defaults(*names)
    
    def login(self):
        raise NotImplementedError 
        # doing this because the login requires main
        # if you see self.main its None 
        # so when i create the main file right 
        # ill create a login class and inhert this class
        # and then i can use the class `Main` from that file
