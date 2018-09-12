import sqlite3

class database():

    def __init__(self, filename):
        self.connection = sqlite3.connect(filename)
        self.connection.row_factory = sqlite3.Row
    
    def close(self):
        self.connection.close()
    
    def getUserByEmail(self, email):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM USERS WHERE email=?", (email,))
        return cursor.fetchone()

    def getUserByUUID(self, uuid):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM USERS WHERE UUID=?", (uuid,))
        return cursor.fetchone()

if __name__ == "__main__":
    bdb = database("booking.db")
    user = bdb.getUserByEmail("emil.carr@protonmail.com")
    print(user.keys())
    for k in user.keys():
        print(user[k])
