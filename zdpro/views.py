from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse
from tasks import test

def plus(request,x,y):
    ret = test(int(x),int(y))
    return HttpResponse("result=%s"%ret)
