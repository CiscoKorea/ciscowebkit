'''
Created on 2016. 7. 5.

@author: "comfact"
'''

from django.conf.urls import url
import test_views

urlpatterns = [
    url(r'^reqview/', test_views.reqview),
    url(r'^origin/', test_views.origin),
    url(r'^$', test_views.cisco),
]