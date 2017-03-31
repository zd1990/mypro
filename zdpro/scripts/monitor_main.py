#coding:utf-8
__author__ = 'DingZhang(dingzhang1990@gmail.com)'
from zdpro.middleware.common import dlog
from zdpro.middleware.monitor import Monitor

def run():
    dlog("start monitor")
    monitor = Monitor()
    monitor.start()