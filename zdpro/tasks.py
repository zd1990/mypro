# coding:utf-8
__author__ = 'DingZhang(dingzhang1990@gmail.com)'

from celery import task,platforms
from middleware.hdware.collect import Collect
platforms.C_FORCE_ROOT = True

@task
def getinfo_hard(types,hostname,port=''):
    '''
    远程获取机器信息
    :type ['cpu_load','mem','nic','disk_use','disk_ops','sysload']
    :param list_type:
    :return:
    '''
    if types == 'cpu_load':
        Collect.get_cpu_load(hostname,port)
    elif types == 'mem':
        Collect.get_mem_info(hostname,port)
    elif types == 'nic':
        Collect.get_nic_info(hostname,port)
    elif types == 'disk_use':
        Collect.get_disk_use(hostname,port)
    elif types == 'disk_ops':
        Collect.get_disk_info(hostname,port)
    elif types == 'sysload':
        Collect.get_sys_load(hostname,port)





