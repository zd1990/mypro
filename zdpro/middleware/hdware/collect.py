# coding:utf-8
from zdpro.middleware.common import plog
from zdpro.models import CpuDB, DiskDB, MemDB, SysloadDB, NicDB, HostDB, DiskNameDB, NicNameDB

__author__ = 'DingZhang(dingzhang1990@gmail.com)'
from common import Cpu, Disk, Mem, NetCard, System


class Collect():
    def __init__(self):
        pass

    @classmethod
    @plog('Collect.get_cpu_load')
    def get_cpu_load(cls, hostname, port):
        ret = Cpu.info_cpu_load(hostname, port)
        assert ret != 1
        ret_list = []
        host_obj = HostDB.objects.get(hostname=hostname)
        for info in ret:
            db_ob = CpuDB(host=host_obj, name=info['name'], usr=info['usr'],
                          nice=info['nice'], system=info['system'], iowati=info['iowait'], irq=info['irq'],
                          soft=info['soft'], idle=info['idle'])
            ret_list.append(db_ob)
        CpuDB.objects.bulk_create(ret_list)

    @classmethod
    @plog('Collect.get_sysload')
    def get_sys_load(cls, hostname, port):
        ret = System.info_sys_load(hostname, port)
        assert ret != 1
        SysloadDB.objects.create(host=HostDB.objects.get(hostname=hostname), m1=ret['1m'], m5=ret['5m'], m15=ret['15m'])

    @classmethod
    @plog('Collect.get_mem_info')
    def get_mem_info(cls, hostname, port):
        ret = Mem.info_mem_use(hostname, port)
        assert ret != 1
        MemDB.objects.create(host=HostDB.objects.get(hostname=hostname), total=ret['memTotal'],
                             available=ret['memAvailable'], free=ret['memFree'], buffers=ret['Buffers'],cached=ret['Cached'])

    @classmethod
    @plog('Collect.get_nic_info')
    def get_nic_info(cls, hostname, port):
        ret = NetCard.info_eth_rw(hostname, port)
        assert ret != 1
        ret_list = []
        for info in ret:
            r_byte,r_packe,w_byte,w_pack,nic_name = info
            tmp_list = NicNameDB.objects.filter(name=nic_name)
            if tmp_list:
                nic_obj = tmp_list[0]
            else:
                NicNameDB.objects.create(name=nic_name)
                nic_obj = NicNameDB.objects.get(name=nic_name)
            ret_list.append(NicDB.objects.create(host=HostDB.objects.get(hostname=hostname),nic=nic_obj,r_byte=r_byte,r_pack=r_packe,w_byte=w_byte,w_pack=w_pack))
        NicDB.objects.bulk_create(ret_list)

    @classmethod
    @plog('Collect.get_disk_use')
    def get_disk_use(cls, hostname, port):
        pass

    @classmethod
    @plog('Collect.get_disk_info')
    def get_disk_info(cls, hostname, port):
        ret = Disk.info_disk_iops(hostname, port)
        ret_list = []
        host_obj = HostDB.objects.get(hostname=hostname)
        for info in ret:
            r_ops ,r_merge,r_bps,r_time,w_ops,w_merge,w_bps,w_time,disk_name = info
            tmp_list =DiskDB.objects.filter(name=disk_name)
            if tmp_list:
                disk_obj = tmp_list[0]
            else:
                DiskDB.objects.create(name=disk_name)
                disk_obj = DiskDB.objects.get(name=disk_name)
            ret_list.append(DiskDB(host=host_obj,disk=disk_obj,r_ops=r_ops,w_ops=w_ops,r_bps=r_bps,w_bps=w_bps))
        DiskDB.objects.bulk_create(ret_list)
