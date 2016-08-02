#-*- coding: utf-8 -*-
'''
Created on 2016. 7. 5.

@author: "comfact"
'''

from ciscowebkit.common import *

class Show(Feature):
    
    def __init__(self): Feature.__init__(self, 0, 'fa-eye')

class Devices(SubFeature):
    
    '''Devices Information'''
    
    def __init__(self): SubFeature.__init__(self, 0, 'fa-gamepad')
    
    def get(self, request, *cmd):
        if len(APIC) == 0: return InfoBlock('데이터 없음', '연결된 APIC이 없습니다. Setting 메뉴에서 APIC 연결을 추가하세요.')
        return APICSET.getDevices()
