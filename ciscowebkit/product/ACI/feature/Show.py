'''
Created on 2016. 7. 5.

@author: "comfact"
'''

from ciscowebkit.common.platform import Feature

class APIC(Feature):
    
    '''ACI Policy Controllers'''
    
    def __init__(self, **kargs): Feature.__init__(self, **kargs)
        
    def action(self, request):
        return 'APIC Service'
    
class Switch(Feature):
    
    '''ACI Leaf Nodes'''
    
    def __init__(self, **kargs): Feature.__init__(self, **kargs)
    
    def action(self, request):
        return 'Switch Service'
    
class EPG(Feature):
    
    '''Endpoint Groups'''
    
    def __init__(self, **kargs): Feature.__init__(self, **kargs)
    
    def action(self, request):
        return 'EPG Service'
    
class EP(Feature):
    
    '''Endpoint'''
    
    def __init__(self, **kargs): Feature.__init__(self, **kargs)
    
    def action(self, request):
        return 'EP Service'