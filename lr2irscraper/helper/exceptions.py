from lr2irscraper.types import BmsMd5


class ParseError(Exception):
    def __init__(self, message: str):
        self.message = message

    def __str__(self):
        return self.message


class UnregisteredError(Exception):
    def __init__(self, bmsmd5: BmsMd5):
        self.bmsmd5 = bmsmd5

    def __str__(self):
        return "unregistered bmsmd5: {}".format(self.bmsmd5.hash)
