#!/usr/bin/python3

import os
import sqlite3
from datetime import datetime
from multiprocessing.dummy import Pool as ThreadPool

from launchbar import LaunchBar


DB_PATH = os.path.join(LaunchBar.support_path(), 'cache.db')

def _get_or_fetch_map(x):
    return Cache().get_or_fetch(x[0], x[1])

class Cache:
    def __init__(self):
        self.connection = sqlite3.connect(DB_PATH, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
    
    def cache_record(self, record, commit=True):
        return self.cache_records((record,), commit)
    
    def cache_records(self, records, commit=True):
        fields = ('uuid', 'name', 'filename', 'path', 'location', 'type', 'kind', 'thumbnail')
        new_records = []
        for r in records:
            new_record = {}
            for f in fields:
                new_record[f] = r.get(f)
            new_record['modification'] = datetime.now() # It's actually  more like "touch date"
            new_records.append(new_record)
        cursor = self.connection.cursor()
        cursor.executemany(
            """insert or ignore into record (
                uuid, name, filename, path, location, type, kind, thumbnail, modification
            ) values (:uuid, :name, :filename, :path, :location, :type, :kind, :thumbnail, :modification)""", new_records
        )
        cursor.executemany(
            """update record
            set name = :name, filename = :filename, path = :path, location = :location, type = :type, kind = :kind, thumbnail = :thumbnail, modification = :modification
            where uuid = :uuid""", new_records
        )
        if commit:
            self.connection.commit()
    
    def cache_query(self, query, uuids, scores, commit=True):
        cursor = self.connection.cursor()
        query_date = datetime.now()
        for uuid, score in zip(uuids, scores):
            cursor.execute(
                """insert or ignore into query (
                    query, record_uuid, score, query_date
                ) values (:query, :record_uuid, :score, :query_date)""", {
                    'query': query,
                    'record_uuid':  uuid,
                    'score':score,
                    'query_date': query_date
                }
            )
            cursor.execute(
                """update query
                set record_uuid = :record_uuid, score = :score, query_date = :query_date
                where query = :query AND record_uuid = :record_uuid""", {
                    'query': query,
                    'record_uuid':  uuid,
                    'score': score,
                    'query_date': query_date,
                }
            )
        if commit:
            self.connection.commit()
    
    def get_cached_query(self, query):
        cursor = self.connection.cursor()
        cursor.execute('select record_uuid, score, query_date from query where query = :query', {'query': query})
        rows = cursor.fetchall()
        uuids = []
        scores = []
        query_date = None
        for row in rows:
            uuids.append(row[0])
            scores.append(row[1])
            query_date = row[2]
        return uuids, scores, query_date
    
    def get_cached_record(self, uuid, modification_date=None):
        cursor = self.connection.cursor()
        if modification_date:
            cursor.execute('select uuid, name, filename, path, location, type, kind, thumbnail, modification from record where uuid = :uuid and modification > :modification_date',
                {'uuid': uuid, 'modification_date': modification_date})
        else:
            cursor.execute('select uuid, name, filename, path, location, type, kind, thumbnail, modification from record where uuid = :uuid', {'uuid': uuid})
        row = cursor.fetchone()
        if row:
            keys = ('uuid', 'name', 'filename', 'path', 'location', 'type', 'kind', 'thumbnail', 'modification')
            return dict(zip(keys, row))
        else:
            return None
    
    def get_or_fetch(self, uuid, modification_date, cache=True):
        return self.get_or_fetch_multiple((uuid,), (modification_date,), cache)[0]

    def get_or_fetch_multiple(self, uuids, modification_dates=None, cache=True):
        uuid_to_record = {uuid: None for uuid in uuids}
        hits = set()

        if modification_dates:
            assert len(uuids) == len(modification_dates)
            assert all(isinstance(d, datetime) or d is None for d in modification_dates)
        for uuid, modification in zip(uuids, modification_dates):
            cached_record = self.get_cached_record(uuid, modification_date=modification)
            if cached_record:
                uuid_to_record[uuid] = cached_record
                hits.add(uuid)
        remained = set(uuids).difference(hits)
        
        if remained:
            remianed_records = self.fetch(remained)
            if cache:
                self.cache_records(remianed_records)
            for r in remianed_records:
                uuid_to_record[r['uuid']] = r

        return [uuid_to_record[uuid] for uuid in uuids]
    
    def fetch(self, uuids):
        import subprocess
        import json
        return json.loads(subprocess.check_output(['osascript', '-l', 'JavaScript', 'uuid.js'] + list(uuids)))

    def get_or_fetch_multithread(self, uuids, modification_dates):
        from multiprocessing import Pool
        pool = Pool(8)

        results = pool.map(_get_or_fetch_map, zip(uuids, modification_dates))
        pool.close() 
        pool.join()
        return results

cursor = Cache().connection.cursor()

cursor.execute("""create table if not exists query (
    query text,
    record_uuid,
    score real,
    query_date timestamp,
    PRIMARY KEY (query, record_uuid)
)""")

cursor.execute("""create table if not exists record (
    uuid text primary key,
    name text,
    filename text,
    path text,
    location text,
    type text,
    kind text,
    thumbnail text,
    modification timestamp
)""")

Cache().connection.commit()

if __name__ == "__main__":
    print(Cache().get_cached_record('35C2D49D-8A59-4E43-8A91-7C547E52A4FF', modification_date=datetime(1997, 2, 19)))