from model import Table

class Products(Table):
    
    def __init__(self):
        self.create_table("id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, price INTEGER NOT NULL, amount INTEGER, type TEXT")