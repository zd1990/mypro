#coding:utf-8
import ConfigParser

from zdpro.middleware.common import plog

__author__ = 'DingZhang(dingzhang1990@gmail.com)'
from project.settings import PATH_CONF
from zdpro.middleware.hdware.common import Common
from zdpro.models import HostDB

class Config():
    def __init__(self):
        self.path_config = PATH_CONF
        self.list_item_default = {'interval_cpu':0,'interval_mem':0,'interval_disk_use':0,'interval_disk_iops':0,'interval_netcard':0,'interval_system':0}
        self.list_section = ['global','host']
        self.list_hostobj = []

    def _config_read(self):
        self.cf = ConfigParser.ConfigParser()
        self.cf.read(PATH_CONF)

    def _config_write(self):
        assert self.cf
        fp = open(self.path_config,'w')
        self.cf.write(fp)
        fp.close()

    @plog('Config.init_config')
    def init_config(self):
        '''
        解析配置文件
        :return:
        '''
        self._config_read()
        list_section_now = self.cf.sections()
        if 'global' in list_section_now:
            dict_global = dict(self.cf.items('global'))
            self.list_item_default.update(dict_global)
        list_stand_section = [i for i in list_section_now if i.startswith('host:')]
        list_stand_host = [i.replace('host:','') for i in list_stand_section]
        if 'host' in list_section_now:
            info_interval_tmp = self.list_item_default.copy()
            dict_host = dict(self.cf.items('host'))
            for hostname,ip in dict_host.items():
                if ip.find(":") != -1:
                    ip,port = ip.split(':')
                else:
                    port = 22
                if hostname in list_stand_host:
                    tmp_info = self.cf.items('host:%s'%hostname)
                    info_interval_tmp.update(tmp_info)
                else:
                    info_interval_tmp = self.list_item_default
                host_obj = Hosts(hostname,ip,port,info_interval_tmp)
                self.list_hostobj.append(host_obj)
        return 0

    def get_hosts(self):
        return self.list_hostobj



class Hosts():
    def __init__(self,hostname,ip,ssh_port,info_interval):
        self.hostname = hostname
        self.ip = ip
        self.ssh_port = ssh_port
        self.interval_cpu = info_interval.get('interval_cpu',0)
        self.interval_mem = info_interval.get('interval_mem',0)
        self.interval_disk_use = info_interval.get('interval_disk_use',0)
        self.interval_disk_iops = info_interval.get('interval_disk_iops',0)
        self.interval_netcard = info_interval.get('interval_netcard',0)
        self.interval_system = info_interval.get('interval_system',0)

    def is_alive(self):
        ret = Common.is_alive(self.hostname)
        return ret

    def loop(self,interval):
        def _loop(func):
            def run(*args,**kwargs):
                ret = func(*args,**kwargs)
            return run
        return _loop

    def monitor(self):
        pass


class Monitor():
    def __init__(self):
        self.list_hostobj = []

    def _initdb(self):
        for host in self.list_hostobj:
            hostname = host.hostname
            ip = host.ip
            if not HostDB.objects.filter(hostname=hostname):
                HostDB.objects.create(hostname=hostname,ip=ip)

    def _monitor(self):
        for host in self.list_hostobj:
            if host.is_alive():
                pass

    def start(self):
        cf = Config()
        tmp_ret = cf.init_config()
        assert tmp_ret == 0,'config init faild'
        self.list_hostobj = cf.list_hostobj
        self._initdb()



