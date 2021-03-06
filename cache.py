#!/usr/bin/python3

import os
import sqlite3
from datetime import datetime
from multiprocessing.dummy import Pool as ThreadPool

from launchbar import LaunchBar


DB_PATH = os.path.join(LaunchBar.support_path(), 'cache.db')

class Cache:
    def __init__(self):
        self.connection = sqlite3.connect(DB_PATH, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
    
    def cache(self, record, commit=True):
        return self.cache_many((record,), commit)
    
    def cache_many(self, records, commit=True):
        fields = ('uuid', 'name', 'filename', 'path', 'location', 'referenceURL', 'type', 'kind', 'thumbnail')
        new_records = []
        for r in records:
            new_record = {}
            for f in fields:
                new_record[f] = r.get(f)
            new_record['modification'] = datetime.now()
            new_records.append(new_record)
        cursor = self.connection.cursor()
        cursor.executemany(
            """insert or ignore into record (
                uuid, name, filename, path, location, reference_url, type, kind, thumbnail, modification
            ) values (:uuid, :name, :filename, :path, :location, :referenceURL, :type, :kind, :thumbnail, :modification)""", new_records
        )
        cursor.executemany(
            """update record
            set name = :name, filename = :filename, path = :path, location = :location, reference_url = :referenceURL, type = :type, kind = :kind, thumbnail = :thumbnail, modification = :modification
            where uuid = :uuid""", new_records
        )
        if commit:
            self.connection.commit()
    
    def get_cached(self, uuid, include_modification=False, modification_date=None):
        cursor = self.connection.cursor()
        if modification_date:
            cursor.execute('select uuid, name, filename, path, location, reference_url, type, kind, thumbnail, modification from record where uuid = :uuid and modification > :modification_date',
                {'uuid': uuid, 'modification_date': modification_date})
        else:
            cursor.execute('select uuid, name, filename, path, location, reference_url, type, kind, thumbnail, modification from record where uuid = :uuid', {'uuid': uuid})
        row = cursor.fetchone()
        if row:
            if include_modification:
                keys = ('uuid', 'name', 'filename', 'path', 'location', 'referenceURL', 'type', 'kind', 'thumbnail', 'modification')
            else:
                row = row[:-1]
                keys = ('uuid', 'name', 'filename', 'path', 'location', 'referenceURL', 'type', 'kind', 'thumbnail')
            return dict(zip(keys, row))
        else:
            return None
    
    def get_or_fetch(self, uuid, cache=True):
        return self.get_or_fetch_multiple((uuid,), cache)[0]

    def get_or_fetch_multiple(self, uuids, modification_dates=None, cache=True, include_modification=False):
        records = [None] * len(uuids)
        uuid_to_pos = {uuid: i for i, uuid in enumerate(uuids)}
        uuids = set(uuids)
        hits = set()

        if modification_dates:
            assert len(uuids) == len(modification_dates)
            assert all(isinstance(d, datetime) for d in modification_dates)
        for i, uuid in enumerate(uuids):
            modification_date = modification_dates[i]
            cached = self.get_cached(uuid, include_modification=include_modification, modification_date=modification_date)
            if cached:
                records[uuid_to_pos[uuid]] = cached
                hits.add(uuid)
        remained = uuids.difference(hits)
        
        if remained:
            import subprocess
            import json
            remianed_records = json.loads(subprocess.check_output(['osascript', '-l', 'JavaScript', 'uuid.js'] + list(remained)))
            if cache:
                self.cache_many(remianed_records)
            for r in remianed_records:
                records[uuid_to_pos[r['uuid']]] = r

        return records

    def get_or_fetch_multithread(self, uuids):
        # from multiprocessing import Pool
        pool = ThreadPool(64)
        results = pool.map(lambda u: Cache().get_or_fetch(u), uuids)
        pool.close() 
        pool.join()
        return results

cursor = Cache().connection.cursor()
cursor.execute("""create table if not exists record (
    uuid text primary key,
    name text,
    filename text,
    path text,
    location text,
    reference_url text,
    type text,
    kind text,
    thumbnail text,
    modification timestamp
)""")
Cache().connection.commit()

if __name__ == "__main__":
    print(Cache().get_cached('35C2D49D-8A59-4E43-8A91-7C547E52A4FF', modification_date=datetime(1997, 2, 19)))