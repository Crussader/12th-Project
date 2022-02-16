from typing import Dict, Optional, Union

import mysql.connector as mysql
from mysql.connector.cursor import MySQLCursor

from .config import Config
from .models import *

__all__ = ('Database',)

MYSQL = mysql.MySQLConnection


def table_exists(table=True, kwargs=True):  # checks if table or kwargs is not empty when calling a function
    def wrapper(func):
        def inner(*args, **kw):
            self, *other = args
            if table:
                if not (name := kw.get('table')):
                    raise ValueError("No Table Name given")
                else:
                    kw.update({'table': name or self.table})

            if kwargs:
                if not kw.get('kwargs'):
                    raise ValueError("No Arguments given to add to Database")

            return func(self, *other, **kw)
        return inner
    return wrapper


class Database:

    def __init__(self, **kwargs):

        if not kwargs:
            raise ValueError("No Arguments given to connect to Database")

        self._database = kwargs.get('database', '')
        self._table = kwargs.pop('table', '')
        self.cnx: MYSQL = mysql.connect(**kwargs)
        self.cursor: MySQLCursor = self.cnx.cursor()

        if self.is_connected():
            print("connected!")

    @classmethod
    def from_config(cls):
        config = Config.load('database')
        return cls(**config)

    @property
    def table(self) -> str:
        return self._table

    @table.setter
    def table(self, other: str) -> str:
        if not isinstance(other, str):
            raise TypeError("Table name must be a string")

        self._table = other
        return self._table

    @property
    def database(self) -> str:
        return self._database

    @database.setter
    def database(self, other: str) -> str:
        if not isinstance(other, str):
            raise TypeError("Database name must be a string")

        if other == self._database:
            return self._database

        self.cursor.execute('use %s', (other, ))
        self._database = other
        return self._database

    def is_connected(self):
        return self.cnx.is_connected()

    @table_exists()
    def add_rec(self, table: Optional[str] = '', kwargs: Dict[str, str] = {}) -> bool:
        keys = ', '.join(kwargs.keys())
        values = ', '.join(['%s'] * len(kwargs))
        sql = f"INSERT INTO {table} ({keys}) VALUES ({values})"
        try:
            self.cursor.execute(sql, tuple(kwargs.values()))
        except mysql.IntegrityError:
            return False
        else:
            self.cnx.commit()
            if self.cursor.rowcount:
                return True
        return False

    @table_exists(kwargs=False)
    def find_rec(self, search: Union[str, int], filter_by: str = 'ID', table: Optional[str] = '', raw=False):
        search_params = {
            "ID": "select * from %s where id = %s",
            "AGE": "select * from %s where age = %s",
            "FIRST_NAME": "select * from %s where first_name = %s",
            "LAST_NAME": "select * from %s where last_name = %s",
            "DOCTOR_IN_CHARGE": "select * from %s where doctor_in_charge = %s",
            "DEPARTMENT": "select * from %s where department = %s",
            "EMAIL": "select * from %s where email = %s"
        }

        if filter_by not in search_params.keys():
            raise ValueError("Invalid Filter")

        if isinstance(search, int):
            search_params = {k: v for k, v in search_params.items() if k in [
                'ID', 'AGE']}
        elif isinstance(search, str):
            search_params = {k: v for k, v in search_params.items() if k not in [
                'ID', 'AGE']}
        else:
            raise TypeError("Search Parameter must be an int or str")

        results = []
        for param in search_params.values():
            try:
                self.cursor.execute(param, (table, search))
            except mysql.ProgrammingError:
                continue
            else:
                if (result := self.cursor.fetchall()) is not []:
                    if raw:
                        results.extend(result)
                        continue
                    for res in result:
                        if table == 'paitents':
                            *other, user_id = res
                            if user_id:
                                user = self.find_rec(
                                    user_id, filter_by="ID", table='users', raw=True)

                            result = Paitent(
                                *other, User(*user.one()) if user_id else DummyUser(None))
                        elif table == 'users':
                            result = User(*result)
                        elif table == 'staff':
                            result = Doctor(*result)

                        results.append(result)

        return Result(results)

    @table_exists()
    def update_rec(self, id: str, table: Optional[str] = '', kwargs: Dict[str, str] = {}):
        update = ', '.join(f"{k}={v}" if isinstance(v, int) else f'{k}="{v}"'
                           for k, v in kwargs.items())

        sql = "UPDATE %s SET %s WHERE id = %s"
        self.cursor.execute(sql, (table, update, id))
        if self.cursor.rowcount:
            self.cnx.commit()  # commit only if there is rowcount
            return True        # so that would mean there was a change
            # then we can commit it to mysql
        else:
            return False

    @table_exists(kwargs=False)
    def delete_rec(self, id: int, verification_id: str, table: Optional[str] = ''):
        # check verification_id with the one the computer generated and the user recieved
        sql = "delete from %s where id=%s"
        self.cursor.execute(sql, (table, id))
        if self.cursor.rowcount:
            self.cnx.commit()

    def close(self):
        self.cnx.close()


if __name__ == '__main__':

    # import timeit
    db = Database.from_config()
    # db.add_rec(table='paitents', kwargs={'id': 1, 'first_name': 'sai', 'last_name': 'krishina',
    #            'gender': 'male', 'age': 20, 'doctor_in_charge': 0, 'department': 0})
    # a = db.find_rec(1, table='paitents')
    # print(a)
    # print(timeit.timeit("db.find_rec(1, table='paitents')", globals=globals(),number=100))
