# coding:utf-8
import Queue
import httplib
import json
import subprocess
import threading
import logging
import time
import errno
zdpro_log = logging.getLogger('zdpro_log')
POLL_TIME_INCR = 0.5

def exec_shell(cmd):
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    p.wait()
    out = p.stdout
    err = p.stderr
    ret = p.returncode
    return out, err, ret

def prints(msg):
    print json.dumps(msg, indent=4)

def get_time():
    value = time.time()
    format = '%Y-%m-%d %H:%M:%S'
    value = time.localtime(value)
    time_now = time.strftime(format, value)
    return time_now

def dlog(log, lever="INFO"):
    '''
    日志打印方法
    :param log:
    :param lever:
    :return:
    '''
    try:
        lever = lever.upper()
        if lever == "INFO":
            zdpro_log.info(log)
        elif lever == "DEBUG":
            zdpro_log.debug(log)
        elif lever == "WARNING":
            zdpro_log.warning(log)
        elif lever == "ERROR":
            zdpro_log.error(log)
        elif lever == "CRITICAL":
            zdpro_log.critical(log)
    except:
        pass


def send_request(methods, ip, port, path, params, head=None, flag=0):
    try:
        if params:
            params_str = json.dumps(params)
        else:
            params_str = ""
        conn = httplib.HTTPConnection("%s:%s" % (ip, port))
        # path = "%s?%s"%(path,params_str)
        if head:
            conn.request(methods, path, params_str, head)
        else:
            conn.request(methods, path, params_str)
        res = conn.getresponse()
        # print res.status, res.reason
        assert res.status in [200, 201, 202, 203, 204], "send_request status=%s,reason=%s,path=%s,params=%s" % (
            res.status, res.reason, path, params_str)
        if flag:
            token_id = res.getheader("X-Subject-Token", "")
            res_json = json.loads(res.read())
            res_json.update({"token_id": token_id})
        else:
            try:
                res_json = json.loads(res.read())
            except:
                res_json = ""
                pass
        ret = res_json
    except Exception, err:
        dlog("send_request err:%s" % err, lever="ERROR")
        ret = 1
    return ret

class WorkPool(): #工作线程
    def __init__(self):
        self.queue = Queue.Queue()
        self.worklist = []
        self.retList = []

    def task_add(self, fun, arglist):
        self.queue.put((fun, arglist))

    def work_add(self, threadnum=3):
        for i in range(threadnum):
            self.worklist.append(WorkThread(self.queue, self.retList))

    def work_start(self):
        for work in self.worklist:
            work.start()

    def work_wait(self, time=120):
        for work in self.worklist:
            if work.isAlive():
                work.join(time)
        self.worklist = []


class WorkThread(threading.Thread):
    def __init__(self, queue, retList):
        threading.Thread.__init__(self)
        self.work_queue = queue
        self.retList = retList

    def run(self):
        while True:
            try:
                fun, args = self.work_queue.get(block=False)
                ret = fun(*args)
                self.retList.append(ret)
            except Exception, data:
                break


class exec_thread(threading.Thread):
    def __init__(self, target, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        self.target = target
        self.exception = None
        threading.Thread.__init__(self)

    def run(self):
        try:
            self.retval = self.target(*self.args, **self.kwargs)
        except Exception as e:
            self.exception = e
            dlog("exec_thread err:%s" % e, lever="ERROR")

def run_in_thread(target, *args, **kwargs):
    interrupt = False
    event = threading.Event()
    timeout = kwargs.pop('timeout', 0)
    countdown = timeout
    kwargs.update({"event": event})
    t = exec_thread(target, *args, **kwargs)
    t.daemon = True
    t.start()
    try:
        while t.is_alive():
            t.join(POLL_TIME_INCR)
            if timeout and t.is_alive():
                countdown = countdown - POLL_TIME_INCR
                if countdown <= 0:
                    raise KeyboardInterrupt
        t.join()
    except KeyboardInterrupt:
        event.set()
        dlog("method:%s timeout" % target.func_name, lever="ERROR")
        interrupt = True
    if interrupt:
        t.retval = -errno.EINTR
    if t.exception:
        raise t.exception
    return t.retval


# 异常日志记录，做装饰符使用
def plog(method_name):
    def logs(func):
        def catch_log(*args, **kwargs):
            try:
                ret = 0
                dlog("start %s" % method_name, lever="DEBUG")
                ret = func(*args, **kwargs)
                dlog("finsh %s" % method_name, lever="DEBUG")
            except Exception, err:
                ret = 1
                dlog("%s err:%s" % (method_name, err), lever="ERROR")
            return ret
        return catch_log
    return logs


# 测试时使用，计算执行时间，如果需要得到更具体的时间消耗，使用@profile
def times(method_name):
    def get_time(func):
        def catch_time(*args, **kwargs):
            time_start = time.time()
            ret = func(*args, **kwargs)
            time_end = time.time()
            time_cost = time_end - time_start
            dlog("%s cost time:%s" % (method_name, time_cost))
            return ret
        return catch_time
    return get_time


