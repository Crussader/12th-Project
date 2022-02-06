from typing import Optional, Dict, Union
import mysql.connector as mysql 
from mysql.connector.cursor import MySQLCursor
from config import Config

__all__ = ('Database',)

MYSQL = mysql.MySQLConnection

def exists(table=True, kwargs=True): # checks if table or kwargs is not empty when calling a function
    def wrapper(func):
        def inner(*args, **kwargs):
            self, *other = args
            if table:
                if not (name:=kwargs.get('table')):
                    raise ValueError("No Table Name given")
                else:
                    kwargs.update({'table': name or self.table})
            
            if kwargs:
                if not kwargs.get('kwargs'):
                    raise ValueError("No Arguments given to add to Database")

            return func(self, *other)
        return inner
    return wrapper

class Database:

    def __init__(self, from_config=True, **kwargs):

        if not from_config and not kwargs:
            raise ValueError("No Arguments given to connect to Database")
        
        if from_config:
            config = Config.load('database')
        else:
            config = kwargs
        
        self._database = config.get('database', '')
        self._table = config.pop('table', '')
        self.cnx: MYSQL = mysql.connect(**config)
        self.cursor: MySQLCursor = self.cnx.cursor()
        
        if self.is_connected():
            print("connected!")

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

    @exists()
    def add_rec(self, table: Optional[str]='', kwargs: Dict[str, str] = {}) -> int:
        keys = ', '.join(kwargs.keys())
        values = ', '.join(['%s'] * len(kwargs))
        sql = f"INSERT INTO {table} ({keys}) VALUES ({values})"
        self.cursor.execute(sql, tuple(kwargs.values()))
        self.cnx.commit()
    
    @exists(kwargs=False)
    def find_rec(self, search: Union[str, int], filter_by: str, table: Optional[str]=''):
        search_params = {
            "ID": "select * from {} where id = %s".format(table),
            "AGE": "select * from {} where age = %s".format(table),
            "FIRST_NAME": "select * from {} where first_name = %s".format(table),
            "LAST_NAME": "select * from {} where last_name = %s".format(table),
            "DOCTOR_IN_CHARGE": "select * from {} where doctor_in_charge = %s".format(table),
            "DEPARTMENT": "select * from {} where department = %s".format(table),
        }
        
        if filter_by not in search_params.keys():
            raise ValueError("Invalid Filter")

        if isinstance(search, int):
            search_params = {k: v for k, v in search_params.items() if k in ['ID', 'AGE']}
        elif isinstance(search, str):
            search_params = {k: v for k, v in search_params.items() if k not in ['ID', 'AGE']}
        else:
            raise TypeError("Search Parameter must be an int or str")

        results = []
        
        for param in search_params.values():
            self.cursor.execute(param, (search,))
            if (result := self.cursor.fetchall()) not in [(), []]:
                results.append(result)
        
        return results
    
    @exists()
    def update_rec(self, id: str, table: Optional[str]='', kwargs: Dict[str, str]={}):
        update = ', '.join(f"{k}={v}" if isinstance(v, int) else f'{k}="{v}"'
                           for k, v in kwargs.items())

        sql = """UPDATE {} SET {} WHERE id = {}""".format(table, update, id)
        self.cursor.execute(sql)
        if self.cursor.rowcount:
            self.cnx.commit() # commit only if there is rowcount
                              # so that would mean there was a change
                              # then we can commit it to mysql
            return True

        else:
            return False

    @exists(kwargs=False)
    def delete_rec(self, id: int, verification_id: str, table: Optional[str]=''):
        # check verification_id with the one the computer generated and the user recieved
        sql = "delete from {} where id={}".format(table, id)

    def close(self):
        self.cnx.close()

if __name__ == '__main__':
    db = Database(from_config=False, host="localhost", password='panipuri123*', user='root', database='hospital')
    # db.add_rec('paitents', {'id': 1, 'first_name': 'sai', 'last_name': 'krishina'})
    db.update_rec(1, 'paitents', {'gender': 'male', 'age': 20, 'doctor_in_charge': 123})
    a = db.find_rec(1, "ID", 'paitents')
    print(a)

    # print(db)