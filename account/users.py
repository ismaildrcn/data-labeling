from enum import Enum

class User:
    def __init__(self, **kwargs):
        self.username = kwargs.get("username")
        self.password = kwargs.get("password")

class Users(Enum):

    ismaildrcn = User(username="ismaildrcn", password="123456")


