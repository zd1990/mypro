# coding:utf-8
__author__ = 'DingZhang(dingzhang1990@gmail.com)'

import os
import time

from zdpro.middleware.common import exec_shell, dlog, plog


class Cpu(object):
    def __init__(self):
        pass

    @classmethod
    @plog('Disk.info_cpu_type')
    def info_cpu_type(cls):
        '''
        获取cpu型号
        :return: {"cpu0":"xxxx","cpu1":"xxxx"}
        '''
        ret = {}
        cmd = "timeout 30 cat /proc/cpuinfo|grep 'model name'|cut -d: -f 2"
        out, err, stat = exec_shell(cmd)
        assert stat == 0, "cmd:%s exec faild err:%s" % (cmd, err.read())
        tmp_type_list = out.readlines()
        type_list = [i.strip() for i in tmp_type_list]
        n = 0
        for types in type_list:
            ret.update({"cpu%s" % n: types})
        return ret

    @classmethod
    @plog('Cpu_info_cpu_load')
    def info_cpu_load(cls):
        """
        获取cpu负载
        :return: {"cpu":{"user":"","nice":"","system":"","idle":"","iowait":"","irq":"","softirq":""},"cpu0"....}
        """
        ret = {}
        cmd = "timeout 30 cat /proc/stat|awk '/^cpu/ {print}'"
        out, err, stat = exec_shell(cmd)
        assert stat == 0, "cmd:%s exec faild err:%s" % (cmd, err.read())
        tmp_list = [i.strip() for i in out.readlines()]
        for line in tmp_list:
            tmp_list_1 = line.split()
            name_cpu = tmp_list_1[0]
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
            ret.update({name_cpu: {"user": user_s, "nice": nice_s, "system": system_s, "idle": idle_s,
                                   "iowait": iowait_s, "irq": irq_s, "softirq": softirq_s}})
        return ret


class Mem(object):
    def __init_(self):
        pass

    @classmethod
    @plog('Mem.info_mem_use')
    def info_mem_use(cls):
        '''
        获取内存使用情况
        :return:{"memTotal":"","memFree":"","memAvailable":"","Buffers":"","Cached":"","SwapCached":""}
        '''
        ret = 0
        cmd = "timeout 30 cat /proc/meminfo|awk 'NR<7 {print $2}'"
        out, err, stat = exec_shell(cmd)
        assert stat == 0, "exec %s faild err:%s" % (cmd, err.read())
        tmp_list = [i.strip() for i in out.readlines()]
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
    def info_nic_get(cls):
        '''
        获取网卡名
        :return:
        '''
        cmd = "timeout 30 cat /proc/net/dev|grep -v lo|tr : \" \"|awk 'NR>2 {print $1}'"
        out, err, stat = exec_shell(cmd)
        assert stat == 0, "exec %s faild err:%s" % (cmd, err.read())
        ret = [i.strip() for i in out.readlines()]
        return ret

    @classmethod
    @plog('NetCard.info_eth_rw')
    def info_eth_rw(cls):
        """
        获取网卡速率
        :return:{"name":{"out":"","in":""},}
        """
        ret = {}
        cmd1 = "timeout 30 cat /proc/net/dev|grep -v lo|tr : \" \"|awk 'NR>2 {print $1}'"
        cmd2 = "timeout 30 cat /proc/net/dev|grep -v lo|tr : \" \"|awk 'NR>2 {print $2}'"
        cmd3 = "timeout 30 cat /proc/net/dev|grep -v lo|tr : \" \"|awk 'NR>2 {print $10}'"
        out, err, stat = exec_shell(cmd1)
        assert stat == 0, "exec %s faild err:%s" % (cmd1, err.read())
        list_devs = [i.strip() for i in out.readlines()]
        out, err, stat = exec_shell(cmd2)
        assert stat == 0, "exec %s faild err:%s" % (cmd2, err.read())
        in_old_list = [i.strip() for i in out.readlines()]
        out, err, stat = exec_shell(cmd3)
        assert stat == 0, "exec %s faild err:%s" % (cmd3, err.read())
        out_old_list = [i.strip() for i in out.readlines()]
        time.sleep(1)
        out, err, stat = exec_shell(cmd2)
        assert stat == 0, "exec %s faild err:%s" % (cmd2, err.read())
        in_now_list = [i.strip() for i in out.readlines()]
        out, err, stat = exec_shell(cmd3)
        assert stat == 0, "exec %s faild err:%s" % (cmd3, err.read())
        out_now_list = [i.strip() for i in out.readlines()]
        num = len(list_devs)
        for i in range(0, num, 1):
            devname = list_devs[i]
            eth_in = int(in_now_list[i]) - int(in_old_list[i])
            eth_out = int(out_now_list[i]) - int(out_old_list[i])
            ret.update({devname: {"in": eth_in, "out": eth_out}})
        return ret


class Disk(object):
    def __init__(self):
        pass

    @classmethod
    @plog('Disk.info_disk_overview')
    def info_disk_overview(cls):
        '''
        获取所有磁盘
        :return:
        '''
        cmd = "timeout 30 fdisk -l|awk -F: '/^Disk \/dev/{print $1}'|cut -d ' ' -f 2"
        out, err, stat = exec_shell(cmd)
        assert stat == 0, "cmd:%s execl faild %s" % (cmd, err.read())
        dev_list_tmp = out.readlines()
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
        st = os.statvfs(devpath)
        free = (st.f_bavail * st.f_frsize)
        total = (st.f_blocks * st.f_frsize)
        used = (st.f_blocks - st.f_bfree) * st.f_frsize
        ret = {"free": free, "total": total, "used": used}
        return ret

    @classmethod
    @plog('Disk.info_disk_iops')
    def info_disk_ipos(cls, dev):
        '''
        获取磁盘iops和读写MBPS
        :param dev:
        :return:
        '''
        ret = {}
        block_size = 512
        io_dict_old = {}
        io_dict_now = {}
        cmd = "cat /proc/diskstats |awk '{print $3}'"
        out, err, stat = exec_shell(cmd)
        tmp_list = out.readlines()
        tmp_list = [i.strip() for i in tmp_list]
        if dev == "*":
            devlist = Disk.info_disk_overview()
        else:
            devlist = dev.spilt(",")
        devlist = [i.split("/")[-1] for i in devlist if i.split("/")[-1] in tmp_list]
        for dev in devlist:
            # $4为读扇区成功次数,$6为读扇区总数,$8为写扇区成功次数,$10为写扇区总数
            cmd1 = "grep '%s ' /proc/diskstats | awk '{print $4,$6}'" % dev
            cmd2 = "grep '%s ' /proc/diskstats | awk '{print $8,$10}'" % dev
            out, err, stat = exec_shell(cmd1)
            tmp_list = out.read().strip().split()
            old_rio = tmp_list[0]
            old_r_block = tmp_list[1]
            out, err, stat = exec_shell(cmd2)
            tmp_list = out.read().strip().split()
            old_wio = tmp_list[0]
            old_w_block = tmp_list[1]
            io_dict_old.update(
                {"old_rio_%s" % dev: old_rio, "old_wio_%s" % dev: old_wio, "old_r_block_%s" % dev: old_r_block,
                 "old_w_block_%s" % dev: old_w_block})
        time.sleep(1)
        for dev in devlist:
            cmd1 = "grep '%s ' /proc/diskstats | awk '{print $4,$6}'" % dev
            cmd2 = "grep '%s ' /proc/diskstats | awk '{print $8,$10}'" % dev
            out, err, stat = exec_shell(cmd1)
            tmp_list = out.read().strip().split()
            now_rio = tmp_list[0]
            now_r_block = tmp_list[1]
            out, err, stat = exec_shell(cmd2)
            tmp_list = out.read().strip().split()
            now_wio = tmp_list[0]
            now_w_blcok = tmp_list[1]
            rio = int(now_rio) - int(io_dict_old["old_rio_%s" % dev])
            wio = int(now_wio) - int(io_dict_old["old_wio_%s" % dev])
            r_byte = (int(now_r_block) - int(io_dict_old["old_r_block_%s" % dev])) * block_size
            w_byte = (int(now_w_blcok) - int(io_dict_old["old_w_block_%s" % dev])) * block_size
            ret.update({dev: {"rio": rio, "wio": wio, "r_byte": r_byte, "w_byte": w_byte}})
        return ret


class System(object):
    def __init__(self):
        pass

    @classmethod
    @plog('Ssytem.info_sys_load')
    def info_sys_load(cls):
        '''
        获取系统负载
        :return:
        '''
        ret = {}
        cmd = "timeout 30 cat /proc/loadavg |awk '{print $1,$2,$3}'"
        out, err, stat = exec_shell(cmd)
        assert stat == 0, "exec %s faild err:%s" % (cmd, err.read())
        list_load = [i.strip() for i in out.read().split()]
        ret = {"1m": list_load[0], "5m": list_load[1], "15m": list_load[2]}
        return ret
