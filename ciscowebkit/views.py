'''
Created on 2016. 7. 8.

@author: "comfact"
'''

from django.http import HttpResponse
from ciscowebkit.common.platform import Manager

# Create your views here.

def action(request):
    return Manager.GET().__action_debug__(request)