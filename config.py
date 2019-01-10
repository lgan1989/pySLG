# -*- coding: utf-8 -*-

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
            log.write(msg + '\n')
else:
    debug = False
    logger = None
