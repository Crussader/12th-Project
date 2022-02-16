from tkinter import ttk
from typing import Tuple, Union, Dict
from customtkinter import CTkLabel

__all__ = ('DefaultEntryText',)


class DefaultEntryText:

    entires: Dict[str, 'DefaultEntryText'] = {}

    @classmethod
    def add(cls, entry: ttk.Entry, default_text: str = '',
            name: str = '', mode: str = '', **kwargs) -> 'DefaultEntryText':

        if entry in cls.entires.values():
            return

        if not isinstance(entry, ttk.Entry):
            raise TypeError(
                f"Expected {type(ttk.Entry)} but got {type(entry)}")

        name = name or entry.winfo_name()
        ret = cls(default_text, entry, mode, **kwargs)
        cls.entires[name] = ret
        return ret

    @classmethod
    def get(cls, entry_or_name,
            reset: bool = True) -> Tuple[str, Union['DefaultEntryText', None]]:

        if isinstance(entry_or_name, cls):
            for k, v in cls.entires:
                if v == entry_or_name:
                    return k, v
            return None

        elif isinstance(entry_or_name, str):
            if 'dob' in entry_or_name:
                base = '.'.join(entry_or_name.split('.')[:2])
                dob = '/'.join(cls.entires[base + v].entry.get()
                               for v in ('.day', '.month', '.year', '.age'))
                return entry_or_name, dob

            value = cls.entires.get(entry_or_name)
            if reset:
                if value.entry.get() == value.text:
                    value.entry.delete(0, 'end')

            return entry_or_name, value

    @classmethod
    def set_defaults(cls, *entries: Union[str, 'DefaultEntryText']):
        print(entries)
        if not entries:
            for k, v in cls.entires.items():
                v.set_default()
        else:

            for entry in entries:
                if isinstance(entry, str):
                    try:
                        cls.entires.get(entry).set_default()
                    except AttributeError:
                        continue
                elif isinstance(entry, ttk.Entry):
                    entry.set_default()

    def __init__(self, text: str, entry: ttk.Entry, mode: str = '',
                 label=None, enter_command=None, name=None):
        self.text = text
        self.entry = entry
        self.mode = mode
        self.label = label

        if enter_command and callable(enter_command):
            if (count := enter_command.__code__.co_argcount) != 1:
                raise ValueError(f"Expected 1 argument: (got {count})")

        elif enter_command and (not callable(enter_command)):
            raise TypeError(
                f"Expected a Callable but got: {type(enter_command)}")

        self.enter_command = enter_command

        if name is not None:
            self.entires[name] = self

    def handle_in(self, _=''):
        if self.entry.get() == self.text:
            self.entry.delete(0, 'end')
            self.entry.configure(foreground="",
                                 show="*" if self.mode == "password" else '')
        if "invalid" in self.entry.state():
            self.entry.state(["!invalid"])
            if self.label:
                if isinstance(self.label, CTkLabel):
                    self.label.set_text(" ")

    def handle_out(self, _=''):
        if not self.entry.get():
            self.entry.insert(0, self.text)
            self.entry.configure(foreground="grey", show="")

    def handle_enter(self, _=''):
        self.enter = self.entry.get()

    def set_default(self):
        self.entry.delete(0, 'end')
        self.entry.insert(0, self.text)
        self.entry.config(foreground='grey', show='')

    def bind(self):
        self.handle_out()
        self.entry.bind("<FocusIn>", self.handle_in)
        self.entry.bind("<FocusOut>", self.handle_out)
        if self.enter_command:
            command = self.enter_command
        command = self.handle_enter
        self.entry.bind("<Return>", command)