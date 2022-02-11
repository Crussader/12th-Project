from dataclasses import dataclass

from ..imagetk import get_image

__all__ = (
    'Result',
    'Department',
    'Level',
    'Doctor',
    'User',
    'DummyUser',
    'Paitent'
)


@dataclass
class Result:
    data: list

    @property
    def is_empty(self):
        return len(self.data) == 0

    def one(self, index=0):
        return self.data[index]

    def many(self, limit=5):
        return self.data[:limit+1]

    def all(self):
        return self.data


@dataclass
class Department:
    deps = {
        0: "",
        1: "Anesthetics",
        2: "Breast Screening",
        3: "Cardiology",
        4: "Ear, nose and throat (ENT)",
        5: "Elderly services department",
        6: "Gastroenterology",
        7: "General Surgery",
        8: "Gynecology",
        9: "Hematology",
        10: "Neonatal Unit",
        11: "Neurology",
        12: "Nutrition",
        13: "Obstetrics",
        14: "Gynecology",
        15: "Oncology",
        16: "Ophthalmology",
        17: "Orthopedics",
        18: "Physiotherapy",
        19: "Renal Unit",
        20: "Sexual Health",
        21: "Urology"
    }

    @classmethod
    def get(cls, id: int):
        if 0 > id > 21:
            raise ValueError(
                "Value is greater than 21, must be within 0 and 21 (got: %s)" % id)

        return cls.deps.get(id)

    dep: get


@dataclass
class Level:

    @classmethod
    def get_level(cls, lvl: int) -> str:
        levels = {
            0: 'USER',
            1: 'DOCTOR',
            2: 'ADMIN',
            3: 'MASTER'
        }
        return levels.get(lvl, 0)  # defaults makes it an user

    lvl: get_level


@dataclass
class Doctor:
    id: int
    name: str
    age: int
    department: Department
    degrees: str


@dataclass
class User:
    user_id: int
    name: str
    password: str
    email: str
    level: Level
    _display_picture: str

    def __repr__(self):
        return f"User(name={self.name} level={self.level} dp={self._display_picture})"

    @property
    def display_picture(self):
        return get_image(self._display_picture)

    dp = display_picture  # an alias so user.dp can also be done


@dataclass
class DummyUser:
    """A Dummy Class in the case user_id is none"""
    user: str


@dataclass
class Paitent:
    id: int
    first_name: str
    last_name: str
    age: int
    gender: str
    doctor_id: int  # The doctor which is responsible for this paitent
    department: Department
    user: User

    @property
    def name(self):
        return ' '.join([self.first_name, self.last_name])
