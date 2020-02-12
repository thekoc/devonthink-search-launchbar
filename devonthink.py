#!/usr/local/python3
"""A wrapper for search.js"""
import sys
import json
import subprocess
import os
import re


from datetime import datetime
from urllib.parse import quote
from launchbar import LaunchBar
from frequency import Frequency
from logger import logger
from cache import Cache
import config

"""An middle layer that handles the records returned by JXA.

Using record (or r) to represent JXA returned record,
using item to represent LaunchBar item.
"""
CONSTANT_FREQUENCY_WEIGHT = config.frequency_weight

def get_extension_name(r):
    filename = r['filename']
    return os.path.splitext(filename)[1][1:]

def readable_path(path):
    readable = path
    if path.startswith('/'):
        readable = readable[1:]
    if path.endswith('/'):
        readable = readable[:-1]
    return re.sub(r'(?<!\\)/', '▶️', readable)

def get_type(r):
    if r['location'].startswith('/Tags'):
        return 'tag'
    elif get_extension_name(r) in ('doc', 'docx'):
        return 'word document'
    elif get_extension_name(r) in ('xls', 'xlsx'):
        return 'excel document'
    elif r.get('type') is None or r.get('type') == 'unknown':
        extension = get_extension_name(r)
        if extension:
            return extension
        else:
            return 'unknown'
    else:
        return r.get('type')

def get_icon(r):
    if get_type(r) == 'tag':
        return 'tag.icns'
    elif get_type(r) == 'picture':
        return r['path']
    potential_icon = os.path.join(LaunchBar.resources_path(), get_type(r) + '.icns')
    if os.path.isfile(potential_icon):
        return potential_icon
    else:
        logger.debug('document without icon: {}'.format(get_type(r)))
        return os.path.join(LaunchBar.resources_path(), 'unknown.icns')

def to_lb_item(record, candidate_uuids, returnKeyToBrowseGroup=True):
    potential_icon = get_icon(record)
    actionArgument = json.dumps({
        'pickedRecord': record,
        'pickedUuid': record['uuid'],
        'candidateUuids': candidate_uuids,
        'returnKeyToBrowseGroup': returnKeyToBrowseGroup
    })
    if record.get('type') in ('group', 'smart group'):
        item = {
            'title': record['name'],
            'badge': record['kind'],
            'icon': potential_icon,
            'subtitle': '📂' + readable_path(record.get('location')),
            'alwaysShowsSubtitle': True,
            'action': 'action.py',
            'actionArgument': actionArgument,
            'actionReturnsItems': True,
        }
    else:
        item = {
            'title': record['name'],
            'badge': record['kind'],
            'icon': potential_icon,
            'quickLookURL': 'file://' + quote(record['path']),
            'subtitle': '📂' + readable_path(record.get('location')),
            'alwaysShowsSubtitle': True,
            'action': 'action.py',
            'actionArgument': actionArgument,
            'actionRunsInBackground': True
        }
    return item


def get_group_children(uuid):
    output = subprocess.check_output(['osascript', '-l', 'JavaScript', 'group.js', uuid])
    return json.loads(output)

class DEVONthink:
    """Provide scored result in LaunchBar items json list."""
    cache = Cache()
    frequency = Frequency()

    def __init__(self):
        pass
        
    def activate(self):
        cmd = ['osascript', '-e', 'tell application "DEVONthink 3" to activate']
        subprocess.call(cmd)

    def reveal_item(self, uuid):
        self.activate()
        cmd = ['/usr/bin/open', 'x-devonthink-item://{}?reveal=1'.format(uuid)]
        # cmd = ['/usr/bin/osascript', 'reveal.scpt', uuid]
        subprocess.call(cmd)

    def open_item(self, uuid):
        cmd = ['/usr/bin/open', 'x-devonthink-item://{}'.format(uuid)]
        subprocess.call(cmd)

    def search_js(self, query):
        jsonArg = json.dumps({
            'query': query,
            'field': 'all',
            # 'range': [0, 80]
        })
        output = subprocess.check_output(['osascript', '-l', 'JavaScript', 'search.js', jsonArg])
        return json.loads(output)
    
    def search_js_cached(self, query):
        logger.debug('before jxa search.js')
        jsonArg = json.dumps({
            'query': query,
            'field': 'part',
            # 'range': [0, 80]
        })
        output = subprocess.check_output(['osascript', '-l', 'JavaScript', 'search.js', jsonArg])
        logger.debug('after jxa search.js')

        records = json.loads(output)
        uuids = [r['uuid'] for r in records]

        logger.debug('before get_or_fetch_multiple')
        
        def str_to_date(date_str):
            return datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S.%f%z")
            
        modification_dates = [str_to_date(r['modificationDate']) for r in records]
        cached = self.cache.get_or_fetch_multiple(uuids, modification_dates=modification_dates)
        logger.debug('after get_or_fetch_multiple')
        for c, r in zip(cached, records):
            c['score'] = r['score']
        return cached
    
    def search_js_multithread(self, query):
        pass
    
    def rescore(self, records):
        for r in records:
            frequency = self.frequency.get_frequency(r['uuid'])
            r['score'] += CONSTANT_FREQUENCY_WEIGHT * frequency if frequency else 0
        records.sort(key=lambda r: r['score'], reverse=True)


    def search(self, query):
        logger.debug('before search js')
        records = self.search_js_cached(query)
        logger.debug('after search js')
        logger.debug('before rescore')
        self.rescore(records)
        logger.debug('after rescore')
        candidate_uuids = [r['uuid'] for r in records]
        return [to_lb_item(r, candidate_uuids, returnKeyToBrowseGroup=False) for r in records]
    
    def group(self, group_uuid):
        children = get_group_children(group_uuid)
        self.rescore(children)
        candidate_uuids = [r['uuid'] for r in children] 
        return [to_lb_item(r, candidate_uuids) for r in children]


if __name__ == "__main__":
    se = DEVONthink()
    print(se.search_js_cached('hhh'))