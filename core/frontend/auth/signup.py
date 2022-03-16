from tkinter import ttk
from typing import Dict, Any

from customtkinter import *

from core.backend.imagetk import *
from core.backend.utils import ThreadPool, rand_id, token_encode
from core.backend.models import *
from ..defaultentry import DefaultEntryText
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

    def clear(self):
        DefaultEntryText.set_defaults(*DefaultEntryText.load_all_base('signup'))
    
    def _continue(self, data: Dict[str, Any]):
        # {'First Name ': 'Parikshit', 'Last Name ': 'Rao', 
        #  'Gender ': 1, 'Email ': 'parikshit@gmail.com', 
        #  'Date of Birth ': '05/06/2004/17', 'Password ': 'abc'}

        data = {k[:-1].replace(' ', "_").lower(): v 
                for k, v in data.items()}

        
        age = data.pop('date_of_birth')
        d, m, y, _ = age.split('/')
        # data['dob'] = '%s-%s-%s' % (y, m ,d)
        data['dob'] = f"{y}-{m}-{d}"
        paitent_data = {**data}
        paitent_data['id'] = rand_id()
        del paitent_data['password']
        del paitent_data['email']

        data['_password'] = token_encode({'key': data.pop('password')})
        data['name'] = ' '.join([data.pop('first_name'), data.pop('last_name')])
        data['level'] = 1 # default level for new users
        data['id'] = rand_id()

        paitent_data['user_id'] = data['id']
        data['paitent_id'] = paitent_data['id']
        
        user = self.main.db.add_rec('users', data)
        paitent = self.main.db.add_rec('paitents', paitent_data)
        if user and paitent: 
            from ..panels._user import UserPanel
            from ..panels._doctor import DoctorPanel
            from ..panels._admin import AdminPanel
            panels = {
                1: UserPanel,
                2: DoctorPanel,
                3: AdminPanel
            }
            t = self.main.db.find_rec(data['id'], "ID", table='users')
            user: User = ThreadPool.wait_result(t).one()
            self.main.user = user
            self.main = self.main(panels.get(user.level))
            fade_in_out(self.root, self.main, self.main.load_window)
        else:
            MessageBox.error('ok_cancel', 'Oh no, Something went Wrong! Please Try Again Later!',
                             yes_command=self.root.quit, no_command=self.root.quit) # something went wrong so prolly no point in going ahead
        

    def check(self, fields):

        def _login():
            self.root.destroy()
            self.root = None
            self.login.login()

        # Data Base check to make sure there arent duplicates as in Email
        # if there are duplicates, then the user will be asked to try again

        # then update the database with the new user
        # run the loading screen to the main window


        func = DefaultEntryText.get
        data = {k.strip('*'): func(v)[1].get_text()
                if k not in ['Date of Birth *','Gender *'] else func(v)[1] 
                if k != 'Gender *' else v.get()
                for k, v in fields}

        duplicate = self.main.db.check_duplicates('email', data['Email '], 'users')
        if duplicate:
            MessageBox.warning('ok_cancel', 'The Email already Exists in the Database, Are you sure it is the Correct Email?, Would you Like to Login Instead?',
                               yes_command=_login, no_command=self.root.quit)

        if not all(data.values()):
            MessageBox.warning("ok_cancel", "The Following Fields are Empty\n"
                               f"{', '.join(k for k, v in data.items() if not v or v == 'DD/MM/YYYY/Age')}"
                               "\nPlease Fill them and try again", no_command=self.root.destroy)

        else:
            MessageBox.info("ok_cancel",
                            "By Signing up, you Agree to our Terms and Conditions"
                            "of Use and Privacy Policy of Cadecous Hospital",
                            yes_command=lambda: self._continue(data),  # move on
                            no_command=lambda: None  # return to sign up page
                            )

    def sign_up(self):
        if isinstance(self.root, CTk):
            self.root.destroy()
            self.root = None

        self.root = CTk(fg_color=Color.ENTRY_COLOR)

        w, h = 600, 900
        self.root.geometry(f"{w}x{h}")
        self.root.attributes('-topmost', True)
        self.root.overrideredirect(True)
        center(self.root, w, h)
        load_theme(self.root)
        
        title_frame = ttk.Frame(self.root, relief='flat')
        close = ttk.Button(title_frame, text='X', command=self.root.destroy)
        ttk.Label(title_frame, text="Sign Up",
                  font=Defont.add(20)).pack(side='top')
        close.place(relx=0.945)
        self._bind_movable_win(*title_frame.children.values(), title_frame)
        title_frame.pack(fill='x')

        sign_up_png = get_image('sign-up.png', basic=True, wh=(30, 30))
        close_png = get_image('cross.png', basic=True, wh=(30, 30))

        gif = GIF("assets/basic/medi.gif", self.root)
        CTkLabel(image=gif.images[0], height=200,
                 width=200, fg_color=self.root.fg_color).pack(pady=5)
        gif.destroy()
        title = ttk.Label(self.root, text="Caduceus Hospital",
                          font=Defont.add(30))
        title.pack(pady=5)

        container = CTkFrame(self.root, fg_color=self.root.fg_color, width=500)
        fields = [('First Name *', 'signup.first_name'), ('Last Name *', 'signup.last_name'),
                  ['Gender *', 'signup.gender'], ('Email *', 'signup.email'), 
                  ('Date of Birth *', 'signup.dob'), ('Password *', 'signup.password')]
        
        r = 0
        for label, name in fields:
            frame = CTkFrame(container, fg_color=Color.ENTRY_COLOR)
            if label == 'Date of Birth *':
                dob(frame, label, name, r)
            elif label == 'Gender *':
                CTkLabel(frame, text=label, text_font=Defont.add(16),
                         fg_color=frame.fg_color, width=170, justify='right').grid(row=0+r, column=0, padx=20)
                gen = gender(frame, r, fg=frame["bg"])
                fields[2][1] = gen
            else:
                CTkLabel(frame, text=label, text_font=Defont.add(16),
                         fg_color=None, width=170, justify='right').grid(row=0+r, column=0, padx=20)
                entry = ttk.Entry(frame, width=25)
                default = DefaultEntryText.add(entry, label.strip('*'), name,
                                               'password' if label == 'Password *' else None)
                default.bind()
                entry.grid(row=0+r, column=1, pady=10, padx=20)

            r += 1
            frame.pack(pady=10)
        tip = CTkLabel(container, text="* Required", text_font=Defont.add(12),
                       fg_color=frame.fg_color, width=100, justify='right')
        tip.pack(side='left')
        container.pack()

        sign_up_ = CTkButton(self.root, text="Sign Up", compound="right",
                             command=lambda: self.check(fields), corner_radius=15,
                             image=sign_up_png, height=40, width=170)
        sign_up_.place(x=125, y=800)

        CTkButton(self.root, text="Clear", compound="right",
                  command=self.clear, corner_radius=15, image=close_png, 
                  height=40, width=170, fg_color=Color.FRAME_COLOR).place(x=325, y=800)
                  
        self.root.config(fg_color=tip['bg'])
        self.root.mainloop()