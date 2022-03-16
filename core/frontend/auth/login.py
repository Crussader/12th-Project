from tkinter import ttk

from customtkinter import *

from core.backend.models import *
from core.backend.imagetk import get_image, GIF
from core.backend.utils import ThreadPool
from ..defaultentry import DefaultEntryText
from ..messagebox import MessageBox
from ..utils import Color, center, load_theme, Defont, fade_in_out

__all__ = ('Login',)


class Login:

    def __init__(self):

        self.root = None
        self.app = None

    def _bind_movable_win(self, *values):

        def start_move(e):
            self.root.x = e.x
            self.root.y = e.y

        def stop_move(e):
            self.root.x = None
            self.root.y = None

        def do_move(e):
            dx = e.x - self.root.x
            dy = e.y - self.root.y
            self.root.geometry(
                f"+{self.root.winfo_x() + dx}+{self.root.winfo_y() + dy}")
        for widget in values:
            widget.bind("<ButtonPress-1>", start_move)
            widget.bind("<ButtonRelease-1>", stop_move)
            widget.bind("<B1-Motion>", do_move)

    def set_invalid(self, entry: ttk.Entry):
        entry.state(["invalid", "!disabled"])
        entry.bell()

    def check(self, email: ttk.Entry, password: ttk.Entry):

        def _signup(signup):
            fade_in_out(self.root, signup, signup.sign_up)

        email.state(["disabled"])
        password.state(["disabled"])

        entry_email = email.get()
        entry_pass = password.get()

        
        t = self.app.db.find_rec(entry_email, filter_by='EMAIL', table='users')
        result = ThreadPool.wait_result(t)
        
        if not result.is_empty:
            user: User = result.one()
            if user.email == entry_email and user.password == entry_pass:
                from ..panels._user import UserPanel
                from ..panels._doctor import DoctorPanel
                from ..panels._admin import AdminPanel
                panels = {
                    1: UserPanel,
                    2: DoctorPanel,
                    3: AdminPanel
                }
                self.app.user = user
                self.app = self.app(panels.get(user.level))
                fade_in_out(self.root, self.app, self.app.load_window)

            if user.password != entry_pass:
                self.set_invalid(password)
        
        else:
            from .signup import SignUp
            signup = SignUp()
            signup.app = self.app
            signup.login = self

            self.set_invalid(email)
            MessageBox.info('ok_cancel', ("Email was not Found in the Database."
                            "\nWould you like to Sign Up?"), yes_command=lambda: _signup(signup),
                            no_command=self.root.destroy)


    def clear(self, *names):
        DefaultEntryText.set_defaults(*names)

    def login(self):
        self.root = CTk()
        w, h = 500, 700
        self.root.geometry(f"{w}x{h}")
        self.root.overrideredirect(True)
        self.root.attributes('-topmost', True)

        center(self.root, w, h)
        load_theme(self.root)

        title_frame = ttk.Frame(self.root, relief='flat')
        close = ttk.Button(title_frame, text="X", command=self.root.destroy)
        close.pack(side='right')
        title_frame.pack(fill='x')
        self._bind_movable_win(*title_frame.winfo_children(), title_frame)

        login_png = get_image('login.png', basic=True, wh=(30, 30))
        close_png = get_image('cross.png', basic=True, wh=(30, 30))

        gif = GIF("assets/basic/medi.gif", self.root) # opening the gif using Image makes the background white
        im = CTkLabel(image=gif.images[0], height=200, width=200, fg_color=None, text='')
        im.pack(pady=10)
        gif.destroy() # remove unwanted label
        
        title = ttk.Label(self.root, text="Caduceus Hospital", 
                          font=Defont.add(30), background=self.root.fg_color[AppearanceModeTracker.appearance_mode])
        title.pack(pady=10)

        frame1 = CTkFrame(self.root, fg_color=Color.ENTRY_COLOR)
        CTkLabel(frame1, text="Email: *", text_font=Defont.add(16), 
                 fg_color=None, width=100).grid(row=0, column=0, padx=20)
        username = ttk.Entry(frame1, width=25)
        default = DefaultEntryText.add(username, "Email", 'login.email')
        default.bind()
        username.grid(row=0, column=1, pady=10, padx=20)
        frame1.pack(pady=10)

        frame2 = CTkFrame(self.root, fg_color=Color.ENTRY_COLOR)
        CTkLabel(frame2, text="Password: *", text_font=Defont.add(16),
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
                  width=170, fg_color=Color.FRAME_COLOR).place(x=270, y=500)

        CTkCheckBox(self.root, text="Remember Me", border_width=2).place(x=70, y=600)
        
        self.root.apploop()
