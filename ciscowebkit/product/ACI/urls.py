'''
Created on 2016. 7. 4.

@author: "comfact"
'''

from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^', views.action),
]
