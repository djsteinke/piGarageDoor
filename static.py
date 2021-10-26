import logging
import os

import properties

c_dir = os.getcwd()
p_dir = os.path.dirname(os.getcwd())
safe_mac = ['58:cb:52:0b:a2:a7']


def check_mac(mac):
    for m in safe_mac:
        if mac == m:
            return True
    return False


def get_logging_level():
    if properties.log_debug:
        return logging.DEBUG
    elif properties.log_info:
        return logging.INFO
    elif properties.log_warning:
        return logging.WARNING
    else:
        return logging.ERROR
