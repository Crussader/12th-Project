from tkinter import Tk, Canvas, Toplevel, ttk 
from typing import Optional, Tuple, Union

import mysql.connector as mysql 
import numpy
from customtkinter import *
from mysql.connector.cursor import MySQLCursor
from PIL import Image, ImageTk
import textwrap
import jwt
import utils
import models

# DEF_FONT = ("Shree Devanagari 714", )
DEF_FONT = ("Avenir", )

def loading_screen(cls: "Login"):

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

    w ,h, length, posx, posy = utils.calculate(900, 500)
    win.geometry(f"{w}x{h}")
    win.minsize(w, h)
    utils.center(win, w, h)

    prog_bar = CTkProgressBar(win, width=length)
    prog_bar.set(0)

    loading_text=CTkLabel(win, text="Loading...", width=250, fg_color=None)
    loading_perc=CTkLabel(win, text="0%", fg_color=None)
    
    title=CTkLabel(win, text="Hospital Program", 
             text_font=("Shree Devanagari 714", 30), 
             corner_radius=8, width=330, height=48, 
             fg_color=None)
    title.pack(pady=5)

    gif=utils.GIF("assets/basic/medi.gif", win, width=200, height=200)
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

    win.after(1000)
    run()
    # utils.fade_in_out(win, cls.main)
    win.mainloop()

class Message:

    root = None

    @classmethod
    def create(cls, type_: str, message: str, yes_no=False, yes_command = None, no_command = None, **kwargs):

        win = Toplevel()
        cls.root = win
        win.overrideredirect(True)
        win.geometry("500x200")
        utils.load_theme(win)
        utils.center(win, 500, 200)
        title_frame = ttk.Frame(win, relief='flat')
        close = ttk.Button(title_frame, text="X", command=win.destroy)
        title = ttk.Label(title_frame, text=type_, font=DEF_FONT+(15, ))
        close.pack(side='right')
        title.pack(side='top')
        title_frame.grid(row=0, column=0, columnspan=2, sticky='ew')
        title_frame.rowconfigure(0, weight=1)

        _msg = textwrap.wrap(message, width=40, fix_sentence_endings=True)

        icon = utils.get_image(type_.lower()+'.png', (50, 50), True)
        CTkLabel(win, image=icon, fg_color=win["bg"], 
                 text='', height=60, width=100).grid(row=1, column=0, sticky='w', padx=20)
        CTkLabel(win, text='\n'.join(_msg), text_font=DEF_FONT+(13, ),
                 width=300, height=100, fg_color=None).grid(row=1, column=1, sticky='w', padx=20)
        # CTkFrame(win).pack(anchor='center')
        if yes_no or 'ok_cancel' in kwargs:
            if 'ok_cancel' in kwargs:
                yes, no = 'Ok', 'Cancel'
            else:
                yes, no = 'Yes', 'No'

            yes_command = yes_command or (lambda: print(yes))
            no_command = no_command or (lambda: print(no))

            if not callable(yes_command) or not callable(no_command):
                raise TypeError("command must be callable")

            CTkButton(win, text=yes, command=yes_command, width=100).place(relx=0.45, rely=0.8)
            CTkButton(win, text=no, command=no_command, 
                      fg_color=models.Color.FRAME, width=100).place(relx=0.7, rely=0.8)
        win.mainloop()
        return cls

    @classmethod
    def show_error(cls, message: str, yes_no=False, yes_command=None, no_command=None, **kwargs):
        cls.create(type_="Error", message=message, yes_no=yes_no, 
                   yes_command=yes_command, no_command=no_command,
                   **kwargs)
    
    @classmethod
    def show_warning(cls, message: str, yes_no=False, yes_command=None, no_command=None, **kwargs):
        cls.create(type_="Warning", message=message, yes_no=yes_no, 
                   yes_command=yes_command, no_command=no_command, 
                   **kwargs)

    @classmethod
    def show_info(cls, message: str, yes_no=False, yes_command=None, no_command=None, **kwargs):
        cls.create(type_="Info", message=message, yes_no=yes_no, 
                   yes_command=yes_command, no_command=no_command,
                   **kwargs)
    

class Database:

    def __init__(self, from_config = True, **kwargs):

        if not from_config and not kwargs:
            raise ValueError("No arguments given to connect to Database")
        
        if from_config:
            config = utils.Config.load('database')
            host = config['host']
            user = config['user']
            password = config['password']
            database = config['database']
        else:
            host = kwargs['host']
            user = kwargs['user']
            password = kwargs['password']
            database = kwargs['database']
        
        self.cnx = mysql.connect(host=host, user=user, 
                                 password=password, 
                                 database=database)
        self.cursor = self.cnx.cursor(cursor_class=MySQLCursor)
        self._database = database
        self._table = ""
    
    @property
    def table(self) -> str:
        return self._table

    @table.setter
    def table(self, other: str) -> str:
        if not isinstance(other, str):
            raise TypeError("Table name must be a string")
        self._table = other
    
    def is_connected(self):
        return self.cnx.is_connected()
    
    def add_rec(self, table: Optional[str], values: Tuple[str, ...]):
        table = table or self._table
        pass

    def find_rec(self, search: Union[str, int]):
        pass

    def update_rec(self, table: Optional[str], values: Tuple[str, ...]):
        table = table or self._table
        pass

    def delete_rec(self, table: Optional[str], id: int):
        table = table or self._table
        pass

    def close(self):
        self.cnx.close()
                                
class Login:

    def __init__(self):

        self.root = None
        self.main = models.Main

    def set_error(self, entry):
        entry.state(["invalid", '!disabled'])

    def check(self, username: ttk.Entry, password: ttk.Entry):
        loading_screen(self)
        # username.state(["disabled"])
        # password.state(["disabled"])
        # self.main.mysql.cursor.execute("bselect * from login where NAME = %s", (username.get(),))
        # result = self.main.mysql.cursor.fetchall()
        # user_ = username.get()
        # pass_ = password.get()
        # if result:
        #     for name, _pass, admin in result:
        #         if user_ and pass_:
        #             if user_ != name:
        #                 self.set_error(username)
        #             if pass_ != _pass:
        #                 self.set_error(password)
        #             username.bell()
        #             break
        # else:
        #     self.set_error(username)
        #     Message.show_info("Username or Email was not Found in the Database.\nWould you like to Sign Up?",
        #                       yes_no=True, command=self.sign_up)

    def clear(self, *names):
        utils.DefaultEntryText.set_defaults(*names)
    
    def create(self):
        if isinstance(self.root, CTk):
            self.root.destroy()
            self.root = None

        self.root = CTk()
        w, h = 500, 700
        self.root.geometry(f"{w}x{h}")
        self.root.overrideredirect(True)
        utils.center(self.root, w, h)
        utils.load_theme(self.root)

        title_frame = ttk.Frame(self.root, relief='flat')
        close = ttk.Button(title_frame, text="X", command=self.root.destroy)
        close.pack(side='right')
        title_frame.pack(fill='x')

        login_png = utils.get_image('login.png', basic=True, wh=(30, 30))
        close_png = utils.get_image('cross.png', basic=True, wh=(30, 30))

        gif = utils.GIF("assets/basic/medi.gif", self.root) # opening the gif using Image makes the background white
        CTkLabel(image=gif.images[0], height=200, width=200, fg_color=None).pack(pady=10)
        gif.destroy() # remove unwanted label

        title = ttk.Label(self.root, text=self.main.APPNAME, font=DEF_FONT+(30, ))
        title.pack(pady=10)

        frame1 = CTkFrame(self.root, fg_color=CTkColorManager.ENTRY)
        CTkLabel(frame1, text="Username: *", text_font=DEF_FONT+(16, ), 
                 fg_color=None, width=100).grid(row=0, column=0, padx=20)
        username = ttk.Entry(frame1, width=25)
        default = utils.DefaultEntryText.add(username, "Username or Email", 'login.username')
        default.bind()
        username.grid(row=0, column=1, pady=10, padx=20)
        frame1.pack(pady=10)

        frame2 = CTkFrame(self.root, fg_color=CTkColorManager.ENTRY)
        CTkLabel(frame2, text="Password: *", text_font=DEF_FONT+(16, ),
                 fg_color=None, width=100).grid(row=0, column=0, padx=20)
        password = ttk.Entry(frame2, width=25)
        default = utils.DefaultEntryText.add(password, "Example: MyStrongPassword", 
                                             'login.password', 'password')
        default.bind()
        password.grid(row=0, column=1, pady=10, padx=20)
        frame2.pack(pady=10)

        CTkButton(self.root, text="Login", compound="right",
                  command=lambda: self.check(username, password),
                  corner_radius=20, image=login_png, height=40, width=170).place(x=60, y=500)
        
        CTkButton(self.root, text="Clear", compound="right",
                  command=lambda: self.clear(username, password),
                  corner_radius=20, image=close_png, height=40, 
                  width=170, fg_color=models.Color.FRAME).place(x=270, y=500)

        CTkCheckBox(self.root, text="Remember Me", border_width=2).place(x=70, y=600)
        
        self.root.mainloop()

    def sign_up(self):

        def start_move(e):
            self.root.x = e.x
            self.root.y = e.y
        
        def stop_move(e):
            self.root.x = None
            self.root.y = None
        
        def do_move(e):
            dx = e.x - self.root.x
            dy = e.y - self.root.y
            self.root.geometry(f"+{self.root.winfo_x() + dx}+{self.root.winfo_y() + dy}")

        if isinstance(self.root, CTk):
            self.root.destroy()
            self.root = None

        self.root = CTk()
        w, h = 600, 800
        self.root.geometry(f"{w}x{h}")
        self.root.overrideredirect(True)
        utils.center(self.root, w, h)
        utils.load_theme(self.root)

        title_frame = ttk.Frame(self.root, relief='flat')
        close = ttk.Button(title_frame, text="X", command=self.root.destroy)
        ttk.Label(title_frame, text="Sign Up", font=DEF_FONT+(20, )).pack(side='top')
        close.place(relx=0.95)
        values = tuple(title_frame.children.values()) +(title_frame, )
        for widget in values:
            widget.bind('<ButtonPress-1>', start_move)
            widget.bind('<ButtonRelease-1>', stop_move)
            widget.bind('<B1-Motion>', do_move)            
        title_frame.pack(fill='x')

        sign_up = utils.get_image('sign-up.png', basic=True, wh=(30, 30))
        close_png = utils.get_image('cross.png', basic=True, wh=(30, 30))

        gif = utils.GIF("assets/basic/medi.gif", self.root)
        CTkLabel(image=gif.images[0], height=200, width=200, fg_color=None).pack(pady=5)
        gif.destroy()
        title=ttk.Label(self.root, text=self.main.APPNAME, font=DEF_FONT+(30, ))
        title.pack(pady=5)

        container = CTkFrame(self.root, fg_color=None, width=500)
        fields = [('First Name *', 'signup.first_name'), ('Last Name *', 'signup.last_name'),
                  ('Username *', 'signup.username'), ('Email *', 'signup.email'), 
                  ('Date of Birth *', 'signup.dob'), ('Password *', 'signup.password')]
        r = 0
        for label, name in fields:
            frame = CTkFrame(container, fg_color=CTkColorManager.ENTRY)
            if label == 'Date of Birth *':
                utils.dob(frame, label, name, r)
            else:
                CTkLabel(frame, text=label, text_font=DEF_FONT+(16, ),
                        fg_color=None, width=100, justify='right').grid(row=0+r, column=0, padx=20)
                entry = ttk.Entry(frame, width=25)
                default = utils.DefaultEntryText.add(entry, label.strip('*'), name, 
                                                    'password' if label == 'Password' else None)
                default.bind()
                entry.grid(row=0+r, column=1, pady=10, padx=20)
            r += 1
            frame.pack(pady=10)
        tip = CTkLabel(container, text="* Required", text_font=DEF_FONT+(12, ),
                       fg_color=None, width=100, justify='right')
        tip.pack(side='left')
        container.pack()

        sign_up_=CTkButton(self.root, text="Sign Up", compound="right",
                command=lambda: self._sign_up(fields), corner_radius=20, 
                image=sign_up, height=40, width=170)
        sign_up_.place(x=125, y=750)
        
        CTkButton(self.root, text="Clear", compound="right",
                  command=lambda: self.clear(*dict(fields).values()),
                  corner_radius=20, image=close_png, height=40, 
                  width=170, fg_color=models.Color.FRAME).place(x=325, y=750)

        self.root.mainloop()

    def _sign_up(self,fields):

        def try_again():
            self.root.deiconify()
            utils.DefaultEntryText.set_defaults(*dict(fields).values())

        func = utils.DefaultEntryText.get
        data = {k.strip('*'): func(v)[1].entry.get()
                if k != 'Date of Birth *' else func(v)[1] 
                for k, v in fields}
        if not all(data.values()):
            self.root.withdraw()
            Message.show_error("The Following Fields are Empty\n"
                               f"{', '.join(k for k, v in data.items() if not v or v == 'DD/MM/YYYY/Age')}"
                               "\nPlease Fill them and try again", ok_cancel=True, 
                               yes_command=try_again, no_command=self.root.destroy)

        else:
            self.root.withdraw()
            Message.show_info("By Signing up, you Agree to our Terms and Conditions"
                            "of Use and Privacy Policy of {}".format(self.main.APPNAME),
                            yes_command=self.root.destroy, 
                            no_command=self.root.deiconify,
                            yes_no=True)
    
        # if utils.Config.config['app']['save_users']:
        #     key = utils.random_key(5)
        #     token = jwt.encode(data, key, algorithm='HS256')
        #     token = utils.token_encode(token, key)
        #     utils.Config.add_user_config(data['signup.username'], token)
        


        

                
if __name__ == '__main__':
    # Message.create('Error', 'This is an error message, Some Error message filled with message\n', 
    #                yes_no=True, command=lambda: print('Yes'))
    # Login().create()
    # Login().sign_up()
    loading_screen(None)