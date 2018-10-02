import sqlite3,json

class database():

    def __init__(self, filename):
        self.connection = sqlite3.connect(filename)
        self.connection.row_factory = sqlite3.Row

    def close(self):
        self.connection.close()

    def getUserByEmail(self, email):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM USERS WHERE email=?", (email,))
        return dict(cursor.fetchone())

    def getUserByUUID(self, uuid):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM USERS WHERE UUID=?", (uuid,))
        return dict(cursor.fetchone())

    def updateUserTriesByUUID(self, uuid, tries, timestamp):
        cursor = self.connection.cursor()

        cursor.execute("UPDATE USERS SET incorrectTries=?, incorrectTime=? WHERE UUID=?", (tries,timestamp,uuid))
        return self.connection.commit()

    def getSettings(self):
        cursor = self.connection.cursor()

        settings = {}
        for s in cursor.execute("SELECT name,value FROM settings"):
            settings[s['name']] = json.loads(s['value'])
        return settings

    def getBookings(self, date):
        cursor = self.connection.cursor()

        bookings = []
        for b in cursor.execute("SELECT bookingID,time,byUser FROM bookings WHERE date=?", (date,)):
            bookings.append(dict(b))

        return bookings

if __name__ == "__main__":
    bdb = database("booking.db")
    user = bdb.getUserByEmail("emil.carr@protonmail.com")
    print(user.keys())
    for k in user.keys():
        print(user[k])
