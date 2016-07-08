'''
Created on 2016. 7. 5.

@author: "comfact"
'''

from ciscowebkit.common.platform import Feature

class INTF_Util(Feature):
    
    '''Interface Utilization'''
    
    def __init__(self, **kargs): Feature.__init__(self, **kargs)
        
    def action(self, request):
        return 'Intf Util Service'
    
class EPG_Util(Feature):
    
    '''Endpoint Group Utilization'''
    
    def __init__(self, **kargs): Feature.__init__(self, **kargs)
    
    def action(self, request):
        return 'EPG Util Service'