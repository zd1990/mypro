# coding:utf-8
__author__ = 'DingZhang(dingzhang1990@gmail.com)'

from celery import task

@task
def test(a, b):
    return a + b
