from itertools import cycle
from tkinter import IntVar, ttk, Text, Toplevel
from typing import List

from customtkinter import *

from ...backend import Database, get_image
from ...backend.models import *
from ...backend.models import Staff
from ...backend.utils import Color, Defont, ThreadPool, chunk, get_age
from ..defaultentry import DefaultEntryText
from ..messagebox import MessageBox
from ..utils import dob, center
from .base import Panel, transition

__all__ = ('UserPanel',) 

class _AddUser:

    temp = {}

    def __init__(self, panel: 'UserPanel'):
        self.panel = panel
        self.main = self.panel.main

    def _parse_entries(self, data):
        data = {k.lower().replace(' ', '_'): v 
               for k, v in data.items()}

        _pass, re_pass = data.pop('password'), data.pop('re-enter_password')
        
        if _pass != re_pass: # and (_pass and re_pass):
            MessageBox.warning('ok_cancel', 'The Two Passwords Entered do not Match!')
            return

        del data['age'] # no need of age
        y, m, d = [data.pop(i) for i in ('yyyy', 'mm', 'dd')]
        data['dob'] = '%s-%s-%s' % (y, m ,d)
        data['_password'] = _pass
        data['name'] = ' '.join([data.pop('first_name'), data.pop('last_name')])
        return data

    def _clear_entries(self):
        DefaultEntryText.set_defaults(*DefaultEntryText.load_all_base('add'))
    
    def _submit(self):
        agree = self.temp.get('check')
        if agree and agree.get() == 0:
            msg = f"You can not Procceed without Agreeing to the terms and Conditions of {self.main.APPNAME}"
            MessageBox.warning('ok_cancel', msg)
            return

        entries = DefaultEntryText.load_all_base('add')

        empty = ', '.join(e.text for e in entries if not e.get_text() and 
                          e.text not in ['Paitent ID', 'Relation'])

        if empty:
            msg = f"You Have missed the following fields\n{empty}"
            MessageBox.warning('ok_cancel', msg)
        else:
            data = {e.text[:-1] if e.text[-1].isspace() 
                    else e.text: e.get_text() for e in entries}
            data['gender'] = self.temp.pop('gender').get()        
            data = self._parse_entries(data)

            db = Database.from_config()
            db.add_rec('users', data)

    def _load_entires(self, frame: CTkFrame):

        # def check(_):
        #     (_, password), (_, re_enter) = DefaultEntryText.get('add.Password_'), DefaultEntryText.get('add.Re-Enter_Password_')
        #     error = CTkLabel(frame, fg_color=None, text='',
        #                      text_color='red', text_font='Montserrat')
        #     error.grid(row=r, column=2, padx=20)
        #     if password.text != password.entry.get() and re_enter.text != re_enter.entry.get():
        #         print(password.entry.get(), re_enter.entry.get(), re_enter.text)
        #         if password.entry.get() != re_enter.entry.get():
        #             error.set_text('Passwords do not Match.')
        #         else:
        #             error.set_text('Password Match.')
        #             error.configure(text_color='green')

        fields = ('First Name *', 'Last Name *', 'Gender *', 'Email *', 'dob *',
                  'Paitent ID', 'Link', 'Password *', 'Re-Enter Password *')
        r = 4

        for field in fields:
            inner = CTkFrame(frame, fg_color=Color.ENTRY_COLOR)

            width = (200 if field in ['Re-Enter Password *', 'Link'] else
                     70 if field == 'Email *' else 120)

            if field != 'dob *':
                label = CTkLabel(inner, text=field.strip('*'), fg_color=None, width=width,
                                 text_font=Defont.add(16, font='Montserrat'))
                if field == 'Link':
                    label.text_label.grid_configure(sticky='nw')
                label.grid(row=0, pady=5, padx=20, sticky='nw')

            if '*' in field:
                req = CTkLabel(inner, text='*', text_font=Defont.add(20),
                               fg_color=None, text_color='red', width=10)
                req.grid(row=0, column=0, sticky='nw', padx=5, pady=5)

            if field == 'Gender *':
                gender = IntVar()
                self.temp["gender"] = gender 
                male = CTkCheckBox(inner, text='Male', corner_radius=10,
                                   border_width=1, variable=gender, offvalue=2)
                male.grid(row=2, column=0, sticky='nw', pady=15, padx=10)

                female = CTkCheckBox(inner, text='Female', corner_radius=10,
                                     border_width=1, onvalue=2, offvalue=1)
                female.grid(row=2, column=0, pady=15, padx=90)

                other = CTkCheckBox(inner, text='Other', corner_radius=10,
                                    border_width=1, variable=gender, onvalue=3)
                other.grid(row=2, column=0, pady=15, padx=5, sticky='e')

            if field == 'dob *':
                a, fr = dob(inner, 'Date of Birth', 'add.dob', r)
                a.grid_configure(row=0, sticky='nw', padx=15, pady=10)
                fr.grid_configure(row=1)

            elif field != 'Gender *':
                entry = ttk.Entry(inner, font='Montserrat',
                                  width=30 if field == 'Email *' or field == 'Re-Enter Password' else 20)

                DefaultEntryText.add(entry, field.strip('*'), mode='password' if 'Pass' in field else '',
                                     name='add.%s' % (field.strip('*').replace(' ', '_'))
                                     ).bind()
                entry.grid(row=1, column=0, pady=10, padx=10, sticky='nw')

            inner.grid(row=r, column=0, padx=10, pady=40 if r == 4 
                       or r == 5 else 10, sticky='nw')

            if 'Pass' in field:
                entry.grid_configure(ipadx=40, pady=10)

            if 'Last Name *' == field or 'Re-Enter Password *' == field:
                inner.grid_configure(
                    row=r-1, padx=370 if "Re" in field else 290, sticky='nw')
            elif field == 'Email *':
                inner.grid_configure(columnspan=1)
            elif field == 'dob *':
                inner.grid_configure(row=r-1, column=0, padx=420)
                req.grid_configure(padx=0)
            elif field == 'Link':
                label.configure(width=22, text="Link ID (Link to another User)")
                entry.configure(width=22)
                inner.grid_configure(row=r-1, column=0, padx=300)
            elif field == 'Gender *':
                inner.grid_configure(row=r-2, column=0, padx=570, pady=40)

            r += 1

    def _load_right_side(self, frame: CTkFrame):
        def _expand(img):
            """Expand a Button a little when on hover"""
            def inner(_):
                frame.after(50)
                img.configure(scale=0.14)

            return inner

        def _shrink(img):
            def inner(_):
                frame.after(50)
                img.configure(scale=0.12)

            return inner

        CTkFrame(frame, width=5).place(relx=0.5, rely=0.4, relheight=0.5)

        two = IntVar()
        check = IntVar()

        self.temp['two_step'] = two
        self.temp['check'] = check

        two_step = CTkCheckBox(frame, text='Enable Two-step Verification',
                               corner_radius=10, border_width=1)
        two_step.place(relx=0.53, rely=0.35)

        info = "Enabling Two-step Verification will allow a \nSafer way of accessing the account"
        CTkLabel(frame, text=info, width=300, height=40,
                 fg_color=None, text_color=Color.LABEL_BG_COLOR).place(relx=0.53, rely=0.39)

        submit_img = get_image('submit.svg', wh=0.12)
        submit = CTkButton(frame, image=submit_img, text='',
                           fg_color=frame.fg_color, width=100,
                           cursor='hand2', compound='left',
                           command=self._submit)
        submit.bind('<Enter>', _expand(submit_img))
        submit.bind('<Leave>', _shrink(submit_img))
        submit.place(relx=0.53, rely=0.55)

        clear_img = get_image('erase.svg', wh=0.12)
        clear = CTkButton(frame, image=clear_img, text='',
                          fg_color=frame.fg_color, width=100,
                          cursor='hand2', compound='left',
                          command=self._clear_entries)
        clear.bind('<Enter>', _expand(clear_img))
        clear.bind('<Leave>', _shrink(clear_img))
        clear.place(relx=0.6, rely=0.55)

        agree = CTkCheckBox(frame, text=f'You Agreed with the terms and Conditions of {self.main.APPNAME}',
                            text_font=Defont.add(12), border_width=1, corner_radius=10, variable=check)
        agree.place(relx=0.53, rely=0.48)

    @transition
    def add_user(self):
        main: CTkFrame = self.main.frames['main']
        a = CTkButton(main, text_font=Defont.add(30, font='Montserrat'), height=50,
                      width=200, text="New User", fg_color=main.fg_color, hover=False,
                      image=get_image('add-user.svg', wh=0.3), compound='left')
        a.grid(row=0, column=0, padx=10, pady=10, sticky='nw')

        about = "Add a User Linked With You, Or Add Multiple Users at Once From a File."
        CTkLabel(main, text_font=Defont.add(11), height=50,
                 width=600, text=about, fg_color=main.fg_color).grid(row=2, column=0, padx=10, sticky='nw')

        CTkFrame(main, height=5).grid(row=3, column=0, columnspan=2,
                                      padx=20, pady=10, sticky='ew')
        main.grid_columnconfigure(1, weight=1)

        main.after(700, self._load_entires, main)
        main.after(700, self._load_right_side, main)

class _Users:

    _all_users = {}

    def __init__(self, panel: 'UserPanel'):
        self.panel = panel
        self.main = panel.main

    def _get_connected_users(self) -> List[User]:
        user: UserType = self.main.user

        if user.linked:
            a = self.main.db.find_rec(1, filter_by='LINKED_ID', 
                                       table='users') # running threaded
            users = ThreadPool.wait_result(a).all() 
            # find records where the linked user ids
        else:
            users = []

        return users

    def _remove(self, user: User):

        def _yes():
            db: Database = self.main.db
            db.update_rec(1, table='users', kwargs={'linked_id': None})
            self._all_users[user.id].destroy()

        MessageBox.warning('yes_no', 'Are you Sure you want to Unlink this User from you?',
                           yes_command=_yes)

    def _edit(self, user: User):
        pass
        
        ### Editable Entry ### NOTE
        # fr = EditableEntry(main, header='Name: ', text=user.name.title()) # will think later
        
    def _create_frame(self, frame: CTkFrame, user: User, r: int, c: int):
        fr = CTkFrame(frame, fg_color=Color.FRAME_2_COLOR, corner_radius=30, cursor='hand2')
        dp = get_image('user.svg', wh=0.2)
        display = CTkLabel(fr, image=dp, height=120, 
                           fg_color=None)
        display.image = dp
        display.pack(padx=10, pady=10, side='left')

        name = CTkLabel(fr, text=user.name.title(), height=30,
                        text_font=Defont.add(15), fg_color=None)
        # name.pack(anchor='w', padx=10, pady=10)
        name.place(relx=0.2, rely=0.25)
        age = CTkLabel(fr, text=f"Age: {get_age(user.dob)}", fg_color=None,
                       text_color='darkgrey', text_font=Defont.add(10), width=50)
        age.place(relx=0.2, rely=0.5)

        CTkLabel(fr, text=f'User ID: {user.id}', fg_color=None, width=180).place(relx=0.27, rely=0.5)
        
        CTkLabel(fr, text=f'Paitent ID: {user.paitent.id}', fg_color=None, width=200).place(relx=0.5, rely=0.5)
        
        edit = CTkButton(fr, text='Edit', hover_color=Color.LABEL_BG_COLOR,
                         fg_color=Color.FRAME_COLOR, corner_radius=20,
                         command=lambda: self.load_individual(user, edit=True))
        edit.place(relx=0.8, rely=0.25)

        remove = CTkButton(fr, text='Remove', hover_color='#e96664',
                           fg_color='#d02f27', corner_radius=20,
                           command=lambda: self._remove(user))

        remove.place(relx=0.8, rely=0.55)

        fr.bind('<Button-1>', lambda _: self.load_individual(user))
        for w in fr.winfo_children():
            if not isinstance(w, CTkButton):
                w.bind('<Button-1>', lambda _: self.load_individual(user))

        fr.grid(row=r, column=c, padx=20, pady=30,
                stick='nw' if c == 0 else 'ne', ipadx=300)

        self._all_users[user.id] = fr

    def _load_users(self, main: CTkFrame, total):
        
        users = self._get_connected_users()

        # self.main.user.id = 12872382832123
        # self.main.user.paitent.id = 12872382832123
        # self._create_frames(main, self.main.user, 4, 0)
        total.set_text(f'Total Users: {len(users)}')

        if not users:
            im = get_image('not-found.svg', wh=0.4)
            a = CTkButton(main, fg_color=Color.FRAME_COLOR, hover=False,
                         image=im, text='No Users Connected with you :(', 
                         height=300, width=300, compound='top',
                         text_color='grey')
            a.place(relx=0.4, rely=0.4)
        else:
            # i should put a limit to how many users can be connected
            row=4
            column = 0
            for _users in chunk(users, len(users)//2):
                for user in _users:
                    main.after(100, self._create_frame, main, user, row, column)
                    row += 1
                column += 1

    def users(self):
        main: CTkFrame = self.main.frames['main']

        top = CTkButton(main, text_font=Defont.add(30), height=50,
                        width=200, text = 'All Users', fg_color=main.fg_color, hover=False,
                        image=get_image('users.svg', wh=0.3), compound='left')
        top.grid(row=0, column=0, padx=10, pady=10, sticky='nw')

        total = CTkLabel(main, text='Total Users: -', text_font=Defont.add(25),
                         height=50, width=310, fg_color=main.fg_color)
        total.grid(row=0, column=1, padx=10, pady=40, sticky='ne')

        about = 'Check all the users Linked with You, along with Yourself.'
        CTkLabel(main, text_font=Defont.add(11), height=50,
                 width=600, text=about, fg_color=main.fg_color).grid(row=2, column=0, padx=10, sticky='nw')
        CTkFrame(main, height=5).grid(row=3, column=0, columnspan=2,
                                      padx=20, pady=10, sticky='ew')
        
        main.grid_columnconfigure(1, weight=1)
        main.after(1100, self._load_users, main, total)

    @transition
    def load_individual(self, user: User, edit=False):

        main: CTkFrame = self.main.frames['main']
        dp = get_image('user.svg', wh=0.3)
        top = CTkButton(main, text_font=Defont.add(30), height=50, hover=False,
                        width=200, text=user.name.title(), fg_color=Color.FRAME_COLOR,
                        image=dp, compound='left')
        top.grid(row=0, column=0, padx=10, pady=10, sticky='nw')
        

        info = f"User ID: {user.id} \t Paitent ID: {user.paitent.id}"
        CTkLabel(main, text_font=Defont.add(11, font='Avenir'), height=50,
                 width=600, text=info, fg_color=Color.FRAME_COLOR).grid(row=2, column=0, padx=10, sticky='nw')
        
        back = CTkButton(main, fg_color=Color.FRAME_COLOR, hover=False, height=30,
                         command=self.users, text='', image=get_image('back.svg', wh=0.1),
                         width=50, compound='left', cursor='hand2')
        back.place(relx=0.023, rely=0.2)

        CTkFrame(main, height=5).grid(row=3, column=0, columnspan=2,
                                      padx=20, pady=10, sticky='ew')

        main.grid_columnconfigure(1, weight=1)

        def _load():
            if edit:
                self._edit(user)
            else:
                attrs = {k: getattr(user, k) for k in user.__slots__}
                r = 4
                column = cycle([0, 1])
                for k, v in attrs.items():
                    if k == 'level':
                        continue # no need of showing levels and all

                    c = next(column)
                    inner = CTkFrame(main)

                    if '_' in k:
                        text = k[1:].capitalize()
                    else:
                        text = k.capitalize() if k != 'id' else k.upper()
                    
                    if isinstance(v, (User, Paitent)) and v:
                        text = f"{text} ID"
                        value = v.id
                    elif k == '_gender':
                        value = user.gender
                    elif k == 'dob':
                        text = k.upper()
                        value = '   Age: '.join([str(v), str(get_age(v))])
                    else:
                        value = str(v)
                    
                    text = f"{text}:"
                    l = CTkLabel(inner, text=text, text_font=Defont.add(15), 
                            fg_color=None, height=40, width=150)
                    l.text_label.place_configure(relx=0.1, anchor='w')
                    # l.text_label.configure(justify='left')
                    l.pack(pady=5, padx=5, side='left')

                    val = CTkLabel(inner, text=value, text_font=Defont.add(15),
                                fg_color=None, height=40, width=300)
                    val.text_label.place_configure(relx=0.1, anchor='w')
                    val.pack(pady=5, padx=5, side='right')
                    inner.grid(row=r if c == 0 else r-1, column=c, 
                               padx=10, sticky='nw', pady=10)
                    r += 1
            
        main.after_idle(_load)

class _DoctorUpdates:

    def __init__(self, panel: 'UserPanel'):
        self.panel = panel
        self.main = panel.main
        self.db: Database = self.main.db

    
    def _shorten(self, text: str, at: int=30):
        return text[:at] + '....'

    def _reply(self, main: CTkFrame, update: Update, _from: Staff, _to: PaitentType):

        def _update():
            reply_text = text.get(1.0, 'end')
            done = self.db.update_user(_to.id, _from.id, reply_text)
            if done:
                top.destroy()
                self.doctor_updates()                

        top = Toplevel()
        top.attributes('-topmost', True)
        top.title(self.main.APPNAME)
        w, h = 600, 600
        top.geometry(f"{w}x{h}")
        top.resizable(None, None)
        center(top, w, h)

        from_label = CTkLabel(top, text=f'From: \tDr. {_to.name.title()}', height=30, 
                              text_font=Defont.add(13), fg_color=None, justify='left')
        from_label.pack(anchor='nw', padx=10, pady=10)

        ttk.Separator(top).pack(fill='x', padx=10)

        to_label = CTkLabel(top, text=f'To: \t{_from.name.title()}', height=30,
                            text_font=Defont.add(13), fg_color=None, justify='left')
        to_label.pack(anchor='nw', padx=10, pady=10)

        ttk.Separator(top).pack(fill='x', padx=10)

        replying_to = CTkLabel(top, text=f'Replying to:\n{self._shorten(update.text, 10)}',
                               text_font=Defont.add(13), fg_color=None, justify='left')
        replying_to.pack(anchor='nw', padx=10, pady=10)

        ttk.Separator(top).pack(fill='x', padx=10)

        text = Text(top, font=Defont.add(12), height=50, relief='flat')
        text.focus()
        text.pack(anchor='nw', padx=10, pady=10)

        reply = CTkButton(top, image=get_image('send.svg', wh=0.05), cursor='hand2',
                          fg_color=None, text='', width=50, corner_radius=20, 
                          hover_color=Color.FRAME_COLOR, height=35,
                          command=_update)
        reply.place(relx=0.87, rely=0.01)

        main.after(500, top.mainloop)

    @transition
    def _show_update(self, update: Update, _from: Staff, _to: PaitentType):
        main: CTkFrame = self.main.frames['main']

        def load():
            dp = get_image('user.svg', wh=0.3)
            top=CTkButton(main, text='', height=50, hover=False,
                        width=200, fg_color=main.fg_color,
                        image=dp)
            top.grid(row=0, column=0, padx=10, pady=10, sticky='nw')

            CTkFrame(main, width=5, height=150).grid(row=0, column=1, padx=5)

            from_label = CTkLabel(main, text=f"From: \tDr. {_from.name.title()}", corner_radius=20,
                                height=40, text_font=Defont.add(15), fg_color=None)
            from_label.text_label.grid_configure(sticky='w')
            from_label.grid(row=0, column=2, sticky='nw', pady=30)

            to_label = CTkLabel(main, text=f"To: \t{_to.name.title()}",
                                height=40, text_font=Defont.add(15), fg_color=None)
            to_label.text_label.grid_configure(sticky='w')
            to_label.grid(row=0, column=2, sticky='nw', pady=60, padx=15)

            _update = CTkLabel(main, text=update.text, width=300, height=100, 
                            fg_color=main.fg_color, justify='left',
                            text_font=Defont.add(13))
            _update.text_label.grid_configure(sticky='w')
            # _update.grid(row=1, column=1, sticky='nw', pady=30, padx=20)
            _update.place(relx=0.01, rely=0.3)
        
            reply = CTkButton(main, text='Reply', text_font=Defont.add(12),
                            command=lambda: self._reply(main, update, _from, _to))
            reply.place(relx=0.15, rely=0.15)

            back = CTkButton(main, fg_color=main.fg_color, hover=False, height=30,
                         command=self.doctor_updates, text='', image=get_image('back.svg', wh=0.1),
                         width=50, compound='left', cursor='hand2')
            back.place(relx=0.023, rely=0.2)

        main.after(200, load)
        # reply.grid(row=0, column=2, sticky='nw', pady=120, padx=15)

    def _create_frame(self, frame: CTkFrame, update: Update, r: int, c: int):
        update_frame = CTkFrame(frame, fg_color=Color.FRAME_COLOR, corner_radius=30, cursor='hand2')
        dp = get_image('user.svg', wh=0.2)
        display = CTkLabel(update_frame, image=dp,
                           height=120)
        display.image=dp
        display.pack(side='left', padx=10, pady=10)

        t = self.db.find_rec(update.from_id, 'ID', table='doctor')
        from_user: Doctor = ThreadPool.wait_result(t).one()

        _from = CTkLabel(update_frame, text='Dr. '+from_user.name.title(), 
                         height=30, text_font=Defont.add(15), fg_color=None, 
                         cursor='arrow')
        _from.place(relx=0.2, rely=0.25)
    
        t = self.db.find_rec(update.to_id, 'ID', table='paitents') # because the person is a paitent not a user
        to_paitent: Paitent = ThreadPool.wait_result(t).one()

        to =CTkLabel(update_frame, text=f"To: {to_paitent.name.title()}", fg_color=None,
                 width=180, text_font=Defont.add(10), cursor='arrow')
        to.text_label.grid_configure(sticky='w')
        to.place(relx=0.2, rely=0.5)

        CTkLabel(update_frame, text=f"System: {bool(update.is_system)}", fg_color=None,
                 text_font=Defont.add(10), text_color='darkgrey', cursor='arrow').place(relx=0.19, rely=0.65)

        CTkLabel(update_frame, text=update.how_long, fg_color=None, cursor='arrow',
                 text_color='darkgrey', text_font=Defont.add(10)).place(relx=0.8, rely=0.5)
        
        date=CTkLabel(update_frame, text=str(update.epoch.date()), fg_color=None,
                 text_color='darkgrey', text_font=Defont.add(10), cursor='arrow')
        date.text_label.grid_configure(sticky='w')
        date.place(relx=0.8, rely=0.65)

        remove = CTkButton(update_frame, text='', fg_color=update_frame.fg_color, corner_radius=20,
                           hover_color=frame.fg_color, width=80,
                           image=get_image('done.svg', wh=0.1),
                           command=update_frame.destroy)
        remove.place(relx=0.87, rely=0.1)

        update_frame.bind("<Button-1>", lambda _: self._show_update(update, from_user, to_paitent))
        for child in update_frame.winfo_children():
            if not isinstance(child, CTkButton):
                child.bind('<Button-1>', lambda _: self._show_update(update, from_user, to_paitent))

        update_frame.grid(row=r, column=c, padx=20, pady=30,
                          sticky='nw' if c == 0 else 'nw', ipadx=300)

    def _load_panel(self, frame: CTkFrame):
        user: User = self.main.user

        updates: List[Update] = self.db.get_updates(user.id).all()
        frame.after(500, self._create_frame, frame, updates[0], 4, 0)

    @transition
    def doctor_updates(self):

        main: CTkFrame = self.main.frames['main']
        a = CTkButton(main, text_font=Defont.add(30), height=50, hover=False,
                      width=200, text='Doctor Updates', fg_color=main.fg_color,
                      image=get_image('update-user.svg', wh=0.3), compound='left')
        a.grid(row=0, column=0, padx=10, pady=10, sticky='nw')

        about = 'Notify and Recieve Updates from your Doctor or from the Hospital!'
        CTkLabel(main, text_font=Defont.add(11), height=50,
                 width=600, text=about, fg_color=main.fg_color).grid(row=2, column=0, padx=10, sticky='nw')
        
        reload = CTkButton(main, text='', hover_color=Color.LABEL_BG_COLOR,
                           fg_color=Color.FRAME_2_COLOR, corner_radius=30,
                           image = get_image('reload.svg', wh=0.1))
        reload.grid(row=2, column=1, sticky='ne', padx=20)

        CTkFrame(main, height=5).grid(row=3, column=0, columnspan=2,
                                      padx=20, pady=10, sticky='ew')
        main.grid_columnconfigure(1, weight=1)
        main.after_idle(self._load_panel, main)

class UserPanel(Panel):
    level = 1

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
                        '\nAdd User', 'Add a User Linked with you!', 'add_user')
        self.main.after(500, self._shortcut, self.main.frames['main'], 'users.svg',
                        '\nAll Users', 'See all the Users Connected with you!', 'users')
        self.main.after(500, self._shortcut, self.main.frames['main'], 'update-user.svg',
                        '\nDoctor Updates', 'See the Updates from your Doctor!', 'doctor_updates')
    
    @transition
    def add_user(self):
        _AddUser(self).add_user()

    @transition
    def users(self):
        _Users(self).users()

    @transition
    def doctor_updates(self):
        _DoctorUpdates(self).doctor_updates()
