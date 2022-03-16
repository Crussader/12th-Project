import itertools
from tkinter import IntVar, Text, Toplevel, ttk

from core.backend import Database, get_image
from core.backend.models import *
from core.backend.utils import Color, Defont, ThreadPool, get_age, rand_id
from customtkinter import *

from ..defaultentry import DefaultEntryText
from ..messagebox import MessageBox
from ..utils import center, dob
from .base import Panel, transition

__all__ = ('DoctorPanel', )

class _BaseInit:
    def __init__(self, panel: 'DoctorPanel'):
        self.panel = panel
        self.main = panel.main
        self.db: Database = panel.main.db

class _AddUser(_BaseInit): # adding Paitent

    temp = {}

    def _parse_entries(self, data):
        data = {k.lower().replace(' ', '_'): v 
               for k, v in data.items()}
        
        # del data['user_id']
        # del data['link'] # link the user as soon as it is created
        del data['age'] # no need of age
        y, m, d = [data.pop(i) for i in ('yyyy', 'mm', 'dd')]
        data['dob'] = '%s-%s-%s' % (y, m ,d)
        data['id'] = rand_id()
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

    @transition
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

            update_user = CTkButton(main, text='Update User', image=get_image('update-user.svg', wh=0.15),
                                    compound='top', text_font=Defont.add(11), 
                                    command=lambda: self.main._set_and_run(self.main.frames['update_paitent'], 
                                                                           _UpdatePaitent(self.panel).update_user(user)))

            update_user.grid(row=r, column=0, sticky='nw', pady=20, padx=20)
            
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
        # l=CTkLabel(search_frame, text='Search', text_font=Defont.add(16), 
        #          fg_color=None, justify='left', width=70)
        # l.grid(row=0, pady=5, padx=10, sticky='nw')
        
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

class _UpdatePaitent(_BaseInit):

    @transition
    def update_paitent(self):
        main: CTkFrame = self.main.frames['main']

        top = CTkButton(main, text_font=Defont.add(30), height=50,
                        width=200, text='Update Users', fg_color=main.fg_color, 
                        hover=False, image=get_image('update-user.svg', wh=0.3),
                        compound='left')
        top.grid(row=0, column=0, padx=10, pady=10, sticky='nw')

        about = 'Check Replies from Paitents or Update paitents.'
        CTkLabel(main, text_font=Defont.add(11), height=50,
                 width=600, text=about, fg_color=main.fg_color).grid(row=2, column=0, padx=10, sticky='nw')
        CTkFrame(main, height=5).grid(row=3, column=0, columnspan=2,
                                      padx=20, pady=10, sticky='ew')
        
        main.grid_columnconfigure(1, weight=1)
        main.after(400, self._load_options)
    
    def _load_options(self):
        main: CTkFrame = self.main.frames['main']

        reply_user = CTkFrame(main, cursor='hand2', corner_radius=30)
        CTkFrame(reply_user, height=50, fg_color=reply_user.fg_color).pack(pady=20)
        short = CTkButton(reply_user, text='Replies', fg_color=reply_user.fg_color,
                          compound="top", image=get_image('reply.svg'),
                          hover=False, text_font=Defont.add(20, font='Montserrat'),
                          command=self.replies)
        short.pack(pady=5, padx=20)

        CTkLabel(reply_user, text='Check Replies from Paitents', width=350, fg_color=reply_user.fg_color,
                 text_font=Defont.add(11, font='Montserrat'), text_color="lightgrey").pack(pady=10)

        CTkFrame(reply_user, height=50, fg_color=reply_user.fg_color).pack(pady=20, padx=20)
        
        main.bind('<Button-1>', lambda _: self.replies)

        reply_user.place(relx=0.25, rely=0.3)
        self.panel._hover(reply_user, color_out=reply_user.fg_color)

        ###

        update_user = CTkFrame(main, cursor='hand2', corner_radius=30)
        CTkFrame(update_user, height=50, fg_color=update_user.fg_color).pack(pady=20, padx=20)
        short = CTkButton(update_user, text='Update Paitent', fg_color=update_user.fg_color,
                          compound="top", image=get_image('update-user.svg'),
                          hover=False, text_font=Defont.add(20, font='Montserrat'),
                          command=self.update_user)
        short.pack(pady=5, padx=20)

        CTkLabel(update_user, text='Update Paitents on their Condition', width=350, fg_color=update_user.fg_color,
                 text_font=Defont.add(11, font='Montserrat'), text_color="lightgrey").pack(pady=10)

        CTkFrame(update_user, height=50, fg_color=update_user.fg_color).pack(pady=20)
        update_user.place(relx=0.55, rely=0.3)
        self.panel._hover(update_user, color_out=update_user.fg_color)

    def _seen(self, update, frame):
        updated = self.db.update_rec(update.id, 'updates', {'seen': 1})
        if updated:
            try:
                frame.destroy()
            except Exception:
                pass

    def _reply_window(self, main: CTkFrame, update: Update, _from: Paitent, _to: Doctor):

        def _update():
            reply_text = text.get(1.0, 'end')
            done = self.db.update_user(_from.id, _to.id, reply_text)
            self.db.update_rec(update.id, 'updates', {'seen': 1, 'replied': 1})
            if done:
                top.destroy()
                self.replies()                

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

    @staticmethod
    def _clean_string(string: str):
        return '\n'.join(i for i in string.strip('"\'').split('\\n'))

    @staticmethod
    def _shorten(text: str, at: int=30):
        return text[:at] + '....'

    @transition
    def _reply(self, update: Update, from_user: Paitent, to_doctor: Doctor):
        main: CTkFrame = self.main.frames['main']

        def load():
            dp = get_image('user.svg', wh=0.3)
            top=CTkButton(main, text='', height=50, hover=False,
                        width=200, fg_color=main.fg_color,
                        image=dp)
            top.grid(row=0, column=0, padx=10, pady=10, sticky='nw')

            CTkFrame(main, width=5, height=150).grid(row=0, column=1, padx=5)

            from_label = CTkLabel(main, text=f"From: \t{from_user.name.title()}", corner_radius=20,
                                height=40, text_font=Defont.add(15), fg_color=None)
            from_label.text_label.grid_configure(sticky='w')
            from_label.grid(row=0, column=2, sticky='nw', pady=30)

            to_label = CTkLabel(main, text=f"To: \tDr. {to_doctor.name.title()}",
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
                            command=lambda: self._reply_window(main, update, from_user, to_doctor))
            reply.place(relx=0.15, rely=0.15)

            back = CTkButton(main, fg_color=main.fg_color, hover=False, height=30,
                         command=self.replies, text='', image=get_image('back.svg', wh=0.1),
                         width=50, compound='left', cursor='hand2')
            back.place(relx=0.023, rely=0.2)
        
        main.after(500, load)

    def _create_update_frame(self, update: Update, r, c, to_doctor: Doctor):
        main: CTkFrame = self.main.frames['main']

        update_frame = CTkFrame(main, fg_color=Color.FRAME_COLOR, corner_radius=30, cursor='hand2')

        dp = get_image('user.svg', wh=0.2)
        display = CTkLabel(update_frame, image=dp, height=120)
        display.image=dp
        display.pack(side='left', padx=10, pady=10)

        t = self.db.find_rec(update.from_id, 'ID', table='paitents')
        from_user: Paitent = ThreadPool.wait_result(t).one()

        _from = CTkLabel(update_frame, text=from_user.name.title(),
                         height=30, text_font=Defont.add(15), fg_color=None,
                         cursor='arrow')
        _from.place(relx=0.2, rely=0.25)

        to =CTkLabel(update_frame, text=f"To: {to_doctor.name.title()}", fg_color=None,
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

        color = update_frame.fg_color[AppearanceModeTracker.appearance_mode]
        remove = CTkButton(update_frame, text='', fg_color=color, corner_radius=20,
                           hover_color=Color.darken_hex_color(color), width=80,
                           image=get_image('done.svg', wh=0.1), command=lambda: self._seen(update, update_frame))
        remove.place(relx=0.87, rely=0.1)

        update_frame.bind("<Button-1>", lambda _: self._reply(update, from_user, to_doctor))
        for child in update_frame.winfo_children():
            if not isinstance(child, CTkButton):
                child.bind('<Button-1>', lambda _: self._reply(update, from_user, to_doctor))

        update_frame.grid(row=r if c==0 else r-1, column=c, 
                          padx=20, pady=120 if r==0 or c==1 else 30, 
                          sticky='nw', ipadx=300)
        
    @transition
    def replies(self):
        main: CTkFrame = self.main.frames['main']

        back = CTkButton(main, fg_color=main.fg_color, hover=False, height=30,
                         command=self.update_paitent, text='', image=get_image('back.svg', wh=0.1),
                         width=50, cursor='hand2')
        back.place(relx=0.023, rely=0.05)

        reload = CTkButton(main, text='', hover=False, fg_color=main.fg_color, height=30,
                           command=self.replies, image=get_image('reload.svg', wh=0.1))
        reload.place(relx=0.06, rely=0.05)

        t = self.db.find_rec(self.main.user.id, 'USER_ID', table='doctor')
        doc: Doctor = ThreadPool.wait_result(t).one()

        updates = self.db.get_updates(doc.id, reply=True)
        if not updates:
            im = get_image('not-found.svg', wh=0.4)
            a = CTkButton(main, fg_color=main.fg_color, hover=False,
                        image=im, text='No New Updates.', 
                        height=300, width=300, compound='top',
                        text_color='grey')
            a.place(relx=0.4, rely=0.4)
        else:
            _updates = updates.all()
            r=0
            c = itertools.cycle([0, 1])
            for update in _updates[:6]:
                update.text = self._clean_string(update.text)
                self._create_update_frame(update, r, next(c), doc)
                r += 1 

    def update_user(self, user: User = None):
        def _send_update(from_id, to_id, text):
            self.db.update_user(from_id, to_id, text)
            _destroy()

        def _destroy():
            for wd in main.winfo_children():
                if isinstance(wd, (ttk.Separator, CTkLabel, Text)):
                    wd.destroy()   

            self.panel.update_paitent()

        def _load():
            current_user: User = self.main.user
            from_label = CTkLabel(main, text=f'From: \tDr. {current_user.name.title()}', height=30, 
                            text_font=Defont.add(13), fg_color=None, justify='left')
            from_label.pack(anchor='nw', padx=10, pady=10)

            ttk.Separator(main).pack(fill='x', padx=10)

            to_label = CTkLabel(main, text=f'To: \t{user.name.title()}', height=30,
                            text_font=Defont.add(13), fg_color=None, justify='left')
            to_label.pack(anchor='nw', padx=10, pady=10)

            ttk.Separator(main).pack(fill='x', padx=10)

            color = main.fg_color[AppearanceModeTracker.appearance_mode]
            text = Text(main, font=Defont.add(12), height=50, relief='flat', background=color)
            text.focus()
            text.pack(anchor='nw', padx=10, pady=10)

            reply = CTkButton(main, image=get_image('send.svg', wh=0.05), cursor='hand2',
                                fg_color=color, text='', width=50, corner_radius=20, 
                                hover_color=Color.FRAME_COLOR, height=35,
                                command=lambda: None)
            reply.place(relx=0.95, rely=0.01)
            back = CTkButton(main, image=get_image('back.svg', wh=0.05), cursor='hand2',
                                fg_color=color, text='', width=50, corner_radius=20,
                                hover_color=Color.FRAME_COLOR, height=35,
                                command=_destroy)
            back.place(relx=0.9, rely=0.01)

        if user is None:
            self.main._set_and_run(self.main.frames['find_user'], 'find_user')
        else:
            Panel._transition(self.panel)
            main: CTkFrame = self.main.frames['main']
            main.after(700, _load)

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

        main_win: CTkFrame = self.main.frames['main']

        question = CTkLabel(main_win, text_font=Defont.add(30, font='Montserrat'),
                            height=50, width=700, text="What would you like to do today?",
                            fg_color=main_win.fg_color)
        question.pack(pady=20)

        self.main.after(500, self._shortcut, main_win, 'add-user.svg',
                        '\nAdd Paitent', 'Add a Paitent to the Database', 'add_user')
        self.main.after(500, self._shortcut, main_win, 'find-user.svg',
                        '\nFind Paitent', 'Find Patients From the Database!', 'find_user')
        self.main.after(500, self._shortcut, main_win, 'update-user.svg',
                        '\nPaitent Updates', 'Update Paitents on their situation!', 'update_paitent')

    def add_user(self):
        _AddUser(self).add_user()

    def find_user(self):
        _FindUser(self).find_user()
    
    def update_paitent(self):
        _UpdatePaitent(self).update_paitent()
