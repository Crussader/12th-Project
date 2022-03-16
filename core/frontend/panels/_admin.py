import itertools
from tkinter import IntVar, Toplevel, ttk
from tkinter.simpledialog import askstring
from typing import Union

from core.backend import Database, get_image
from core.backend.models import *
from core.backend.utils import (Color, Defont, ThreadPool, get_age,
                                get_outer_path, rand_id, random_key)
from customtkinter import *
from PIL import Image, ImageDraw, ImageFont, ImageTk

from ..defaultentry import DefaultEntryText
from ..messagebox import MessageBox
from ..utils import center, dob
from .base import Panel, transition

__all__ = ('AdminPanel', )

class _BaseInit:
    def __init__(self, panel: 'AdminPanel'):
        self.panel = panel
        self.main = panel.main
        self.db: Database = panel.main.db

class _AddUser(_BaseInit):
    temp = {}

    @transition
    def add_user(self):
        main: CTkFrame = self.main.frames['main']
        top = CTkButton(main, text_font=Defont.add(30), height=50,
                        width=200, text='Add User', fg_color=main.fg_color, 
                        hover=False, image=get_image('add-user.svg', wh=0.3),
                        compound='left')
        top.grid(row=0, column=0, padx=10, pady=10, sticky='nw')

        about = 'Add User or Paitent to the Database, You can add multiple records into the Database.'
        CTkLabel(main, text_font=Defont.add(11), height=50,
                 width=600, text=about, fg_color=main.fg_color).grid(row=2, column=0, padx=10, sticky='nw')
        CTkFrame(main, height=5).grid(row=3, column=0, columnspan=2,
                                      padx=20, pady=10, sticky='ew')
        
        main.grid_columnconfigure(1, weight=1)
        main.after(500, self._load_options)

    def _load_options(self):
        main: CTkFrame = self.main.frames['main']

        paitent = CTkFrame(main, cursor='hand2', corner_radius=30)
        CTkFrame(paitent, height=50, fg_color=paitent.fg_color).pack(pady=20)
        short = CTkButton(paitent, text='Paitent', fg_color=paitent.fg_color,
                          compound="top", image=get_image('paitent.svg'),
                          hover=False, text_font=Defont.add(20, font='Montserrat'),
                          command=self._add_paitent)
        short.pack(pady=5, padx=20)

        CTkLabel(paitent, text='Add a Paitent to the Database', width=350, fg_color=paitent.fg_color,
                 text_font=Defont.add(11, font='Montserrat'), text_color="lightgrey").pack(pady=10)

        CTkFrame(paitent, height=50, fg_color=paitent.fg_color).pack(pady=20, padx=20)
        
        main.bind('<Button-1>', lambda _: self._add_paitent)

        paitent.place(relx=0.25, rely=0.3)
        self.panel._hover(paitent, color_out=paitent.fg_color)

        ###

        user = CTkFrame(main, cursor='hand2', corner_radius=30)
        CTkFrame(user, height=50, fg_color=user.fg_color).pack(pady=20, padx=20)
        short = CTkButton(user, text='User', fg_color=user.fg_color,
                          compound="top", image=get_image('user.svg'),
                          hover=False, text_font=Defont.add(20, font='Montserrat'),
                          command=self._add_user)
        short.pack(pady=5, padx=20)

        CTkLabel(user, text='Add a User to the Database', width=350, fg_color=user.fg_color,
                 text_font=Defont.add(11, font='Montserrat'), text_color="lightgrey").pack(pady=10)

        CTkFrame(user, height=50, fg_color=user.fg_color).pack(pady=20)
        user.place(relx=0.55, rely=0.3)
        self.panel._hover(user, color_out=user.fg_color)

    def _parse_entries(self, data, type_: str):
        data = {k.lower().replace(' ', '_'): v 
               for k, v in data.items()}

        if type_ == 'users':
            _pass, re_pass = data.pop('password'), data.pop('re-enter_password')
        
            if _pass != re_pass: # and (_pass and re_pass):
                MessageBox.warning('ok_cancel', 'The Two Passwords Entered do not Match!')
                return
            
            data['_password'] = _pass
            data['name'] = ' '.join([data.pop('first_name'), data.pop('last_name')])
            
        del data['age']
        y, m, d = [data.pop(i) for i in ('yyyy', 'mm', 'dd')]
        data['dob'] = '%s-%s-%s' % (y, m ,d)
        data['id'] = rand_id()

        return data
        

    def _clear_entries(self):
        DefaultEntryText.set_defaults(*DefaultEntryText.load_all_base('add'))

    def _submit(self, type_: str):
        agree = self.temp.get('check')
        if agree and agree.get() == 0:
            msg = f"You can not Procceed without Agreeing to the terms and Conditions of {self.main.APPNAME}"
            MessageBox.warning('ok_cancel', msg)
            return

        entries = DefaultEntryText.load_all_base('add')

        empty = ', '.join(e.text for e in entries if not e.get_text() and 
                          e.text not in ['User ID', 'Link'])

        if empty:
            msg = f"You Have missed the following fields\n{empty}"
            MessageBox.warning('ok_cancel', msg)
        else:
            data = {e.text[:-1] if e.text[-1].isspace() 
                    else e.text: e.get_text() for e in entries}
            data['gender'] = self.temp.pop('gender').get()        
            data = self._parse_entries(data, type_)
            self.db.add_rec(type_, data)
            

    def _load_adding_of_paitent(self):
        main: CTkFrame = self.main.frames['main']
        def _expand(img):
            """Expand a Button a little when on hover"""
            def inner(_):
                main.after(50)
                img.configure(scale=0.14)

            return inner

        def _shrink(img):
            def inner(_):
                main.after(50)
                img.configure(scale=0.12)

            return inner

        CTkFrame(main, width=5).place(relx=0.5, rely=0.4, relheight=0.5)

        check = IntVar()
        self.temp['check'] = check

        submit_img = get_image('submit.svg', wh=0.12)
        submit = CTkButton(main, image=submit_img, text='', fg_color=main.fg_color, width=100,
                           cursor='hand2', compound='left', command=lambda: self._submit('paitents'))
        submit.bind('<Enter>', _expand(submit_img))
        submit.bind('<Leave>', _shrink(submit_img))
        submit.place(relx=0.53, rely=0.45)

        clear_img = get_image('erase.svg', wh=0.12)
        clear = CTkButton(main, image=clear_img, text='', fg_color=main.fg_color, width=100,
                        cursor='hand2', compound='left', command=self._clear_entries)
        clear.bind('<Enter>', _expand(clear_img))
        clear.bind('<Leave>', _shrink(clear_img))
        clear.place(relx=0.6, rely=0.45)

        agree = CTkCheckBox(main, text=f'You Agree with the terms and Conditions of {self.main.APPNAME}',
                            text_font=Defont.add(12), border_width=1, corner_radius=10, variable=check)
        agree.place(relx=0.53, rely=0.35)

        top = CTkButton(main, text='Add Paitent', image=get_image('paitent.svg', wh=0.2),
                width=150, height=50, fg_color=main.fg_color, hover=False, 
                compound='left', text_font=Defont.add(25))
        top.grid(row=0, column=0, padx=10, pady=10, sticky='nw')

        about = "Add a Paitent to the Database"
        l = CTkLabel(main, text_font=Defont.add(11), height=50,
                 width=600, text=about, fg_color=main.fg_color)
        l.grid(row=2, column=0, padx=10, sticky='nw')

        back = CTkButton(main, fg_color=main.fg_color, hover=False, height=30,
                         command=self.add_user, text='', image=get_image('back.svg', wh=0.1),
                         width=50, compound='left', cursor='hand2')
        back.place(relx=0.023, rely=0.15)
        
        CTkFrame(main, height=5).grid(row=3, column=0, columnspan=2,
                                      padx=20, pady=10, sticky='ew')
        main.grid_columnconfigure(1, weight=1)

        fields = ('First Name *', 'Last Name *', 'Gender *', 'dob *',
                  'User ID', 'Link', 'Doctor ID *')
        r = 4

        for field in fields:
            inner = CTkFrame(main, fg_color=Color.ENTRY_COLOR)

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

            if 'Last Name *' == field:
                inner.grid_configure(row=r-1, padx=290, sticky='nw')
            elif field == 'dob *':
                inner.grid_configure(row=r-2, column=0, padx=300)
                req.grid_configure(padx=0)
            elif field == 'Link':
                label.configure(width=22, text="Link ID (Link to another User)")
                entry.configure(width=22)
                inner.grid_configure(row=r-1, column=0, padx=300)
            elif field == 'Gender *':
                inner.grid_configure(row=r-1, column=0, padx=10)
            r += 1

    def _load_adding_of_user(self):
        main: CTkFrame = self.main.frames['main']
        def _expand(img):
            """Expand a Button a little when on hover"""
            def inner(_):
                main.after(50)
                img.configure(scale=0.14)

            return inner

        def _shrink(img):
            def inner(_):
                main.after(50)
                img.configure(scale=0.12)

            return inner

        CTkFrame(main, width=5).place(relx=0.5, rely=0.4, relheight=0.5)

        two = IntVar()
        check = IntVar()
        self.temp['check'] = check

        self.temp['two_step'] = two
        self.temp['check'] = check

        two_step = CTkCheckBox(main, text='Enable Two-step Verification',
                               corner_radius=10, border_width=1)
        two_step.place(relx=0.53, rely=0.35)

        info = "Enabling Two-step Verification will allow a \nSafer way of accessing the account"
        CTkLabel(main, text=info, width=300, height=40,
                 fg_color=None, text_color=Color.LABEL_BG_COLOR).place(relx=0.53, rely=0.39)

        submit_img = get_image('submit.svg', wh=0.12)
        submit = CTkButton(main, image=submit_img, text='', fg_color=main.fg_color, width=100,
                           cursor='hand2', compound='left', command=lambda: self._submit('users'))
        submit.bind('<Enter>', _expand(submit_img))
        submit.bind('<Leave>', _shrink(submit_img))
        submit.place(relx=0.53, rely=0.55)

        clear_img = get_image('erase.svg', wh=0.12)
        clear = CTkButton(main, image=clear_img, text='', fg_color=main.fg_color, width=100,
                        cursor='hand2', compound='left', command=self._clear_entries)
        clear.bind('<Enter>', _expand(clear_img))
        clear.bind('<Leave>', _shrink(clear_img))
        clear.place(relx=0.6, rely=0.55)
        

        agree = CTkCheckBox(main, text=f'You Agree with the terms and Conditions of {self.main.APPNAME}',
                            text_font=Defont.add(12), border_width=1, corner_radius=10, variable=check)
        agree.place(relx=0.53, rely=0.48)

        top = CTkButton(main, text='Add User', image=get_image('paitent.svg', wh=0.2),
                width=150, height=50, fg_color=main.fg_color, hover=False, 
                compound='left', text_font=Defont.add(25))
        top.grid(row=0, column=0, padx=10, pady=10, sticky='nw')

        about = "Add a User to the Database"
        l = CTkLabel(main, text_font=Defont.add(11), height=50,
                 width=600, text=about, fg_color=main.fg_color)
        l.grid(row=2, column=0, padx=10, sticky='nw')

        back = CTkButton(main, fg_color=main.fg_color, hover=False, height=30,
                         command=self.add_user, text='', image=get_image('back.svg', wh=0.1),
                         width=50, compound='left', cursor='hand2')
        back.place(relx=0.023, rely=0.15)

        CTkFrame(main, height=5).grid(row=3, column=0, columnspan=2,
                                      padx=20, pady=10, sticky='ew')
        main.grid_columnconfigure(1, weight=1)

        fields = ('First Name *', 'Last Name *', 'Gender *', 'Email *', 'dob *',
                  'Paitent ID', 'Link', 'Password *', 'Re-Enter Password *')
        r = 4

        for field in fields:
            inner = CTkFrame(main, fg_color=Color.ENTRY_COLOR)

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

    @transition
    def _add_paitent(self):
        main: CTkFrame = self.main.frames['main']
        main.after(500, self._load_adding_of_paitent)

    @transition
    def _add_user(self):
        main: CTkFrame = self.main.frames['main']
        main.after(500, self._load_adding_of_user)

class _FindUser(_BaseInit):

    filter_by = None

    @transition
    def find_user(self):
        main: CTkFrame = self.main.frames['main']
        a = CTkButton(main, text_font=Defont.add(30, font='Montserrat'), height=50,
                      width=200, text="Find Paitent", fg_color=main.fg_color, hover=False,
                      image=get_image('find-user.svg', wh=0.3), compound='left')
        a.grid(row=0, column=0, padx=10, pady=10, sticky='nw')

        about = "Find a Paitent or User from the Database"
        CTkLabel(main, text_font=Defont.add(11), height=50,
                 width=600, text=about, fg_color=main.fg_color).grid(row=2, column=0, padx=10, sticky='nw')

        CTkFrame(main, height=5).grid(row=3, column=0, columnspan=2,
                                      padx=20, pady=10, sticky='ew')
        main.grid_columnconfigure(1, weight=1)
        main.after(500, self._load_search_box, main)

    @transition
    def _load_individual(self, user: User):
        main: CTkFrame = self.main.frames['main']
        dp = get_image('user.svg', wh=0.3)
        top = CTkButton(main, text_font=Defont.add(30), height=50, hover=False,
                        width=200, text=user.name.title(), fg_color=main.fg_color,
                        image=dp, compound='left')
        top.grid(row=0, column=0, padx=10, pady=10, sticky='nw')
        

        info = f"User ID: {user.id} \t Paitent ID: {user.paitent.id}"
        l=CTkLabel(main, text_font=Defont.add(11, font='Avenir'), height=50,
                 width=600, text=info, fg_color=main.fg_color, justify='left')
        l.grid(row=2, column=0, padx=10, sticky='nw')
        
        back = CTkButton(main, fg_color=main.fg_color, hover=False, height=30,
                         command=self.find_user, text='', image=get_image('back.svg', wh=0.1),
                         width=50, compound='left', cursor='hand2')
        back.place(relx=0.023, rely=0.2)

        CTkFrame(main, height=5).grid(row=3, column=0, columnspan=2,
                                      padx=20, pady=10, sticky='ew')
        main.grid_columnconfigure(1, weight=1)

        def _load():
            attrs = {k: getattr(user, k) for k in user.__slots__}
            r = 4
            column = itertools.cycle([0, 1])
            for k, v in attrs.items():
                if k in ['level', '_password']:
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
                l.text_label.grid_configure(sticky='w')
                # l.text_label.configure(justify='left')
                l.pack(pady=5, padx=5, side='left')

                val = CTkLabel(inner, text=value, text_font=Defont.add(15),
                            fg_color=None, height=40, width=300)
                val.text_label.grid_configure(sticky='w')
                val.pack(pady=5, padx=5, side='right')
                inner.grid(row=r if c == 0 else r-1, column=c, 
                            padx=10, sticky='nw', pady=10)
                r += 1

            remove_user = CTkButton(main, text='Delete User', image=get_image('remove-user.svg', wh=0.15),
                                    compound='top', text_font=Defont.add(11),
                                    command=lambda: self.main._set_and_run(self.main.frames['delete_user'], 
                                                                           _RemoveUser(self.panel).remove_user(user)))


            remove_user.grid(row=r, column=0, sticky='nw', pady=20, padx=20)
            
        main.after_idle(_load)
    

    def _create_frame(self, frame: CTkFrame, user: User, r, c):
        fr = CTkFrame(frame, fg_color=Color.FRAME_COLOR, corner_radius=30, cursor='hand2')
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
                       text_font=Defont.add(10), width=50)
        age.place(relx=0.2, rely=0.5)

        CTkLabel(fr, text=f'User ID: {user.id}', fg_color=None, width=180).place(relx=0.27, rely=0.5)
        
        CTkLabel(fr, text=f'Paitent ID: {user.paitent.id}', fg_color=None, width=200).place(relx=0.5, rely=0.5)

        fr.bind('<Button-1>', lambda _: self._load_individual(user))
        for w in fr.winfo_children():
            if not isinstance(w, CTkButton):
                w.bind('<Button-1>', lambda _: self._load_individual(user))

        fr.grid(row=r, column=c, padx=20, pady=30,
                stick='nw' if c == 0 else 'ne', ipadx=300)

    def _search_user(self, box: ttk.Entry):

        def _no_result():
            im = get_image('not-found.svg', wh=0.4)
            a = CTkButton(main, fg_color=Color.FRAME_COLOR, hover=False,
                        image=im, text='Could not find the User :(', 
                        height=300, width=300, compound='top',
                        text_color='grey')
            a.place(relx=0.4, rely=0.4)

        main: CTkFrame = self.main.frames['main']
        for wid in main.winfo_children():
            if isinstance(wid, CTkButton) and 'Could not find' in wid.text:
                wid.destroy()
                break
        
        field = box.get()
        
        if self.filter_by:
            if self.filter_by == 'id':
                try:
                    field = int(field)
                except ValueError:
                    _no_result()
                    return 
        else:
            try:
                field = int(field)
                self.filter_by = 'id'
            except ValueError:
                if '@' in field:
                    self.filter_by = 'email'
                else:
                    self.filter_by = 'name'
            
        for table in ('users', 'paitents'):
            filter_by = (self.filter_by.upper() if self.filter_by in ['id', 'email'] 
                         else 'FIRST_NAME' if table == 'paitents' and self.filter_by == 'name' 
                         else self.filter_by.upper())
            t = self.db.find_rec(field, filter_by, table=table)
            result: Result = ThreadPool.wait_result(t)
            if not result.is_empty:
                r = 4 
                c = itertools.cycle([0, 1])
                for res in result.many(6):
                    user = res if isinstance(res, User) else res.user
                    self._create_frame(main, user, r, next(c))
                    r+=1
                break
        else:
            _no_result()                

    @staticmethod
    def _set(by):
        _FindUser.filter_by = by

    def _show_filter_by(self, frame: CTkFrame, btn: CTkButton):
        btn.set_state('disabled')
        main : CTkFrame = self.main.frames['main']

        def _expand(i: int):
            cnf = frame.grid_info()
            cnf['ipadx'] = i
            frame.grid_configure(**cnf)
            if  i <= 100:
                main.after(1, _expand, i+5)
            
        main.after(1, _expand, 5)
        # color = Color.FRAME_COLOR[AppearanceModeTracker.appearance_mode]
        # color = Color.darken_hex_color(color)
        _id = CTkButton(frame, text='By ID', fg_color=frame.fg_color, 
                        cursor='hand2', hover_color=Color.LABEL_BG_COLOR,
                        command=lambda: self._set('id'))
        _id.pack(side='left', anchor='nw', padx=5, pady=10)

        sep = ttk.Separator(frame, orient='vertical')
        sep.pack(side='left', anchor='nw', padx=5, pady=10, fill='y')

        _name = CTkButton(frame, text='By Name', fg_color=frame.fg_color, 
                          cursor='hand2', hover_color=Color.LABEL_BG_COLOR,
                          command=lambda: self._set('name'))
        _name.pack(side='left', anchor='nw', padx=5, pady=10)

        sep1 = ttk.Separator(frame, orient='vertical')
        sep1.pack(side='left', anchor='nw', padx=5, pady=10, fill='y')

        _email = CTkButton(frame, text='By Email', fg_color=frame.fg_color, 
                           cursor='hand2', hover_color=Color.LABEL_BG_COLOR,
                           command=lambda: self._set('email'))
        _email.pack(side='left', anchor='nw', padx=5, pady=10)

        sep2 = ttk.Separator(frame, orient='vertical')
        sep2.pack(side='left', anchor='nw', padx=5, pady=10, fill='y')


    def _load_search_box(self, frame: CTkFrame):

        search_frame = CTkFrame(frame, fg_color=Color.ENTRY_COLOR)
        
        im =get_image('search.svg', wh=0.1) 
        l = CTkButton(search_frame, text='', image=im, width=60, 
                      fg_color=Color.ENTRY_COLOR, hover=False, cursor='hand2',
                      command=lambda: self._search_user(search))
        l.grid(row=0, column=0, padx=10)

        search = ttk.Entry(search_frame, font='Montserrat', width=40)
        DefaultEntryText.add(search, 'Search (ID, Name, ...)', name='search.entry').bind()
        search.grid(row=0, column=1, pady=10, padx=10, sticky='nw')
        search_frame.grid(row=0, column=1, pady=30, padx=10, sticky='ne')

        filter_frame = CTkFrame(frame)
        _by = CTkButton(filter_frame, text='Filter by', fg_color=filter_frame.fg_color,
                        command=lambda: self._show_filter_by(filter_frame, _by))
        _by.pack(side='right', padx=5, pady=10)
        filter_frame.grid(row=2, column=1, sticky='ne', padx=10)


class _RemoveUser(_BaseInit):

    def _verification_id(self, user, im):

        def _check():
            if _input.get() in self.db.vertification.values():
                id_ =self.db.vertification.get(user.id)
                self.db.delete_rec(user.id, id_, table='users')
                self.db.delete_rec(user.paitent.id, id_, table='paitents')
                del self.db.vertification[user.id]
                self.panel.home()

        def _destroy():
            del self.db.vertification[user.id]
            win.destroy()

        win = Toplevel()
        win.attributes('-topmost', True)
        win.overrideredirect(True)

        win.geometry("600x300")
        center(win, 600, 300)

        title_frame = ttk.Frame(win, relief='flat')
        close = ttk.Button(title_frame, text="X", command=_destroy)
        title = ttk.Label(title_frame, text='Question', font=Defont.add(11))
        close.pack(side='right', anchor='ne')
        title.pack(side='top', anchor='n')
        title_frame.pack(fill='x', padx=5)

        CTkLabel(win, text='Please Enter The Code from the Image', text_font=Defont.add(12)).pack(pady=10)
        _im = CTkLabel(win, text='', image=im)
        _im.image=im
        _im.pack(pady=5)

        _input = ttk.Entry(win, font=Defont.add(12))
        _input.pack(pady=20)

        CTkButton(win, text='Ok', command=_check, width=100).place(relx=0.25, rely=0.8)
        CTkButton(win, text='Cancel', command=_destroy, width=100, fg_color=win['bg']).place(relx=0.45, rely=0.8)
        win.mainloop()

    def _remove(self, user: User):
        password = askstring('Remove User', 'Please Enter your Password.', show='*')

        if self.main.user._password == password:
            key = random_key(k=10)
            with Image.new('RGB', (250, 60)) as img:
                draw = ImageDraw.Draw(img)
                font = ImageFont.truetype(get_outer_path('assets', 'fonts', 'Shizuru-Regular.ttf'), size=40)
                draw.text((5, 0), key, fill=(255, 255, 0), font=font)
                tk_image = ImageTk.PhotoImage(img)
                self.db.vertification[user.id] = key
                self._verification_id(user, tk_image)

    def remove_user(self, user: Union[User, Paitent] = None):
        if user is None:
            # self.panel.find_user()
            self.main._set_and_run(self.main.frames['find_user'], 'find_user')
        else:
            Panel._transition(self.panel)
            main: CTkFrame = self.main.frames['main']
            top = CTkButton(main, text_font=Defont.add(30), height=50,
                            width=200, text='Remove User', fg_color=main.fg_color, 
                            hover=False, image=get_image('remove-user.svg', wh=0.3),
                            compound='left')
            top.grid(row=0, column=0, padx=10, pady=10, sticky='nw')

            about = 'Remove Users or Paitents from the Database.'
            l = CTkLabel(main, text_font=Defont.add(11), height=50,
                     width=600, text=about, fg_color=main.fg_color)
            l.text_label.grid_configure(sticky='nw')
            l.grid(row=2, column=0, padx=10, sticky='nw')
            CTkFrame(main, height=5).grid(row=3, column=0, columnspan=2,
                                          padx=20, pady=10, sticky='ew')
            main.grid_columnconfigure(1, weight=1)

            user: User = user if isinstance(user, User) else user.user
            attrs = {k: getattr(user, k) for k in user.__slots__}
            r = 4
            column = itertools.cycle([0, 1])
            for k, v in attrs.items():
                if k in ['level', '_password']:
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
                l.text_label.grid_configure(sticky='w')
                # l.text_label.configure(justify='left')
                l.pack(pady=5, padx=5, side='left')

                val = CTkLabel(inner, text=value, text_font=Defont.add(15),
                            fg_color=None, height=40, width=300)
                val.text_label.grid_configure(sticky='w')
                val.pack(pady=5, padx=5, side='right')
                inner.grid(row=r if c == 0 else r-1, column=c, 
                            padx=10, sticky='nw', pady=10)
                r += 1

            MessageBox.warning('ok_cancel', f'Are you sure you want to Remove `{user.name}` from the Database, Note: You Can not Undo This Action.',
                               yes_command=lambda: self._remove(user), no_command=self.panel.home)

class AdminPanel(Panel):
    level=3

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
        
        main_win: CTkFrame = self.main.frames['main']
        question = CTkLabel(main_win, text_font=Defont.add(30, font='Montserrat'),
                            height=50, width=700, text="What would you like to do today?",
                            fg_color=main_win.fg_color)
        question.pack(pady=20)
        self.main.after(500, self._shortcut, main_win, 'add-user.svg', '\nAdd User',
                        'Add a Paitent or User to Database', 'add_user')
        self.main.after(500, self._shortcut, main_win, 'find-user.svg', '\nFind User',
                        'Find Paitent or User in the Database', 'find_user')
        self.main.after(500, self._shortcut, main_win, 'remove-user.svg', '\nRemove User',
                        'Remove a Paitent or User From the Database', 'delete_user')
        
    def add_user(self):
        _AddUser(self).add_user() 

    def find_user(self):
        _FindUser(self).find_user()

    def delete_user(self):
        _RemoveUser(self).remove_user()
