'''
Created on 2016. 7. 8.

@author: "comfact"
'''

from ciscowebkit.common.engine import Engine

# Create your views here.

def action(request):
    return Engine.GET().__action__(request)

class DisableCSRF(object):
    def process_request(self, request):
        setattr(request, '_dont_enforce_csrf_checks', True)