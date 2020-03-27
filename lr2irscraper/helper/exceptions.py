from typing import Union


class ParseError(Exception):
    def __init__(self, message: str):
        self.message = message

    def __str__(self):
        return self.message


class UnregisteredError(Exception):
    def __init__(self, id_or_hash: Union[int, str], kind: str):
        self.id_or_hash = id_or_hash
        self.kind = kind

    def __str__(self):
        return "{}: unregistered {}".format(self.id_or_hash, self.kind)
