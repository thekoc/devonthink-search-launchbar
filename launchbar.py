#!/usr/bin/python3
import os
import subprocess
import re
from urllib.parse import quote_plus

DEBUG = os.getenv('LB_ACTION_PATH') is None

def getenv(key, default=None):
    if DEBUG:
        if re.match(r'LB_.*_PATH', key):
            return os.path.curdir
        elif re.match(r'LB_.*_KEY', key):
            return "1"
    else:
        return os.getenv(key, default)

class LaunchBar:
    @staticmethod
    def is_shift_key():
        return getenv('LB_OPTION_SHIFT_KEY') == "1"
    
    @staticmethod
    def is_command_key():
        return getenv('LB_OPTION_COMMAND_KEY') == "1"

    @staticmethod
    def is_control_key():
        return getenv('LB_OPTION_CONTROL_KEY') == "1"
        
    @staticmethod
    def is_space_key():
        return getenv('LB_OPTION_SPACE_KEY') == "1"

    @staticmethod
    def is_alternate_key():
        return getenv('LB_OPTION_ALTERNATE_KEY') == "1"
    
    @staticmethod
    def hide():
        subprocess.call(['osascript', '-e', 'tell application "LaunchBar" to hide'])
    
    @staticmethod
    def large_type(msg):
        subprocess.call(['open', 'x-launchbar:large-type?string={}'.format(quote_plus(msg))])

    @staticmethod
    def cache_path():
        return getenv('LB_CACHE_PATH')
    
    @staticmethod
    def support_path():
        return getenv('LB_SUPPORT_PATH')

    @staticmethod
    def resources_path():
        return os.path.join(getenv('LB_ACTION_PATH'), 'Contents', 'Resources')
