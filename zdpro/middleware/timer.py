#coding:utf-8
__author__ = 'DingZhang(dingzhang1990@gmail.com)'

import time
import threading

class Timer(threading.Thread):
    def __init__(self):
        super(Timer,self).__init__()
        self.work_list = []
        self.lock = threading.Lock()
        self.cond = threading.Condition()

    def __put(self,func,args,kwargs,interval):
        '''
        任务入队，并排序
        (func,args,kwargs,interval,times)
        :return:
        '''
        flag = 1
        times_work = int(time.time()) + int(interval)
        if not self.work_list:
            self.work_list.append((func,args,kwargs,interval,times_work))
            if self.lock.locked():
                self.lock.release()
        else:
            for i in self.work_list:
                times = i[-1]
                if times_work < times:
                    index = self.work_list.index(i)
                    self.lock.acquire()
                    self.work_list.insert(index,(func,args,kwargs,interval,times_work))
                    self.lock.release()
                    if index == 0:
                        self.cond.acquire()
                        self.cond.notify()
                        self.cond.release()
                    flag = 0
                    break
            if flag:
                self.work_list.append((func,args,kwargs,interval,times_work))

    def __get(self):
        '''
        任务出队，删除任务
        :return:
        '''
        if self.work_list:
            ret = self.work_list[0]
        else:
            self.lock.acquire() #如果list为空则阻塞
            ret = self.work_list[0]
            self.lock.release()
        return ret

    def __pop(self):
        '''
        删除任务
        :return:
        '''
        self.lock.acquire()
        self.work_list.pop(0)
        self.lock.release()

    def add(self,func):
        '''
        添加任务的装饰器
        :return:
        '''
        def work_put(*args,**kwargs):
            interval = kwargs.pop('interval')
            self.__put(func,args,kwargs,interval)
        return work_put

    def run(self):
        '''
        运行函数
        :return:
        '''
        while True:
            self.lock.acquire()
            func,args,kwargs,interval,times = self.__get()
            if self.lock.locked():
                self.lock.release()
            times_now = int(time.time())
            if times_now >= times:
                func(*args,**kwargs)
                self.__pop()
                self.__put(func,args,kwargs,interval)
            else:
                time_sleep = times - times_now
                self.cond.acquire()
                self.cond.wait(time_sleep) #如果有新加入的任务的执行时间比现在的早，则唤醒线程执行
                self.cond.release()
