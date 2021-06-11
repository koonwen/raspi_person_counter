import sqlite3
import time

class DatabaseDriver:
    '''
    Database driver for connecting to our DB,
    pushing photos to the DB and getting data
    '''
    def __init__(self):
        self.conn = sqlite3.connect("Model/photos.db", check_same_thread=False)
        self.c = self.conn.cursor() #TODO WHAT IS A CURSOR?

    def create_table(self):
        """To create our table"""
        try:
            self.c.execute("""
                CREATE TABLE info (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                number_ppl INTEGER,
                time TEXT NOT NULL,
                date TEXT NOT NULL
                )
            """)
            self.conn.commit()
            return ("table successfully created")
        except Exception:
            return("table has already been created")

    def add_data(self, num):
        """
        :param num: number of people in image
        -> (string) success/failure response message
        """
        current_time = time.strftime("%X")
        date = time.strftime("%x")
        try:
            self.c.execute("INSERT INTO info (number_ppl, time, date) VALUES (:number_ppl, :time, :date)"
                           ,{"number_ppl": num, "time": current_time, "date": date })
            self.conn.commit()
            return "<successfully added: {}>".format(num)
        except:
            return "error"

    def find(self, id):
        """id:(integer) -> (dict) row specified by id"""
        self.c.execute("SELECT * FROM info WHERE id = ?", (id,))
        row = self.c.fetchone()
        if row == None:
            return None
        else:
            format = {
                "id": row[0],
                "number_ppl": row[1],
                "time": row[2],
                "date": row[3]
            }
            return format

    def get_all(self):
        """returns all entries in database (dict)"""
        table = self.c.execute("SELECT * FROM info")
        store = []
        for row in table:
            temp = {
                "id": row[0],
                "number_ppl":row[1],
                "time":row[2],
                "date":row[3]
            }
            store.append(temp)
        return store

    def get_most_recent(self, n):
        """n:(integer) -> (dict list) n most recent entries"""
        cursor = self.c.execute("SELECT * FROM info ORDER BY id DESC LIMIT ?", (n,))
        store = []
        for row in cursor:
            temp = {
                "id": row[0],
                "number_ppl":row[1],
                "time":row[2],
                "date":row[3]
            }
            store.append(temp)
        return store

    def delete(self, id):
        """
        id:(integer) -> (string) success/failure response message"""
        temp = self.find(id)
        if temp == None:
            return "Failed to delete, No id found!"
        else:
            self.c.execute("DELETE FROM info WHERE id = ?",(id,))
            self.conn.commit()
            return "Deleted : {}".format(temp)

    def drop_table(self):
        try:
            self.c.execute("DROP TABLE info")
            return "table dropped!"
        except Exception:
            return "Error, table not found"

# For testing purposes
# if __name__ == "__main__":
#     db = DatabaseDriver()
#     db.conn.close()
