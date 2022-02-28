from datetime import datetime
from tkinter import IntVar, ttk

from customtkinter import *

from ...backend import Database, get_image
from ...backend.models import *
from ...backend.utils import Color, Defont
from ..defaultentry import DefaultEntryText
from ..messagebox import MessageBox
from ..utils import dob
from .base import Panel

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
        if agree := self.temp.pop('check') and (agree.get() == 0):
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
            inner = CTkFrame(frame, fg_color=Color.ENTRY)

            width = (200 if field in ['Re-Enter Password *', 'Link'] else
                     70 if field == 'Email *' else 120)

            if field != 'dob *':
                label = CTkLabel(inner, text=field.strip('*'), fg_color=None, width=width,
                                 text_font=Defont.add(16 if field != 'Link' else 13, font='Montserrat'))
                padx = (5 if 'ID' in field or field in [
                        'Password *', 'Relation'] else 20)
                label.grid(row=0, pady=5, padx=padx, sticky='nw')

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
                entry.grid(row=1, column=0, pady=10, padx=10)

            inner.grid(row=r, column=0, padx=10, pady=40 if r ==
                       4 or r == 5 else 10, sticky='nw')

            if 'Pass' in field:
                entry.grid_configure(ipadx=40, pady=10)

            if 'Last Name *' == field or 'Re-Enter Password *' == field:
                inner.grid_configure(
                    row=r-1, padx=370 if "Re" in field else 290, sticky='nw')
            elif field == 'Email *':
                inner.grid_configure(columnspan=1)
            elif field == 'dob *':
                inner.grid_configure(row=r-1, column=0, padx=420)
            elif field == 'Link':
                label.set_text("Link ID (Link to another User)")
                label.grid_configure(ipadx=25, padx=5)
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
        self.temp['two_step'] = two
        two_step = CTkCheckBox(frame, text='Enable Two-step Verification',
                               corner_radius=10, border_width=1)
        two_step.place(relx=0.53, rely=0.35)

        info = "Enabling Two-step Verification will allow a \nSafer way of accessing the account"
        CTkLabel(frame, text=info, width=300, height=40,
                 fg_color=None, text_color=Color.LABEL_BG).place(relx=0.53, rely=0.39)

        submit_img = get_image('submit.svg', wh=0.12)
        submit = CTkButton(frame, image=submit_img, text='',
                           fg_color=Color.FRAME, width=100,
                           cursor='hand2', compound='left',
                           command=self._submit)
        submit.bind('<Enter>', _expand(submit_img))
        submit.bind('<Leave>', _shrink(submit_img))
        submit.place(relx=0.53, rely=0.55)

        clear_img = get_image('erase.svg', wh=0.12)
        clear = CTkButton(frame, image=clear_img, text='',
                          fg_color=Color.FRAME, width=100,
                          cursor='hand2', compound='left',
                          command=self._clear_entries)
        clear.bind('<Enter>', _expand(clear_img))
        clear.bind('<Leave>', _shrink(clear_img))
        clear.place(relx=0.6, rely=0.55)

        check = IntVar()
        self.temp['check'] = check
        agree = CTkCheckBox(frame, text=f'You Agreed with the terms and Conditions of {self.main.APPNAME}',
                            text_font=Defont.add(12), border_width=1, corner_radius=10, variable=check)
        agree.place(relx=0.53, rely=0.48)

    def add_user(self):

        Panel._transition(self.panel)
        main: CTkFrame = self.main.frames['main']
        a = CTkButton(main, text_font=Defont.add(30, font='Montserrat'), height=50,
                      width=200, text="New User", fg_color=Color.FRAME, hover=False,
                      image=get_image('add-user.svg', wh=0.3), compound='left')
        a.grid(row=0, column=0, padx=10, pady=10, sticky='nw')

        about = "Add a User Linked With You, Or Add Multiple Users at Once From a File."
        CTkLabel(main, text_font=Defont.add(11), height=50,
                 width=600, text=about, fg_color=Color.FRAME).grid(row=2, column=0, padx=10, sticky='nw')

        CTkFrame(main, height=5).grid(row=3, column=0, columnspan=2,
                                      padx=20, pady=10, sticky='ew')
        main.grid_columnconfigure(1, weight=1)

        main.after(700, self._load_entires, main)
        main.after(700, self._load_right_side, main)

class _Users:

    def __init__(self, panel: 'UserPanel'):
        self.panel = panel
        self.main = panel.main

    def _get_connected_users(self):
        # user: UserType = self.main.user

        users = self.main.db.find_rec(1, filter_by='LINKED_ID', 
                            table='users') # run threaded
        print(users)
        # if user.linked: # there is a linked user
            # find records where the linked user ids
            

                         
        

    def users(self):
        
        Panel._transition(self.panel)
        main: CTkFrame = self.main.frames['main']
        top = CTkButton(main, text_font=Defont.add(30), height=50,
                        width=200, text = 'All Users', fg_color=Color.FRAME, hover=False,
                        image=get_image('users.svg', wh=0.3), compound='left')
        top.grid(row=0, column=0, padx=10, pady=10, sticky='nw')

        about = 'Check all the users Linked with You, along with Yourself.'
        CTkLabel(main, text_font=Defont.add(11), height=50,
                 width=600, text=about, fg_color=Color.FRAME).grid(row=2, column=0, padx=10, sticky='nw')
        CTkFrame(main, height=5).grid(row=3, column=0, columnspan=2,
                                      padx=20, pady=10, sticky='ew')
        
        main.grid_columnconfigure(1, weight=1)

        self._get_connected_users()


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
                            fg_color=Color.FRAME)
        question.pack(pady=20)

        self.main.after(500, self._shortcut, self.main.frames['main'], 'add-user.svg',
                        '\nAdd User', 'Add a User Linked with you!', 'add_user')
        self.main.after(500, self._shortcut, self.main.frames['main'], 'users.svg',
                        '\nAll Users', 'See all the Users Connected with you!', '')
        self.main.after(500, self._shortcut, self.main.frames['main'], 'update-user.svg',
                        '\nDoctor Updates', 'See the Updates from your Doctor!', '')
    
    def add_user(self):
        _AddUser(self).add_user()

    def users(self):
        _Users(self).users()
