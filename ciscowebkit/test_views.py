'''
Created on 2016. 7. 5.

@author: "comfact"
'''

from django.shortcuts import render
from django.http import HttpResponse
from django.template  import Context, loader
from django.conf import settings

# Create your views here.

def origin(request):
    template = loader.get_template('bootstrap/index.html')
    return HttpResponse(template.render())

def cisco(request):
    template = loader.get_template('ciscoview.html')
    return HttpResponse(template.render())

def reqview(request):
    print 'PATH', request.path
    print 'PATH_INFO', request.path_info
    print 'METHOD', request.method
    return HttpResponse('NULL')