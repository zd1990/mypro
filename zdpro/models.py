from __future__ import unicode_literals

from django.db import models

# Create your models here.

class Host(models.Model):
    ip = models.CharField(default='',max_length=20)
    hostname = models.CharField(default='',max_length=100)

class DiskName(models.Model):
    name = models.CharField(default='',max_length=20)

class NicName(models.Model):
    name = models.CharField(default='',max_length=100)

class Cpu(models.Model):
    host_id = models.ForeignKey(Host)
    cpu_num = models.IntegerField()
    usr = models.FloatField()
    nice = models.FloatField()
    sys = models.FloatField()
    iowait = models.FloatField()
    irq = models.FloatField()
    soft = models.FloatField()
    steal = models.FloatField()
    quest = models.FloatField()
    gnice = models.FloatField()
    idle = models.FloatField()
    times = models.TimeField()

class Disk(models.Model):
    disk_id = models.ForeignKey(DiskName)
    host_id = models.ForeignKey(Host)
    r_ops = models.FloatField()
    w_ops = models.FloatField()
    r_bps = models.FloatField()
    w_bps = models.FloatField()
    times = models.TimeField()

class Mem(models.Model):
    host_id = models.ForeignKey(Host)
    total = models.IntegerField()
    used = models.IntegerField()
    free = models.IntegerField()
    times = models.TimeField()

class Nic(models.Model):
    host_id = models.ForeignKey(Host)
    nic_id = models.ForeignKey(NicName)
    r_byte = models.IntegerField()
    w_byte = models.IntegerField()
    r_pack = models.IntegerField()
    w_pack = models.IntegerField()
    times = models.TimeField()

class Sysload(models.Model):
    host_id = models.ForeignKey(Host)
    m1 = models.FloatField()
    m5 = models.FloatField()
    m15 = models.FloatField()
    times = models.TimeField()