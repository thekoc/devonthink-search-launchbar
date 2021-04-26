#!/usr/bin/python3
#
# LaunchBar Action Script
#

import sys
import json

from devonthink import DEVONthink
from logger import logger
from config import UserConfig

EXCLUDED_TAG = UserConfig.excluded_tag
QUERY_TEMPLATE = 'name:({}) tags!={}'
items = []

def preprocess_query(arg):
    def prepend_tilde(word):
        if word.startswith('~'):
            return word
        else:
            return '~' + word

    if len(arg.split()) == 1:
        return QUERY_TEMPLATE.format(prepend_tilde(arg), EXCLUDED_TAG)
    else:
        parts = arg.split(' ')
        parts = [prepend_tilde(p) for p in parts]
        return QUERY_TEMPLATE.format(' '.join(parts), EXCLUDED_TAG)

def main():
    dt = DEVONthink()
    for arg in sys.argv[1:]:
        if arg:
            logger.debug('======================')
            logger.debug('before search')
            query = preprocess_query(arg)
            logger.debug('query: ' + query)
            items.extend(dt.search(query))
            logger.debug('after search')
        
            if not items:
                items.append({
                    'title': 'No record found',
                    'icon': 'character:☹️'
                })
        else:
            items.append({
            'title': 'Please input the query',
            'icon': 'character:⌨️'
            })
    logger.debug(f'Record amounts: {len(items)}')
    print(json.dumps(items))


if __name__ == "__main__":
    main()
