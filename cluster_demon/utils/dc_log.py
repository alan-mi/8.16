# -*- coding: utf-8 -*-

import os
import sys
import logging
import datetime
import multiprocessing

log_dir = os.path.expanduser('/tmp')+'/cluster_logs/'
if not os.path.exists(log_dir):
    os.makedirs(log_dir)
elif not os.path.isdir(log_dir):
    os.makedirs(log_dir)
else:
    pass

logger = logging.getLogger()
# logger.setLevel(logging.INFO)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s %(levelname)s %(pathname)s %(funcName)s [line:%(lineno)d] %(message)s')

logfile = logging.FileHandler('{}{}.log'.format(
    log_dir,
    # datetime.datetime.now().strftime('%Y-%m-%d_%H.%M.%S_') + multiprocessing.current_process().name
    datetime.datetime.now().strftime('%Y-%m-%d_%H.%M.%S_') + os.path.splitext(os.path.basename(sys.argv[0]))[0]
), mode='a')
# logfile.setLevel(logging.CRITICAL)
# logfile.setLevel(logging.ERROR)
logfile.setLevel(logging.WARNING)
# logfile.setLevel(logging.INFO)
# logfile.setLevel(logging.DEBUG)
logfile.setFormatter(formatter)
logger.addHandler(logfile)

console = logging.StreamHandler()
# console.setLevel(logging.CRITICAL)
# console.setLevel(logging.ERROR)
# console.setLevel(logging.WARNING)
# console.setLevel(logging.INFO)
console.setLevel(logging.DEBUG)
console.setFormatter(formatter)
logger.addHandler(console)
