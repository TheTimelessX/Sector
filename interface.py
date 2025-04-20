import json
from typing import Literal

codes = Literal['OK', 'ERROR']

class User(object):
    def __init__(self, user_results: tuple = ()):
        self.ur = user_results
        if len(self.ur) > 0:
            self.uid: int = self.ur[0]
            self.file_ids: list[str] = json.loads(self.ur[1])
            self.verified: bool = True if self.ur[2] == 1 else False
        else:
            self.uid: int = 0
            self.file_ids: list[str] = []
            self.verified: bool = False

class UserResponse(object):
    def __init__(self, results: dict = {}):
        self.status: codes = results.get("status", "ERROR")
        self.user: User = User(results.get("user", ()))
        self.__ = results

    def __str__(self):
        return json.dumps(self.__, indent=2)