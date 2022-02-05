import mysql.connector as mysql 
from mysql.connector.cursor import MySQLCursor

class Database:

    def __init__(self, from_config=True, **kwargs):

        if not from_config and not kwargs:
            raise ValueError("No Arguments given to connect to Database")
        
        if from_config:
            pass

        else:
            pass

        # self.cnx = mysql.connect()
