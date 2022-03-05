from tkinter import ttk, IntVar

from customtkinter import *

from core.backend import Database, get_image
from core.backend.utils import Defont, Color
from ..utils import dob, gender
from ..defaultentry import DefaultEntryText
from ..messagebox import MessageBox
from .base import Panel, transition

__all__ = ('DoctorPanel', )

class _BaseInit:
    def __init__(self, panel):
        self.panel = panel
        self.main = panel.main
        self.db: Database = panel.main.db

class _AddUser(_BaseInit): # adding Paitent

    temp = {}

    def _parse_entries(self, data):
        data = {k.lower().replace(' ', '_'): v 
               for k, v in data.items()}
        # _pass, re_pass = data.pop('password'), data.pop('re-enter_password')
        
        # if _pass != re_pass: # and (_pass and re_pass):
        #     MessageBox.warning('ok_cancel', 'The Two Passwords Entered do not Match!')
        #     return
        
        del data['user_id']
        del data['link'] # link the user as soon as it is created
        # but cant do now
        del data['age'] # no need of age
        y, m, d = [data.pop(i) for i in ('yyyy', 'mm', 'dd')]
        data['dob'] = '%s-%s-%s' % (y, m ,d)
        # data['_password'] = _pass
        return data

    def _submit(self):
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
            data = self._parse_entries(data)

            self.db.add_rec('paitents', data)

    def _clear_entries(self):
        DefaultEntryText.set_defaults(*DefaultEntryText.load_all_base('add'))

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

        check = IntVar()

        self.temp['check'] = check

        submit_img = get_image('submit.svg', wh=0.12)
        submit = CTkButton(frame, image=submit_img, text='',
                           fg_color=frame.fg_color, width=100,
                           cursor='hand2', compound='left',
                           command=self._submit)
        submit.bind('<Enter>', _expand(submit_img))
        submit.bind('<Leave>', _shrink(submit_img))
        submit.place(relx=0.53, rely=0.45)

        clear_img = get_image('erase.svg', wh=0.12)
        clear = CTkButton(frame, image=clear_img, text='',
                          fg_color=frame.fg_color, width=100,
                          cursor='hand2', compound='left',
                          command=self._clear_entries)
        clear.bind('<Enter>', _expand(clear_img))
        clear.bind('<Leave>', _shrink(clear_img))
        clear.place(relx=0.6, rely=0.45)

        agree = CTkCheckBox(frame, text=f'You Agree with the terms and Conditions of {self.main.APPNAME}',
                            text_font=Defont.add(12), border_width=1, corner_radius=10, variable=check)
        agree.place(relx=0.53, rely=0.35)

    def _load_entries(self, frame: CTkFrame):
        
        fields = ('First Name *', 'Last Name *', 'Gender *', 'dob *',
                  'User ID', 'Link', 'Doctor ID *')
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

    def add_user(self):
        main: CTkFrame = self.main.frames['main']
        a = CTkButton(main, text_font=Defont.add(30, font='Montserrat'), height=50,
                      width=200, text="New Paitent", fg_color=main.fg_color, hover=False,
                      image=get_image('add-user.svg', wh=0.3), compound='left')
        a.grid(row=0, column=0, padx=10, pady=10, sticky='nw')

        about = "Add a Paitent to the Database"
        CTkLabel(main, text_font=Defont.add(11), height=50,
                 width=600, text=about, fg_color=main.fg_color).grid(row=2, column=0, padx=10, sticky='nw')

        CTkFrame(main, height=5).grid(row=3, column=0, columnspan=2,
                                      padx=20, pady=10, sticky='ew')
        main.grid_columnconfigure(1, weight=1)
        main.after(500, self._load_entries, main)
        main.after(500, self._load_right_side, main)

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




