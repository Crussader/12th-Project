from .base import Panel

__all__ = ('User', )

class User(Panel):
    level = 1

    def home(self):
        self.main.after(500, self._shortcut, self.main.frames['main'], 
                        'add-user.svg', '\nAdd User', 'Add a User Linked with you')
        self.main.after(800, self._shortcut, self.main.frames['main'],
                        'users.svg', '\nAll Users', 'See all the Users Connected with you')
        self.main.after(1000, self._shortcut, self.main.frames['main'],
                        'update-user.svg', '\nDoctor Updates', 'See the Updates from your Doctor')

