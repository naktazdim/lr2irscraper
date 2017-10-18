# -*- coding: utf-8 -*-
from typing import Union


class ParseError(Exception):
    pass


class UnregisteredError(Exception):
    def __init__(self, id_or_hash: Union[int, str], kind: str):
        self.id_or_hash = id_or_hash
        self.kind = kind

    def __str__(self):
        return "{}: unregistered {}".format(self.id_or_hash, self.kind)


class RankingChangedError(Exception):
    pass
