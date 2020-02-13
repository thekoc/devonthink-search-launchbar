#!/usr/local/bin/python3
#
# LaunchBar Action Script
#

import sys
import json
import re

from devonthink import DEVONthink
from logger import logger
import config

QUERY_TEMPLATE = config.query_template
items = []

def preprocess_query(arg):
    def prepend_tilde(word):
        if word.startswith('~'):
            return word
        else:
            return '~' + word
    
    query_template = QUERY_TEMPLATE
    if len(arg.split()) == 1:
        return query_template.format(prepend_tilde(arg))
    else:
        parts = arg.split(' ')
        parts[-1] = prepend_tilde(parts[-1])
        return query_template.format(' '.join(parts))

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
    print(json.dumps(items))

    # print(items[0])
    # import subprocess
    # subprocess.call(['./action.py', items[0]['actionArgument']])

if __name__ == "__main__":
    main()
    # items.append({
    #     'title': 'test',
    #     'action': 'action.py',
    # })
    # print(json.dumps(items))
