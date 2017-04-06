# coding:utf-8
import socket

__author__ = 'DingZhang(dingzhang1990@gmail.com)'

import os
import time
import paramiko
import pandas as pd

from zdpro.middleware.common import exec_shell, dlog, plog


class Cpu(object):
    def __init__(self):
        pass

    @classmethod
    @plog('Disk.info_cpu_type')
    def info_cpu_type(cls,hostname,port=''):
        '''
        获取cpu型号
        :return: {"cpu0":"xxxx","cpu1":"xxxx"}
        '''
        ret = {}
        cmd = "timeout 30 cat /proc/cpuinfo|grep 'model name'|cut -d: -f 2"
        out = Common.command(cmd,hostname,port)
        tmp_type_list = out.read().strip().split('\n')
        type_list = [i.strip() for i in tmp_type_list]
        n = 0
        for types in type_list:
            ret.update({"cpu%s" % n: types})
        return ret

    @classmethod
    @plog('Cpu_info_cpu_load')
    def info_cpu_load(cls,hostname,port=''):
        """
        获取cpu负载
        :return: {"cpu":{"user":"","nice":"","system":"","idle":"","iowait":"","irq":"","softirq":""},"cpu0"....}
        """
        ret = {}
        cmd = "timeout 30 cat /proc/stat|awk '/^cpu/ {print}'"
        out = Common.command(cmd,hostname,port)
        tmp_list = [i.strip() for i in out.read().strip().split('\n')]
        for line in tmp_list:
            tmp_list_1 = line.split()
            cpu_id = tmp_list_1[0]
            user = int(tmp_list_1[1])
            nice = int(tmp_list_1[2])
            system = int(tmp_list_1[3])
            idle = int(tmp_list_1[4])
            iowait = int(tmp_list_1[5])
            irq = int(tmp_list_1[6])
            softirq = int(tmp_list_1[7])
            cputime = user + nice + system + idle + iowait + irq + softirq
            user_s = "%.2f" % (user * 100 / cputime)
            nice_s = "%.2f" % (nice * 100 / cputime)
            system_s = "%.2f" % (system * 100 / cputime)
            idle_s = "%.2f" % (idle * 100 / cputime)
            iowait_s = "%.2f" % (iowait * 100 / cputime)
            irq_s = "%.2f" % (irq * 100 / cputime)
            softirq_s = "%.2f" % (softirq * 100 / cputime)
            ret = {"name":cpu_id,"usr": user_s, "nice": nice_s, "system": system_s, "idle": idle_s,
                                   "iowait": iowait_s, "irq": irq_s, "softirq": softirq_s}
            yield ret


class Mem(object):
    def __init_(self):
        pass

    @classmethod
    @plog('Mem.info_mem_use')
    def info_mem_use(cls,hostname,port=""):
        '''
        获取内存使用情况
        :return:{"memTotal":"","memFree":"","memAvailable":"","Buffers":"","Cached":"","SwapCached":""}
        '''
        ret = 0
        cmd = "timeout 30 cat /proc/meminfo|awk 'NR<7 {print $2}'"
        out = Common.command(cmd,hostname,port)
        tmp_list = [i.strip() for i in out.read().strip().split('\n')]
        memTotal = tmp_list[0]
        memFree = tmp_list[1]
        memAvailable = tmp_list[2]
        Buffers = tmp_list[3]
        Cached = tmp_list[4]
        SwapCached = tmp_list[5]
        ret = {"memTotal": memTotal, "memFree": memFree, "memAvailable": memAvailable, "Buffers": Buffers,
               "Cached": Cached, "SwapCached": SwapCached}
        return ret


class NetCard(object):
    def __init__(self):
        pass

    @classmethod
    @plog('NetCard.info_nic_get')
    def info_nic_get(cls,hostname,port=''):
        '''
        获取网卡名
        :return:
        '''
        cmd = "timeout 30 cat /proc/net/dev|grep -v lo|tr : \" \"|awk 'NR>2 {print $1}'"
        out = Common.command(cmd,hostname,port)
        ret = [i.strip() for i in out.readlines()]
        return ret

    @classmethod
    @plog('NetCard.info_eth_rw')
    def info_eth_rw(cls,hostname,port):
        """
        获取网卡速率
        :return:[[nic_in,nic_out,nic_name]]
        """
        ret = {}
        def _dataframe(tmp_list):
            pandas_list = [i.split() for i in tmp_list]
            unames = ['nic_name','nic_in_byte','nic_in_packets','nic_out_byte','nic_out_packets']
            dataframe = pd.DataFrame(pandas_list,columns=unames)
            return dataframe

        cmd = "timeout 30 awk 'NR>2,gsub(/:/,\"\"){print $1,$2,$3,$10,$11}' /proc/net/dev"
        if Common.islocalhost(hostname):
            out_old,err,stat = exec_shell(cmd)
            assert stat == 0,"exec %s faild err:%s" % (cmd, err.read())
            time.sleep(1)
            out_now,err,stat = exec_shell(cmd)
            assert stat == 0,"exec %s faild err:%s" % (cmd, err.read())
        else:
            with RemoteSSH(hostname,port) as rs:
                out_old = rs.exec_cmd(cmd)
                time.sleep(1)
                out_now = rs.exec_cmd(cmd)
        tmp_list_old = out_old.read().strip().split('\n')
        dataframe_old = _dataframe(tmp_list_old)
        dataframe_old[['nic_in_byte','nic_in_packets','nic_out_byte','nic_out_packets']] = dataframe_old[['nic_in_byte','nic_in_packets','nic_out_byte','nic_out_packets']].astype(int)
        tmp_list_now = out_now.read().strip().split('\n')
        dataframe_now = _dataframe(tmp_list_now)
        dataframe_now[['nic_in_byte','nic_in_packets','nic_out_byte','nic_out_packets']] = dataframe_now[['nic_in_byte','nic_in_packets','nic_out_byte','nic_out_packets']].astype(int)
        ret_data = (dataframe_now.iloc[:,1:] - dataframe_old.iloc[:,1:]).join(dataframe_now['nic_name'])
        ret_json = ret_data.to_json(orient='values')
        return ret_json


class Disk(object):
    def __init__(self):
        pass

    @classmethod
    @plog('Disk.info_disk_overview')
    def info_disk_overview(cls,hostname,port=''):
        '''
        获取所有磁盘
        :return:
        '''
        # cmd = "timeout 30 fdisk -l|awk -F: '/^Disk \/dev/{print $1}'|cut -d ' ' -f 2 >/dev/null 2>&1"
        cmd = "lsblk|grep disk|awk '{print $1}'"
        # out, err, stat = exec_shell(cmd)
        # assert stat == 0, "cmd:%s execl faild %s" % (cmd, err.read())
        out = Common.command(cmd,hostname,port)
        dev_list_tmp = out.read().strip().split('\n')
        dev_list = [i.strip() for i in dev_list_tmp]
        ret = dev_list
        return ret

    @classmethod
    @plog('Disk.info_disk_use')
    def info_disk_use(cls, devpath):
        '''
        获取磁盘容量
        :param dev:
        :return:
        '''
        import os
        st = os.statvfs(devpath)
        free = (st.f_bavail * st.f_frsize)
        total = (st.f_blocks * st.f_frsize)
        used = (st.f_blocks - st.f_bfree) * st.f_frsize
        ret = {"free": free, "total": total, "used": used}
        return ret

    @classmethod
    @plog('Disk.info_disk_iops')
    def info_disk_iops(cls,hostname,port,dev="*"):
        '''
        获取磁盘iops和读写MBPS
        :param dev:
        :return:[['r_ops','r_merge','r_bps','r_time','w_ops','w_merge','w_bps','w_time','disk_name']]
        '''
        def _dataframe(tmp_list):
            pandas_list = [i.split() for i in tmp_list]
            unames = ['disk_name','r_ops','r_merge','r_bps','r_time','w_ops','w_merge','w_bps','w_time']
            dataframe = pd.DataFrame(pandas_list,columns=unames)
            return dataframe
        ret = {}
        block_size = 512
        cmd = "cat /proc/diskstats |awk '{print $3}'"
        # out, err, stat = exec_shell(cmd)
        out = Common.command(cmd,hostname,port)
        tmp_list = out.read().strip().split('\n')
        tmp_list = [i.strip() for i in tmp_list]
        if dev == "*":
            devlist = Disk.info_disk_overview(hostname,port)
        else:
            devlist = dev.spilt(",")
        devlist = [i.split("/")[-1] for i in devlist if i.split("/")[-1] in tmp_list]
        cmd = "awk '{print $3,$4,$5,$6,$7,$8,$9,$10,$11}' /proc/diskstats"
        if Common.islocalhost(hostname):
            out_old,err,stat = exec_shell(cmd)
            assert stat==0,"cmd:%s execl faild %s" % (cmd, err.read())
            time.sleep(1)
            out_now,err,stat = exec_shell(cmd)
            assert stat==0,"cmd:%s execl faild %s" % (cmd, err.read())
        else:
            with RemoteSSH(hostname,port) as rs:
                out_old = rs.exec_cmd(cmd)
                time.sleep(1)
                out_now = rs.exec_cmd(cmd)
        tmp_list_old = [i for i in out_old.read().strip().split('\n')]
        dataframe_old = _dataframe(tmp_list_old)
        tmp_list_now = [i for i in out_now.read().strip().split('\n')]
        dataframe_now = _dataframe(tmp_list_now)
        ret_data = (dataframe_now.iloc[:,1:].astype(int) - dataframe_old.iloc[:,1:].astype(int)).join(dataframe_now['disk_name'])
        ret_data['r_bps'] = ret_data['r_bps']*block_size
        ret_data['w_bps'] = ret_data['w_bps']*block_size
        ret_json = ret_data.to_json(orient='values')
        return ret_json


class System(object):
    def __init__(self):
        pass

    @classmethod
    @plog('System.info_sys_load')
    def info_sys_load(cls,hostname,port):
        '''
        获取系统负载
        :return:
        '''
        ret = {}
        cmd = "timeout 30 cat /proc/loadavg |awk '{print $1,$2,$3}'"
        out = Common.command(cmd,hostname,port)
        list_load = [i.strip() for i in out.read().split()]
        ret = {"1m": list_load[0], "5m": list_load[1], "15m": list_load[2]}
        return ret

    @classmethod
    def get_hostname(self):
        '''
        获取机器hostname
        :return:
        '''
        hostname = socket.gethostname()
        return hostname

class Common(object):
    def __init__(self):
        pass

    @classmethod
    def islocalhost(cls,hostname):
        local_hostname = System.get_hostname()
        return True if local_hostname == hostname else False

    @classmethod
    def command(cls,cmd,hostname='',port=''):
        if not hostname or Common.islocalhost(hostname):
            out,err,stat = exec_shell(cmd)
            assert stat == 0,"exec %s faild err:%s"%(cmd,err.read())
        else:
            with RemoteSSH(hostname,port) as rs:
                out = rs.exec_cmd(cmd)
        return out

    @classmethod
    def is_alive(cls,hostname):
        cmd = "ping -c 1 %s"%hostname
        out,err,stat = exec_shell(cmd)
        ret = True if not stat else False
        return ret



class RemoteSSH():
    def __init__(self,address,port):
        self.address = address
        self.port = port if port else 22

    def __connect(self):
        self.ssh_fd = paramiko.SSHClient()
        self.ssh_fd.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.ssh_fd.connect(self.address,port=self.port,timeout=10)

    def __enter__(self):
        self.__connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        if exc_val:
            dlog("RemoteSSH err:%s"%exc_val)

    def connect(self):
        self.__connect()

    def close(self):
        self.ssh_fd.close()

    def exec_cmd(self,cmd):
        stdin,stdout,stderr = self.ssh_fd.exec_command(cmd)
        assert not stderr.read(),'cmd:%s exec faild,err:%s'%(cmd,stderr.read())
        return stdout

