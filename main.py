import sqlite3


class Database:
    def __init__(self, db_file):
        self.db = sqlite3.connect(db_file)
        self.cursor = self.db.cursor()

    def create_table(self):
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS name_and_token(
            user_id INTEGER,
            name TEXT,
            token TEXT,
            flag INTEGER
        )""")
        self.db.commit()

    def add_user(self, user_id, user_name, user_token):
        counter = 0
        with self.db:
            self.cursor.execute("SELECT * FROM name_and_token WHERE user_id=?", (user_id, ))
            if self.cursor.fetchone() is None:
                counter += 1
                self.cursor.execute("INSERT INTO name_and_token VALUES(?, ?, ?, ?)",
                                    (user_id, user_name, user_token, 0, ))
                self.db.commit()
        return counter

    def delete_user(self, user_id):
        self.cursor.execute('DELETE FROM name_and_token WHERE user_id = ?', (user_id,))
        self.db.commit()

    def get_token(self, user_id):
        counter = 0
        self.cursor.execute("SELECT * FROM name_and_token")
        records = self.cursor.fetchall()
        for row in records:
            counter += 1
            if user_id == row[0]:
                return row[2]
            if counter > len(records):
                return counter

    def user_presence(self, user_id):
        self.cursor.execute("SELECT user_id FROM name_and_token")  # cursor позволяет делать запросы к БД
        records = self.cursor.fetchall()
        for row in records:
            if user_id == row[0]:
                return True
        return False

    def enable_alert_for_user(self, token):
        self.cursor.execute('UPDATE name_and_token SET flag = 1 WHERE token = ?', (token, ))
        self.db.commit()

    def turn_off_alert(self, token):
        self.cursor.execute('UPDATE name_and_token SET flag = 0 WHERE token = ?', (token, ))
        self.db.commit()

    def check_alert_user(self, token):
        self.cursor.execute("SELECT token FROM name_and_token WHERE flag = 1")
        records = self.cursor.fetchall()
        for row in records:
            if row[0] == token:
                return True
        return False
