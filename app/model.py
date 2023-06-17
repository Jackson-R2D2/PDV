import sqlite3
import asyncio
import aiosqlite

class DatabaseConnection:

    def __init__(self, db):
        self.connect = sqlite3.connect(db)
        self.cursor = self.connect.cursor()
        self.commit = self.connect.commit



class Table():

    database = DatabaseConnection('database/register.db')
    

    def create_table(self, campos):
        sql = f"CREATE TABLE IF NOT EXISTS {self.__class__.__name__.lower()} ({campos})"
        self.database.cursor.execute(sql)  


    def insert_values(self, columns, values):
        sql = f"INSERT INTO {self.__class__.__name__.lower()} {columns} VALUES {values}"
        self.database.cursor.execute(sql)
        self.database.commit()


    def all(self):
        sql = f"SELECT * FROM {self.__class__.__name__.lower()}"
        querys = self.database.cursor.execute(sql) 
        return querys.fetchall()  
    

    def get(self, **kwargs):
        identifier = Table.convert_kwargs_to_string(kwargs)
        sql = f"SELECT * FROM {self.__class__.__name__.lower()} WHERE {identifier}"
        querys = self.database.cursor.execute(sql)
        row = querys.fetchone()
        if row == None:
            raise TypeError
        return row


    def update(self, fields, values, **kwargs):
        identifier = Table.convert_kwargs_to_string(kwargs)
        sql = f"UPDATE {self.__class__.__name__} SET {fields} WHERE {identifier}"
        self.database.cursor.execute(sql, values)
        self.database.commit()

    
    def delete(self, **kwargs):
        identifier = Table.convert_kwargs_to_string(kwargs)
        sql = f"DELETE FROM {self.__class__.__name__} WHERE {identifier}"
        self.database.cursor.execute(sql)
        self.database.commit()

    
    @staticmethod
    async def async_all():
        db = await aiosqlite.connect('database/register.db')
        cursor = await db.execute('SELECT * FROM products')
        rows = await cursor.fetchall()
        return iter(rows)

    
    @staticmethod
    def convert_kwargs_to_string(kwargs):
        string = str()
        for key in kwargs:
            string += f'{key} = {kwargs[key]}'
        return string