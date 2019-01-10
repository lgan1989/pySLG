# -*- coding: utf-8 -*-
import sys

FPS = 60
clock = 0
db_initiated = False
env = 'dev'

if env == 'dev':
    debug = True
    f = open("log.txt" , "w")
    f.close()
    def logger(msg):
        with open("log.txt" , "a") as log:
            if sys.version_info[0] < 3:
                log.write(msg.encode('utf-8') + '\n')
            else:
                log.write(msg + '\n')
else:
    debug = False
    logger = None
