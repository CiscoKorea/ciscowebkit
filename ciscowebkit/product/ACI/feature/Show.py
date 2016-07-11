'''
Created on 2016. 7. 5.

@author: "comfact"
'''

from ciscowebkit.common import Feature, SubFeature

class Show(Feature):
    
    def __init__(self): Feature.__init__(self, 'fa-eye')

class APIC(SubFeature):
    
    '''ACI Policy Controllers'''
    
    def __init__(self): SubFeature.__init__(self, 'fa-gamepad')
        
    def action(self, request):
        return 'APIC Service'
    
class Switch(SubFeature):
    
    '''ACI Leaf Nodes'''
    
    def __init__(self): SubFeature.__init__(self, 'fa-cubes')
    
    def action(self, request):
        return 'Switch Service'
    
class EPG(SubFeature):
    
    '''Endpoint Groups'''
    
    def __init__(self): SubFeature.__init__(self, 'fa-square-o')
    
    def action(self, request):
        return 'EPG Service'
    
class EP(SubFeature):
    
    '''Endpoint'''
    
    def __init__(self): SubFeature.__init__(self, 'fa-dot-circle-o')
    
    def action(self, request):
        return 'EP Service'