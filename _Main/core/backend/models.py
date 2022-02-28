from dataclasses import dataclass
from datetime import date
from typing import Optional, Union

from customtkinter import *

# from database import Database
# from .imagetk import get_image
# from .utils import Color, Defont

__all__ = (
    'Result',
    'Department',
    'Level',
    'Doctor',
    'User',
    'Paitent',
    'UserType',
    'PaitentType',
    'DoctorType',
)

UserType = Optional['User']
PaitentType = Optional['Paitent']
DoctorType = Optional['Doctor']


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


@dataclass(slots=True)
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


@dataclass(slots=True)
class Doctor:
    id: int
    name: str
    age: int
    department: Department
    degrees: str


@dataclass(slots=True)
class User:


    id: int
    name: str
    email: str
    _password: str
    _gender: int
    level: Level
    dob: str
    linked: UserType
    paitent: PaitentType

    @property
    def gender(self):
        return [None, 'Male', 'Female', 'Other'][self._gender]

@dataclass(slots=True)
class Paitent:
    id: int
    first_name: str
    last_name: str
    dob: date
    gender: str
    doctor: Doctor  # The doctor which is responsible for this paitent
    user: UserType

    @property
    def name(self):
        return ' '.join([self.first_name, self.last_name])


