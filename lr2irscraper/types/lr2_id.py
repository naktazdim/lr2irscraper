from dataclasses import dataclass


@dataclass()
class Lr2Id:
    type: str
    id: int

    def __post_init__(self):
        if self.type not in ["bms", "course"]:
            raise ValueError("lr2 id type must be 'bms' or 'course': {}".format(self.type))
        if self.id <= 0:
            raise ValueError("lr2 id must be positive integer: {}".format(self.id))

