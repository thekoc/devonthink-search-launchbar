#!/usr/bin/python3
"""This file is executed when user press enter on one of the search result
"""

import os
import sys
import json
import subprocess

from launchbar import LaunchBar
from devonthink import DEVONthink
from devonthink import DEVONthink
from frequency import Frequency
from logger import logger
from config import UserConfig


items = []
SHORTCUT_PATH  = UserConfig.shortcut_path

dt = DEVONthink()


def browse_group(dt, uuid):
    logger.debug('browse_group')
    items.extend(dt.group(uuid))
    print(json.dumps(items))

def create_shortcut(record, is_smart_group=False):
    expanded = os.path.expanduser(SHORTCUT_PATH)
    os.makedirs(expanded, exist_ok=True)
    devonthink_url = dt.get_reference_url(record['uuid'], is_smart_group)
    content = """
        <?xml version="1.0" encoding="UTF-8"?>
        <!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
        <plist version="1.0">
        <dict>
            <key>URL</key>
            <string>{URL}</string>
        </dict>
        </plist>
    """.format(URL=devonthink_url)
    with open(os.path.join(expanded, record['name'] + '.inetloc'), 'w') as f:
        f.write(content)

def action(record, uuid, candidate_uuids, return_key_to_browse):
    logger.debug('Picked record is: ' + str(record))
    Frequency().update_frequency(uuid, candidate_uuids)
    record_type = record.get('type')
    is_smart_group = (record_type == 'smart group')
    if record_type in ('group', 'smart group'):
        logger.debug('item is group')
        if LaunchBar.is_command_key() and LaunchBar.is_alternate_key():
            create_shortcut(record, is_smart_group)
            LaunchBar.hide()
            dt.open_item(uuid)
        elif LaunchBar.is_command_key():
            LaunchBar.hide()
            dt.reveal_item(uuid)
        elif LaunchBar.is_alternate_key():
            browse_group(dt, uuid)
        else:
            if return_key_to_browse:
                browse_group(dt, uuid)
            else:
                LaunchBar.hide()
                dt.open_item(uuid)
    else:
        if LaunchBar.is_command_key() and LaunchBar.is_alternate_key():
            create_shortcut(record, is_smart_group)
            LaunchBar.hide()
            dt.open_item(uuid)
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

def main():
    argument = json.loads(sys.argv[1])
    record = argument['pickedRecord']
    uuid = argument['pickedUuid']
    candidate_uuids = argument['candidateUuids']
    return_key_to_browse = argument.get('returnKeyToBrowseGroup')
    action(record, uuid, candidate_uuids, return_key_to_browse)


if __name__ == "__main__":
    main()
    # record = {"name": "CSI7162 ITS", "kind": "Group", "location": "/", "type": "group", "path": "", "uuid": "0A02D63C-D815-474D-8D14-3897A6D4784C", "filename": "CSI7162 ITS"}
    # create_shortcut(record, False)