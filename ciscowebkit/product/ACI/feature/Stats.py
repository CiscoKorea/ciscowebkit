'''
Created on 2016. 7. 5.

@author: "comfact"
'''

from ciscowebkit.common import Feature, SubFeature

class Stats(Feature):
    
    def __init__(self): Feature.__init__(self, 'fa-eye')

class INTF_Util(SubFeature):
    
    '''Interface Utilization'''
    
    def __init__(self): SubFeature.__init__(self)
        
    def action(self, request):
        return 'Intf Util Service'
    
class EPG_Util(SubFeature):
    
    '''Endpoint Group Utilization'''
    
    def __init__(self): SubFeature.__init__(self)
    
    def action(self, request):
        return 'EPG Util Service'