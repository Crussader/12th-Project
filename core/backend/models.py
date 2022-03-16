from dataclasses import dataclass
from datetime import date, datetime
from typing import Optional, Union

from customtkinter import *

from core.backend.utils import token_decode

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
    'Update'
)

UserType = Optional['User']
PaitentType = Optional['Paitent']
DoctorType = Optional['Doctor']
Staff = Union[DoctorType, UserType]


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
class User:
    id: int
    name: str
    email: str
    _password: str
    level: Level
    _gender: int
    dob: date
    linked: UserType
    paitent: PaitentType

    @property
    def gender(self):
        return [None, 'Male', 'Female', 'Other'][self._gender]
    
    @property
    def password(self):
        pass_ =  token_decode(self._password, full=True)
        return pass_['key']
    
        
@dataclass(slots=True)
class Doctor:
    id: int
    name: str
    _dep: Department
    _extra: str
    user: User
    age: int

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

@dataclass(slots=True)
class Update:
    id: int
    from_id: int
    to_id: int
    text: str
    epoch: datetime
    is_system: bool
    read: bool
    replied: bool

    @property
    def how_long(self):
        def _approx(t):
            seconds = t.total_seconds()
            mins = seconds // 60
            hours = seconds // 3600
            days = seconds // 86400

            if mins <= 60:
                time = str(round(mins)) + ' mins ago'
            elif hours <= 48:
                time = str(round(hours)) + ' hours ago'
            else:
                time = str(round(days)) + ' days ago'
            
            return 'About {}'.format(time)

        now = datetime.utcnow()
        return _approx(now-self.epoch)

