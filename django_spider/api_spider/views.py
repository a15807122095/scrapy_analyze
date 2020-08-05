from django.shortcuts import render

# Create your views here.

from django.http import HttpResponse
import sys,os
# sys.path.append(os.path.dirname(__file__) + os.sep + '../../')

def spider_api(request):
    print(sys.path)
    return HttpResponse('message')