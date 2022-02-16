from .base import Panel

__all__ = ('Admin', )

class Admin(Panel):
    level = 3

    def home(self):
        pass