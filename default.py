#!/usr/bin/python3
#
# LaunchBar Action Script
#

import sys
import json
import os

from devonthink import DEVONthink
from logger import logger
from config import UserConfig
from cache import DB_PATH as DB_PATH_CACHE
from frequency import DB_PATH as DB_PATH_FREQUENCY

EXCLUDED_TAG = UserConfig.excluded_tag
QUERY_TEMPLATE = 'name:({}) tags!={}'
items = []

class LaunchBarError(Exception):
    def __init__(self, launchbar_item, message=None):
        self.message = message
        self.launchbar_item = launchbar_item

def clean_all_db():
    os.remove(DB_PATH_CACHE)
    os.remove(DB_PATH_FREQUENCY)

def parse_query(arg):
    def prepend_tilde(word):
        if word.startswith('~'):
            return word
        else:
            return '~' + word
    if arg.startswith('>'):
        arg = arg[1:].strip()
        if arg == 'clean':
            clean_all_db()
        else:
            raise LaunchBarError(dict(title='Invalid arguments',icon='character:🚫'))

    elif len(arg.split()) == 1:
        return QUERY_TEMPLATE.format(prepend_tilde(arg), EXCLUDED_TAG)
    else:
        parts = arg.split(' ')
        parts = [prepend_tilde(p) for p in parts]
        return QUERY_TEMPLATE.format(' '.join(parts), EXCLUDED_TAG)

def main():
    dt = DEVONthink()
    assert len(sys.argv) == 2
    arg = sys.argv[1]
    try:
        if arg:
            logger.debug('======================')
            logger.debug('before search')
            query = parse_query(arg)
            logger.debug('query: ' + query)
            items.extend(dt.search(query))
            logger.debug('after search')
        
            if not items:
                raise LaunchBarError({
                    'title': 'No record found',
                    'icon': 'character:☹️'
                })
        else:
            raise LaunchBarError({
            'title': 'Please inpu the query',
            'icon': 'character:⌨️'
            })
    except LaunchBarError as e:
        lb_item = e.launchbar_item
        if lb_item:
            items.append(lb_item)
        else:
            raise ValueError()
        
    logger.debug(f'Record amounts: {len(items)}')
    print(json.dumps(items))


if __name__ == "__main__":
    main()
