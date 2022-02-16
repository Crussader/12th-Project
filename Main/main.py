from tkinter import ttk
import tksvg
from turtle import width
from core import *
from typing import Dict

__version__ = "0.4"

class Main(CTk):
    APPNAME = "Caduceus Hospital"
    frames: Dict[str, CTkFrame] = {}
    current = None
    panel: Panel = None

    def __init__(self, panel):

        self.panel = panel(self)

        super().__init__(self.APPNAME)
        self.state('zoomed')
        self.configure(fg_color=None)
        load_theme(self)
        tksvg.load(self)
        self.load_home()


    def _set_and_run(self, button: CTkButton, func: str):
        button.configure(fg_color=Color.LABEL_BG)
        if self.current:
            self.after(10)
            self.current.configure(fg_color=Color.FRAME)
        self.current = button

    def _expand(self, frame: CTkFrame, i: int=0, max = 300):
        frame.pack_configure(side='right', anchor="ne", padx=10, pady=10, ipadx=i)
        if i <= max:
            self.after(10, self._expand, frame, i+1)

    def load_home(self):

        tab = CTkFrame(self, width=70)
        self.frames['tab'] = tab

        logo = get_image('icon.png', basic=True)
        logo_l = CTkLabel(tab, image=logo, width=70, height=50,
                          fg_color=None)
        logo_l.image = logo
        logo_l.pack(pady=15, padx=5)

        CTkLabel(tab, text=self.APPNAME.split()[0], text_color=Color.CHECKBOX_LINES, 
                 text_font=Defont.add(12), width=100, fg_color=None).pack()
        
        ttk.Separator(tab).pack(fill='x', padx=5, pady=10)

        CTkFrame(tab, fg_color=Color.FRAME, width=70, height=125).pack(pady=5) # seperator


        profile = CTkFrame(self, width=200, height=70)
        pfp = CTkButton(profile, image=get_image('user.svg', wh=0.1), 
                        width=100, height=70, hover_color=Color.FRAME,
                        fg_color=Color.FRAME, compound='right', text='')
        pfp.pack(padx=5, pady=10, side='right')
        
        CTkLabel(profile, text='Logged in as', text_font=Defont.add(10), 
                 text_color=Color.ENTRY, fg_color=None, width=100).place(relx=.14, rely=.2)
        CTkLabel(profile, text='Parikshit Rao', text_font=Defont.add(11),
                 fg_color=None).place(relx=.1, rely=.45)
        my_profile = CTkButton(profile, text='My Profile', text_font=Defont.add(8),
                               width=30, height=20, fg_color=None, hover=False)
        # bind hover to profile win
        my_profile.place(relx=.1, rely=.73)
        log_out = CTkButton(profile, text='Log out', text_font=Defont.add(8),
                            width=30, height=20, fg_color=None, hover=False)
        # bind hover to logout
        log_out.place(relx=.34, rely=.73)

        home = CTkButton(tab, image=get_image('home.svg', wh=0.08), text='',
                         fg_color=Color.LABEL_BG, width=70, height=50,
                         hover_color=Color.LABEL_BG,
                         command=lambda: self._set_and_run(home, 'home_page'))
        self.current = home
        home.pack(pady=20)

        self.panel.load_tab()

        CTkLabel(tab, text=f'V {__version__}', text_color=Color.LABEL_BG, 
                 fg_color=None, width=50, text_font=Defont.add(10)).pack(side='bottom', pady=10)


        settings = CTkButton(tab, image=get_image("settings.svg", wh=0.1),
                             text='', fg_color=Color.FRAME, width=70, height=60, hover_color=Color.LABEL_BG,
                             command=lambda: self._set_and_run(settings, "settings"))
        settings.pack(pady=10, side='bottom')


        profile.pack(side='right', anchor="ne", padx=10, pady=10, ipadx=70)
        # self.after(2000, self._expand, profile, 7)

        self.home()

        tab.pack(anchor='w', fill="y", expand=True, 
                 side="left", pady=10, padx=10)
    
    def home(self):
        
        main_win = CTkFrame(self, width=500, height=500)
        self.frames['main'] = main_win

        question = CTkLabel(main_win, text_font=Defont.add(30),
                            height=50, width=700, text="What would you like to do today?",
                            fg_color=Color.FRAME)
        question.pack(pady=20)

        self.panel.home()
        # if panel in ["admin", "doctor"]:

        #     self.after(500, self._shortcut, main_win, 'add-user.svg',
        #                "\nAdd Patient", "Add a Patient to Database")

        #     self.after(800, self._shortcut, main_win, "find-user.svg",
        #                "\nFind Patient", "Find a Paitent from Database")

        #     self.after(1000, self._shortcut, main_win, "update-user.svg",
        #                "\nUpdate Paitent", "Update Paitent Records")

        main_win.place(relx=0.1, rely=0.15,
                       relheight=0.8, relwidth=0.85)



# Main('admin').mainloop()
if __name__ == "__main__":
    # app = Main(User)
    # app.mainloop()
    loading_screen(None)
