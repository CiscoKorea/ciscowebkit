'''
Created on 2016. 7. 8.

@author: "comfact"
'''
from django.template import Template, Context, loader
from django.http import HttpResponse
from ciscowebkit.common.engine import Engine

# Create your views here.

def action(request):
    return Engine.GET().__action__(request)

def test(request):
    return HttpResponse(loader.get_template('test.html').render())

class DisableCSRF(object):
    def process_request(self, request):
        setattr(request, '_dont_enforce_csrf_checks', True)