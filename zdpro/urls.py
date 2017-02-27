#coding:utf-8
__author__ = 'DingZhang(dingzhang1990@gmail.com)'
from django.conf.urls import url,include
from django.contrib import admin
from views import plus

urlpatterns = [
    url(r'^plus/?P<x>\d/?P<y>\d', plus)
]
