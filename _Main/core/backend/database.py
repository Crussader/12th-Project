"""
Database Structure for Hospital
|
├─ Users ─── (General Database of all Users that can be accesed by the Admin)
|           ├─ id (Primary Key)
|           ├─ name
|           ├─ email (if the same email is found then we will ask if we want to link it to them)
|           ├─ _password (ill use tokens so it will remain safe)
|           ├─ level (integer like 1, 2, 3 (user, doctor, admin))
|           ├─ gender (int 1, 2, 3 (Male, Female, Other))
|           ├─ dob (string)
|           ├─ linked_id (linked id if any)
├─ Paitents ────
|                ├─ id (Primary Key)
|                ├─ first_name
|                ├─ last_name
|                ├─ dob (DD/MM/YYYY/Age)
|                ├─ doctor_id (int)
|                ├─ user_id (`User` if there is one or else `DummyUser` is used)
├─ Doctor ────
|              ├─ id (Primary Key (Different one from users))
|              ├─ name
|              ├─ age
|              ├─ department
|              ├─ _extra (like degrees, etc.)
|              ├─ user_id

"""

from datetime import datetime, timedelta
from typing import Dict, Optional, Union

import mysql.connector as mysql
from mysql.connector.cursor import MySQLCursor

from .config import Config
from .models import *
from .utils import ThreadPool, decode


__all__ = ('Database',)

MYSQL = mysql.MySQLConnection


def table_exists(table=True, kwargs=True):  # checks if table or kwargs is not empty when calling a function
    def wrapper(func):
        def inner(*args, **kw):
            self, *other = args
            if table:
                if not (name := kw.get('table')):
                    if not isinstance(other, str):
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

    cache = {}

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
    def from_config(cls, table: str = ''):
        config = Config.load('database')
        _cls = cls(**config)
        if table:
            _cls._table = table

        return _cls

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

    def add_rec(self, table: Optional[str] = '', kwargs: Dict[str, str] = {}) -> bool:
        keys = ', '.join(kwargs.keys())
        values = ', '.join(['%s'] * len(kwargs))
        sql = f"INSERT INTO {table} ({keys}) VALUES ({values})"
        try:
            self.cursor.execute(sql, tuple(kwargs.values()))
        except mysql.IntegrityError: # if there is a duplicate
            return False
        else:
            self.cnx.commit()
            return True

    def _fetch_rec(self, id, table: str):
        rec = self.cache.get(id)
        if rec:
            return rec

        sql = 'select * from {} where id={}'.format(table, id) 
        self.cursor.execute(sql)
        _raw = self.cursor.fetchone()

        self.cache[id] = _raw
        return _raw

    def _try_fetching(self, param, table, search, raw):
        try:
            self.cursor.execute(param.format(table), (search,))
        except mysql.ProgrammingError as e:
            return None
        else:
            if (result := self.cursor.fetchall()) is not []:
                if raw:
                    return raw

                for res in result:
                    if table == 'paitents':
                        *other, doctor_id, user_id = res
                        result = Paitent(*other, None, None)

                        if user_id and not (user := self.cache.get(user_id)):
                            user = self._fetch_rec(user_id, table='users')
                            *other, _ = user
                            result.user = User(*other, result)
                        
                        if doctor_id and not (doctor := self.cache.get(doctor_id)):
                            doctor = self._fetch_rec(doctor_id, table='doctor')
                            result.doctor = Doctor(*doctor)

                    elif table == 'users':
                        *other, linked_id, paitent_id = res
                        result = User(*other, None, None)

                        if linked_id and not (linked := self.cache.get(linked_id)):
                            linked = self.find_rec(linked_id, 'LINKED_ID', table='users') # linked user is different
                            # result.linked = linked.one()
                            result.linked = ThreadPool.wait_result(linked).one()
                        
                        if paitent_id and not (paitent := self.cache.get(paitent_id)):
                            paitent = self.find_rec(paitent_id, 'ID', table='paitents')
                            result.paitent = ThreadPool.wait_result(paitent).one()

                    elif table == 'doctor':
                        result = Doctor(*res)

                return result

    @table_exists(kwargs=False)
    @ThreadPool.run_threaded()
    def find_rec(self, search: Union[str, int], filter_by: str = '', table: Optional[str] = '', raw=False):
        search_params = {
            "ID": "select * from {} where id = %s",
            "AGE": "select * from {} where age = %s",
            "LINKED_ID": 'select * from {} where linked_id = %s',
            "PAITENT_ID": 'select * from {} where paitent_id = %s',
            "FIRST_NAME": "select * from {} where first_name = %s",
            "LAST_NAME": "select * from {} where last_name = %s",
            "DEPARTMENT": "select * from {} where department = %s",
            "EMAIL": "select * from {} where email = %s",
        }

        if filter_by not in search_params.keys():
            raise ValueError("Invalid Filter (%s)" % (filter_by,))

        if isinstance(search, int):
            search_params = {k: v for k, v in search_params.items() if k in [
                'ID', 'AGE', 'LINKED_ID', 'PAITENT_ID']}
        elif isinstance(search, str):
            search_params = {k: v for k, v in search_params.items() if k not in [
                'ID', 'AGE', 'LINKED_ID', 'PAITENT_ID']}
        else:
            raise TypeError("Search Parameter must be an int or str")

        results = []

        if table=='users':
            if Config.load('app')['save_user_info']:
                cfg = Config.load('users', file='user')
                data = decode(cfg)
            

        if filter_by:
            result = self._try_fetching(search_params.get(filter_by), 
                                        table, search, raw)
            if result:
                results.append(result)
        else:
            for param in search_params.values():
                result = self._try_fetching(param, table, search, raw)

        ThreadPool.add(Result(results))

        
    @ThreadPool.run_threaded()
    def update_rec(self, id: str, table: Optional[str] = '', kwargs: Dict[str, str] = {}):
        update = ', '.join(f"{k}={v}" if isinstance(v, int) else f'{k}="{v}"'
                           if isinstance(v, str) else f'{k}=null'
                           for k, v in kwargs.items())

        sql = "UPDATE {} SET {} WHERE id = %s".format(table, update)
        
        self.cursor.execute(sql, (id, ))
        if self.cursor.rowcount:
            self.cnx.commit()  # commit only if there is rowcount
            return True        # so that would mean there was a change
            # then we can commit it to mysql
        else:
            return False

    @table_exists(kwargs=False)
    def delete_rec(self, id: int, verification_id: str, table: Optional[str] = ''):
        # check verification_id with the one the computer generated and the user recieved
        sql = "delete from {} where id=%s".format(table)
        self.cursor.execute(sql, (id, ))
        if self.cursor.rowcount:
            self.cnx.commit()

    def update_user(self, _from: int, _to: int, text: str):
        return self.add_rec('updates', 
               {'from_id': _from, 
                'to_id': _to, 
                'update_text': text,
                'epoch': datetime.utcnow()})

    def get_updates(self, id: int):

        self.cursor.execute("select * from updates where to_id=%s", (id, ))
        results = self.cursor.fetchall()
        if not results:
            return None
        else:
            return Result([Update(*i) for i in results])


    def close(self):
        self.cnx.close()


if __name__ == '__main__':
    db = Database.from_config()
    # # db.update_user(1228182, 128218232, 'new update')
    res = db.get_updates(128218232).data[-1]
    print(res)
    print(res.how_long)
