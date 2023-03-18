
class WrongOption(Exception):
    def __init__(self):
        self.message = "This option doesn't exist."
        super().__init__(self.message)