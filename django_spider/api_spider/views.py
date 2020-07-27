from django.shortcuts import render

# Create your views here.

from django.http import HttpResponse


def spider_api(request):
    return HttpResponse('spider_message')