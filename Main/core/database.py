from typing import Optional, Dict, Union
import mysql.connector as mysql 
from mysql.connector.cursor import MySQLCursor
from config import Config

__all__ = ('Database',)

MYSQL = mysql.MySQLConnection

class Database:

    def __init__(self, from_config=True, **kwargs):

        if not from_config and not kwargs:
            raise ValueError("No Arguments given to connect to Database")
        
        if from_config:
            config = Config.load('database')
        else:
            config = kwargs
        
        self.cnx: MYSQL = mysql.connect(**config)
        self.cursor: MySQLCursor = self.cnx.cursor()

        self._database = config["database"]
        self._table = ""

    @property
    def table(self):
        return self._table
    
    @table.setter
    def table(self, other: str) -> str:
        if not isinstance(other, str):
            raise TypeError("Table name must be a string")

        self._table = other
        return self._table

    def is_connected(self):
        return self.cnx.is_connected()

    def add_rec(self, table: Optional[str]='', **kwargs: Dict[str, str]) -> int:

        table = table or self._table

        if not table:
            raise ValueError("No Table Name given")

        if not kwargs:
            raise ValueError("No Arguments given to add to Database")

        keys = ', '.join(kwargs.keys())
        values = ', '.join(['%s'] * len(kwargs))
        sql = f"INSERT INTO {table} ({keys}) VALUES ({values})"
        self.cursor.execute(sql, kwargs.values())
        self.cnx.commit()
    
    def find_rec(self, search: Union[str, int], filter_by: str, table: Optional[str]=''):
        
        search_params = {
            "ID": "select * from {} where id = %s".format(table),
            "AGE": "select * from {} where age = %s".format(table),
            "FIRST_NAME": "select * from {} where first_name = %s".format(table),
            "LAST_NAME": "select * from {} where last_name = %s".format(table),
            "DOCTOR_IN_CHARGE": "select * from {} where doctor_in_charge = %s".format(table),
            "DEPARTMENT": "select * from {} where department = %s".format(table),
        }
        table = table or self._table

        if not table:
            raise ValueError("No Table Name given")
        
        if filter_by not in search_params.values():
            raise ValueError("Invalid Filter")

        if isinstance(search, int):
            search_params = search_params[0: 2]
        elif isinstance(search, str):
            search_params = search_params[2: ]
        else:
            raise TypeError("Search Parameter must be an int or str")

        results = []
        
        for param in search_params in search_params:
            self.cursor.execute(param, (search,))
            if (result := self.cursor.fetchall()) not in [(), []]:
                results.append(result)
            
    
    def update_rec(self, id: str, table: Optional[str]='',**kwargs: Dict[str, str]):
        table = table or self._table

        if not table:
            raise ValueError("No Table Name given")
        
        if not kwargs:
            raise ValueError("No Arguments given to update in Database")

        keys = ', '.join(kwargs.keys())
        values = ', '.join(['%s'] * len(kwargs))
        sql = "UPDATE {} SET ({}) = ({}) where id = {}".format(table, keys, values, id)
        self.cursor.execute(sql, kwargs.values())
        self.cnx.commit()
        if self.cursor.rowcount:
            return True # check if the same row has the same values
                        # because if it does then .rowcount will be 0
                        # and that could be mean an error if not checked

        else:
            return False

    def delete_rec(self, id: int, verification_id: str):
        pass        

    def close(self):
        self.cnx.close()

if __name__ == '__main__':
    db = Database()
    # print(db)