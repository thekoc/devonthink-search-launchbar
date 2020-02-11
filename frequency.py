import sqlite3
import os
from launchbar import LaunchBar

class Frequency:
    def __init__(self):
        self.sql_path = os.path.join(LaunchBar.support_path(), 'frequency.db')
        self.connection = sqlite3.connect(self.sql_path)
        cursor = self.connection.cursor()
        cursor.execute("create table if not exists frequency (uuid text primary key, picked integer default 0, appeared integer default 0)")
        self.connection.commit()

    def update_frequency(self, picked_uuid, candidate_uuids):    
        cursor = self.connection.cursor()
        cursor.executemany(
            'insert or ignore into frequency (uuid) values (?)',
            ((uuid,) for uuid in candidate_uuids)
        )
        cursor.executemany(
            'update frequency set appeared = appeared + 1 where uuid = ?',
            ((uuid,) for uuid in candidate_uuids))

        cursor.execute(
            'insert or ignore into frequency (uuid) values (?)', (picked_uuid,)
        )
        cursor.execute(
            'update frequency set picked = picked + 1 where uuid = ?', (picked_uuid,))
        self.connection.commit()

    def get_frequency(self, uuid):
        cursor = self.connection.cursor()
        cursor.execute('select picked, appeared from frequency where uuid = ?', (uuid,))
        one = cursor.fetchone()
        if one:
            picked, appeared = one
            return picked / appeared
        else:
            return None

            


if __name__ == "__main__":
    f = Frequency()
    f.update_frequency('234', '123 234 345'.split())
    print(f.get_frequency('123'))