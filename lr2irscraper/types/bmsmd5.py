from dataclasses import dataclass
import re


@dataclass()
class BmsMd5:
    hash: str

    def __post_init__(self):
        if re.match("^([0-9a-f]{32}|[0-9a-f]{160})$", self.hash) is None:
            raise ValueError("hash must be 32 or 160 hexadecimal digits: {}".format(self.hash))

    def __format__(self, _):
        return self.hash

    @property
    def type(self):
        return "bms" if len(self.hash) == 32 else "course"
