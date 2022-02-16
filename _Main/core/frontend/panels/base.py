from customtkinter import *
from ...backend.utils import Color, Defont
from ...backend.imagetk import get_image


class Panel:
    level = 0

    def _shortcut(self, master: CTkFrame, image: str, text: str, sub_text: str):
        frame = CTkFrame(master)
        CTkFrame(frame, height=50, fg_color=Color.FRAME_2).pack(pady=20)
        short = CTkButton(frame, text=text, fg_color=Color.FRAME_2, 
                          compound="top", image=get_image(image),
                          hover=False, text_font=Defont.add(20))
        short.pack(pady=5, padx=20)
        CTkLabel(frame, text=sub_text, width=350, fg_color=Color.FRAME_2,
                 text_font=Defont.add(11), text_color="lightgrey").pack(pady=10)
        CTkFrame(frame, height=50, fg_color=Color.FRAME_2).pack(pady=20)
        frame.pack(side="left", padx=90)

    def __init__(self, main):
        self.main = main

    def __eq__(self, __o: object) -> bool:
        if not isinstance(__o, int):
            raise TypeError(f"{type(__o)} can not be compared with {self.__class__.__name__}")
        
        return self.level == __o
    
    def __ne__(self, __o: object) -> bool:
        if not isinstance(__o, int):
            raise TypeError(f"{type(__o)} can not be compared with {self.__class__.__name__}")
        

        return self.level != __o
    
    def __ge__(self, __o: int) -> bool:
        if not isinstance(__o, int):
            raise TypeError(f"{type(__o)} can not be compared with {self.__class__.__name__}")

        return __o >= self.level
    
    def __gt__(self, __o: int) -> bool:
        if not isinstance(__o, int):
            raise TypeError(f"{type(__o)} can not be compared with {self.__class__.__name__}")
        
        return __o > self.level

    def __le__(self, __o: int) -> bool:
        if not isinstance(__o, int):
            raise TypeError(f"{type(__o)} can not be compared with {self.__class__.__name__}")
        
        return __o <= self.level
    
    def __lt__(self, __o: int) -> bool:
        if not isinstance(__o, int):
            raise TypeError(f"{type(__o)} can not be compared with {self.__class__.__name__}")
        
        return __o < self.level
    
    def home(self):
        raise NotImplementedError
    
    def load_tab(self):
        tab = self.main.frames["tab"]

        if self > 1:
            add_user = CTkButton(tab, image=get_image("add-user.svg", wh=0.1), 
                                text='', fg_color=Color.FRAME, width=70, height=60, 
                                hover_color=Color.LABEL_BG, compound='right',
                                command=lambda: self.main._set_and_run(add_user, "add_user"))
            add_user.pack(pady=20)

            find_user = CTkButton(tab, image=get_image("find-user.svg", wh=0.1),
                                text='', fg_color=Color.FRAME, width=70, height=60, hover_color=Color.LABEL_BG,
                                command=lambda: self.main._set_and_run(find_user, "find_user"))
            find_user.pack(pady=20)

        if self >= 1:
            if self == 1:
                users = CTkButton(tab, image=get_image("users.svg", wh=0.1),
                                text='', fg_color=Color.FRAME, width=70, height=60, hover_color=Color.LABEL_BG,
                                command=lambda: self.main._set_and_run(users, "users"))
                users.pack(pady=20)
            update_user = CTkButton(tab, image=get_image("update-user.svg", wh=0.1),
                                text='', fg_color=Color.FRAME, width=70, height=60, hover_color=Color.LABEL_BG,
                                command=lambda: self.main._set_and_run(update_user, "update_user"))
            update_user.pack(pady=20)

        if self == 3:
            delete_user = CTkButton(tab, image=get_image("remove-user.svg", wh=0.1),
                                    text='', fg_color=Color.FRAME, width=70, height=60, hover_color=Color.LABEL_BG, 
                                    command=lambda: self.main._set_and_run(delete_user, "delete_user"))
            delete_user.pack(pady=20)