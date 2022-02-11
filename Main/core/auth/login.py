from tkinter import ttk

from customtkinter import *

from ..database import Database
from ..defaultentry import DefaultEntryText
from ..imagetk import *
from ..messagebox import MessageBox
from ..models import User
from ..utils import *

__all__ = ('Login',)


class Login:

    def __init__(self):

        self.root = None
        self.main = None

    def set_invalid(self, entry: ttk.Entry):
        entry.state(["invalid", "!disabled"])
        entry.bell()

    def check(self, email: ttk.Entry, password: ttk.Entry):

        email.state(["disabled"])
        password.state(["disabled"])

        entry_email = email.get()
        entry_pass = password.get()

        db = Database.from_config()
        result = db.find_rec(entry_email, filter_by="EMAIL", table='users')
        if not result.is_empty:
            # check the first one because there can always be only one email
            user: User = result.one()
            if user.email != entry_email:
                self.set_invalid(email)
            if user.password != entry_pass:
                self.set_invalid(password)

        else:
            self.set_invalid(email)
            MessageBox.info('ok_cancel', ("Email was not Found in the Database."
                            "\nWould you like to Sign Up?"))

    def clear(self, *names):
        DefaultEntryText.set_defaults(*names)

    def login(self):
        if isinstance(self.root, CTk):
            self.root.destroy()
            self.root = None

        self.root = CTk()
        w, h = 500, 700
        self.root.geometry(f"{w}x{h}")
        self.root.overrideredirect(True)
        center(self.root, w, h)
        load_theme(self.root)

        title_frame = ttk.Frame(self.root, relief='flat')
        close = ttk.Button(title_frame, text="X", command=self.root.destroy)
        close.pack(side='right')
        title_frame.pack(fill='x')

        login_png = get_image('login.png', basic=True, wh=(30, 30))
        close_png = get_image('cross.png', basic=True, wh=(30, 30))

        gif = GIF("assets/basic/medi.gif", self.root) # opening the gif using Image makes the background white
        CTkLabel(image=gif.images[0], height=200, width=200, fg_color=None).pack(pady=10)
        gif.destroy() # remove unwanted label

        title = ttk.Label(self.root, text="", font=DEF_FONT+(30, ))
        title.pack(pady=10)

        frame1 = CTkFrame(self.root, fg_color=Color.ENTRY)
        CTkLabel(frame1, text="Username: *", text_font=DEF_FONT+(16, ), 
                 fg_color=None, width=100).grid(row=0, column=0, padx=20)
        username = ttk.Entry(frame1, width=25)
        default = DefaultEntryText.add(username, "Username or Email", 'login.username')
        default.bind()
        username.grid(row=0, column=1, pady=10, padx=20)
        frame1.pack(pady=10)

        frame2 = CTkFrame(self.root, fg_color=Color.ENTRY)
        CTkLabel(frame2, text="Password: *", text_font=DEF_FONT+(16, ),
                 fg_color=None, width=100).grid(row=0, column=0, padx=20)
        password = ttk.Entry(frame2, width=25)
        default = DefaultEntryText.add(password, "Example: MyStrongPassword", 
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
