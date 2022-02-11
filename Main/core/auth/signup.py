from tkinter import ttk

from customtkinter import *

from ..defaultentry import DefaultEntryText
from ..imagetk import *
from ..messagebox import MessageBox
from ..utils import *


__all__ = ('SignUp',)


class SignUp:

    def __init__(self):
        self.root: CTk = None
        self.main = None

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

    def clear(self, fields):
        DefaultEntryText.set_defaults(*dict(fields).values())

    def check(self, fields):

        @run_threaded
        def try_again():
            DefaultEntryText.set_defaults(*dict(fields).values())

        # Data Base check to make sure there arent duplicates as in
        # Name, Email, Username
        # if there are duplicates, then the user will be asked to try again

        # then update the database with the new user
        # run the loading screen to the main window

        if self.main is None:
            raise TypeError("Main is None.")

        func = DefaultEntryText.get
        data = {k.strip('*'): func(v)[1].entry.get()
                if k not in ['Date of Birth *','Gender *'] else func(v)[1] 
                if k != 'Gender *' else v.get()
                for k, v in fields}

        if not all(data.values()):
            MessageBox.warning("ok_cancel", "The Following Fields are Empty\n"
                               f"{', '.join(k for k, v in data.items() if not v or v == 'DD/MM/YYYY/Age')}"
                               "\nPlease Fill them and try again",
                               yes_command=try_again, no_command=self.root.destroy)

        else:
            MessageBox.info("ok_cancel",
                            "By Signing up, you Agree to our Terms and Conditions"
                            "of Use and Privacy Policy of Cadecous Hospital",
                            yes_command=self.root.destroy,  # move on
                            no_command=lambda: None  # return to sign up page
                            )

    def sign_up(self):
        if isinstance(self.root, CTk):
            self.root.destroy()
            self.root = None

        self.root = CTk()

        w, h = 600, 900
        self.root.geometry(f"{w}x{h}")
        self.root.overrideredirect(True)
        center(self.root, w, h)
        load_theme(self.root)
        
        title_frame = ttk.Frame(self.root, relief='flat')
        close = ttk.Button(title_frame, text='X', command=self.root.destroy)
        ttk.Label(title_frame, text="Sign Up",
                  font=DefFont.add(20)).pack(side='top')
        close.place(relx=0.945)
        self._bind_movable_win(*title_frame.children.values(), title_frame)
        title_frame.pack(fill='x')

        sign_up_png = get_image('sign-up.png', basic=True, wh=(30, 30))
        close_png = get_image('cross.png', basic=True, wh=(30, 30))

        gif = GIF("assets/basic/medi.gif", self.root)
        CTkLabel(image=gif.images[0], height=200,
                 width=200, fg_color=None).pack(pady=5)
        gif.destroy()
        title = ttk.Label(self.root, text="Caduceus Hospital",
                          font=DefFont.add(30))
        title.pack(pady=5)

        container = CTkFrame(self.root, fg_color=None, width=500)
        fields = [('First Name *', 'signup.first_name'), ('Last Name *', 'signup.last_name'),
                  ['Gender *', 'signup.gender'], ('Email *', 'signup.email'), 
                  ('Date of Birth *', 'signup.dob'), ('Password *', 'signup.password')]
        
        r = 0
        for label, name in fields:
            frame = CTkFrame(container, fg_color=CTkColorManager.ENTRY)
            if label == 'Date of Birth *':
                dob(frame, label, name, r)
            elif label == 'Gender *':
                CTkLabel(frame, text=label, text_font=DefFont.add(16),
                         fg_color=None, width=170, justify='right').grid(row=0+r, column=0, padx=20)
                gen = gender(frame, r, fg=frame["bg"])
                fields[2][1] = gen
            else:
                CTkLabel(frame, text=label, text_font=DefFont.add(16),
                         fg_color=None, width=170, justify='right').grid(row=0+r, column=0, padx=20)
                entry = ttk.Entry(frame, width=25)
                default = DefaultEntryText.add(entry, label.strip('*'), name,
                                               'password' if label == 'Password *' else None)
                default.bind()
                entry.grid(row=0+r, column=1, pady=10, padx=20)

            r += 1
            frame.pack(pady=10)
        tip = CTkLabel(container, text="* Required", text_font=DefFont.add(12),
                       fg_color=None, width=100, justify='right')
        tip.pack(side='left')
        container.pack()

        sign_up_ = CTkButton(self.root, text="Sign Up", compound="right",
                             command=lambda: self.check(fields), corner_radius=15,
                             image=sign_up_png, height=40, width=170)
        sign_up_.place(x=125, y=800)

        CTkButton(self.root, text="Clear", compound="right",
                  command=lambda: self.clear(fields),
                  corner_radius=15, image=close_png, height=40,
                  width=170, fg_color=Color.FRAME).place(x=325, y=800)
                  
        self.root.config(fg_color=tip['bg'])
        self.root.mainloop()




