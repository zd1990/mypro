# coding:utf-8
__author__ = 'DingZhang(dingzhang1990@gmail.com)'

from celery import task
from middleware.hdware.collect import Collect

@task
def getinfo_hard(list_type,hostname,port=''):
    '''
    远程获取机器信息
    :type ['cpu_load','mem','nic','disk_use','disk_ops','sysload']
    :param list_type:
    :return:
    '''
    for type in list_type:
        if type == 'cpu_load':
            Collect.get_cpu_load(hostname,port)
        elif type == 'mem':
            Collect.get_mem_info(hostname,port)
        elif type == 'nic':
            Collect.get_nic_info(hostname,port)
        elif type == 'disk_use':
            Collect.get_disk_use(hostname,port)
        elif type == 'disk_ops':
            Collect.get_disk_info(hostname,port)
        elif type == 'sysload':
            Collect.get_sys_load(hostname,port)





