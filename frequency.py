#!/usr/bin/python3

import sqlite3
import os
from launchbar import LaunchBar
from config import UserConfig

CONSTANT_A = UserConfig.a
CONSTANT_B = UserConfig.b

class Frequency:
    def __init__(self):
        self.sql_path = os.path.join(LaunchBar.support_path(), 'frequency.db')
        self.connection = sqlite3.connect(self.sql_path)
        cursor = self.connection.cursor()
        cursor.execute("create table if not exists frequency (uuid text primary key, score integer default 0)")
        self.connection.commit()

    def update_frequency(self, picked_uuid, candidate_uuids):
        """This is not strict frequency but "frequency score"

        The "frequency score" is calculated by `old_value * a + is_chosen * (1-a)` where 0 < a < 1
        
        Arguments:
            picked_uuid {str} -- The uuid of the chosen item
            candidate_uuids {list} -- The candidate uuids
        """
        a = CONSTANT_A
        b = CONSTANT_B
        cursor = self.connection.cursor()
        cursor.executemany(
            'insert or ignore into frequency (uuid) values (?)',
            ((uuid,) for uuid in candidate_uuids)
        )
        not_chosen = set(candidate_uuids) - set([picked_uuid])

        cursor.executemany(
            'update frequency set score = score * ? where uuid = ?',
            ((a, uuid,) for uuid in not_chosen))

        cursor.executemany(
            'update frequency set score = ? where uuid = ? and 0 < score and score < ?',
            ((b, uuid, b) for uuid in not_chosen))
        
        picked_score = self.get_frequency(picked_uuid)
        if picked_score == 0:
            cursor.execute(
                'update frequency set score = ? where uuid = ?', (b, picked_uuid,))
        else:
            cursor.execute(
                'update frequency set score = score * ? + ? where uuid = ?', (a, 1 - a, picked_uuid,))
        self.connection.commit()

    def get_frequency(self, uuid):
        cursor = self.connection.cursor()
        cursor.execute('select score from frequency where uuid = ?', (uuid,))
        one = cursor.fetchone()
        if one:
            score = one[0]
            return score
        else:
            return None

            


if __name__ == "__main__":
    f = Frequency()
    f.update_frequency('234', '123 234 345'.split())
    print(f.get_frequency('123'))