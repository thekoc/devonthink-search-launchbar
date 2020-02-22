#!/usr/bin/python3
import os
import sys
import json
import subprocess

from launchbar import LaunchBar
from devonthink import DEVONthink
from devonthink import DEVONthink
from frequency import Frequency
from logger import logger


items = []


def browse_group(dt, uuid):
    logger.debug('browse_group')
    items.extend(dt.group(uuid))
    print(json.dumps(items))

def main():
    dt = DEVONthink()
    argument = json.loads(sys.argv[1])
    record = argument['pickedRecord']
    uuid = argument['pickedUuid']
    candidate_uuids = argument['candidateUuids']
    Frequency().update_frequency(uuid, candidate_uuids)
    if record.get('type') in ('group', 'smart group'):
        logger.debug('item is group')
        if LaunchBar.is_command_key():
            LaunchBar.hide()
            dt.reveal_item(uuid)
        elif LaunchBar.is_alternate_key():
            browse_group(dt, uuid)
        else:
            if argument.get('returnKeyToBrowseGroup'):
                browse_group(dt, uuid)
            else:
                LaunchBar.hide()
                dt.open_item(uuid)
    else:
        if LaunchBar.is_command_key() and LaunchBar.is_alternate_key():
            subprocess.call(['open', os.path.dirname(record['path'])])
        elif LaunchBar.is_command_key():
            LaunchBar.hide()
            dt.reveal_item(uuid)
        elif LaunchBar.is_alternate_key():
            subprocess.call(['open', record['path']])
        elif LaunchBar.is_shift_key():
            subprocess.call(['open', os.path.dirname(record['path'])])
        else:
            LaunchBar.hide()
            dt.open_item(uuid)


if __name__ == "__main__":
    main()
    # reveal_item('EFFA8C64-963B-4213-B5B1-D011D42DB575')
    # subprocess.call(['/usr/bin/open', 'x-devonthink-item://{}?reveal=1'.format('EFFA8C64-963B-4213-B5B1-D011D42DB575')])