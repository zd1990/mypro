from __future__ import unicode_literals

from django.db import models

# Create your models here.

class HostDB(models.Model):
    ip = models.CharField(default='',max_length=20)
    hostname = models.CharField(default='',max_length=100)

class DiskNameDB(models.Model):
    name = models.CharField(default='',max_length=20)

class NicNameDB(models.Model):
    name = models.CharField(default='',max_length=100)

class CpuDB(models.Model):
    host = models.ForeignKey(HostDB)
    name = models.FloatField()
    usr = models.FloatField()
    nice = models.FloatField()
    system = models.FloatField()
    iowait = models.FloatField()
    irq = models.FloatField()
    soft = models.FloatField()
    idle = models.FloatField()
    times = models.TimeField(auto_now_add=True)

class DiskDB(models.Model):
    disk = models.ForeignKey(DiskNameDB)
    host = models.ForeignKey(HostDB)
    r_ops = models.FloatField()
    w_ops = models.FloatField()
    r_bps = models.FloatField()
    w_bps = models.FloatField()
    times = models.TimeField(auto_now_add=True)

class MemDB(models.Model):
    host = models.ForeignKey(HostDB)
    total = models.IntegerField()
    available = models.IntegerField()
    free = models.IntegerField()
    buffers = models.IntegerField()
    cached = models.IntegerField()
    times = models.TimeField(auto_now_add=True)

class NicDB(models.Model):
    host = models.ForeignKey(HostDB)
    nic = models.ForeignKey(NicNameDB)
    r_byte = models.IntegerField()
    w_byte = models.IntegerField()
    r_pack = models.IntegerField()
    w_pack = models.IntegerField()
    times = models.TimeField(auto_now_add=True)

class SysloadDB(models.Model):
    host = models.ForeignKey(HostDB)
    m1 = models.FloatField()
    m5 = models.FloatField()
    m15 = models.FloatField()
    times = models.TimeField(auto_now_add=True)