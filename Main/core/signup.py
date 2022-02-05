from defaultentry import DefaultEntryText
from messagebox import MessageBox

__all__ = ('SignUp',)

class SignUp:

    def __init__(self):
        self.root = None
        self.main = None

    def _bind_movable_win(self):

        def start_move(e):
            self.root.x = e.x
            self.root.y = e.y
        
        def stop_move(e):
            self.root.x = None
            self.root.y = None
        
        def do_move(e):
            dx = e.x - self.root.x
            dy = e.y - self.root.y
            self.root.geometry(f"+{self.root.winfo_x() + dx}+{self.root.winfo_y() + dy}")

        values = tuple()
        for widget in values:
            widget.bind("<ButtonPress-1>", start_move)
            widget.bind("<ButtonRelease-1>", stop_move)
            widget.bind("<B1-Motion>", do_move)
        
    def check(self, fields):
        def try_again():
            self.root.deiconify()
            DefaultEntryText.set_defaults(*dict(fields).values())

        func = DefaultEntryText.get
        data = {k.strip('*'): func(v)[1].entry.get()
                if k != 'Date of Birth *' else func(v)[1] 
                for k, v in fields}

        if not all(data.values()):
            self.root.withdraw()
            MessageBox.error("The Following Fields are Empty\n"
                            f"{', '.join(k for k, v in data.items() if not v or v == 'DD/MM/YYYY/Age')}"
                            "\nPlease Fill them and try again", ok_cancel=True, 
                            yes_command=try_again, no_command=self.root.destroy)

        else:
            self.root.withdraw()
            MessageBox.info("ok_cancel",
                            "By Signing up, you Agree to our Terms and Conditions"
                            "of Use and Privacy Policy of Cadecous Hospital",
                            yes_command=self.root.destroy, # move on
                            no_command=self.root.deiconify # return to sign up page
                            )

        # Data Base check to make sure there arent duplicates as in
        # Name, Email, Username
        # if there are duplicates, then the user will be asked to try again

        # then update the database with the new user
        # run the loading screen to the main window

        if self.main is None:
            raise TypeError("Main is None.")

    def sign_up(self):
        raise NotImplementedError
        # same reason for login.py

