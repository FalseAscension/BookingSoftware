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
        return dict(cursor.fetchone())

    def getUserByUUID(self, uuid):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM USERS WHERE UUID=?", (uuid,))
        return dict(cursor.fetchone())

    def updateUserTriesByUUID(self, uuid, tries, timestamp):
        cursor = self.connection.cursor()

        cursor.execute("UPDATE USERS SET incorrectTries=?, incorrectTime=? WHERE UUID=?", (tries,timestamp,uuid))
        return self.connection.commit()

    def getRooms(self):
        cursor = self.connection.cursor()

        rooms = []
        for r in cursor.execute("SELECT roomNo FROM rooms"):
            rooms.append(r[0])
        return rooms

    def getBookings(self, date):
        cursor = self.connection.cursor()

        bookings = []
        for b in cursor.execute("SELECT bookingID,byUser FROM bookings WHERE date=?", (date,)):
            bookings.append(dict(b))
        return bookings

if __name__ == "__main__":
    bdb = database("booking.db")
    user = bdb.getUserByEmail("emil.carr@protonmail.com")
    print(user.keys())
    for k in user.keys():
        print(user[k])
