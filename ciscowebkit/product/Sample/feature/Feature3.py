'''
Created on 2016. 7. 11.

@author: "comfact"
'''

from ciscowebkit.common import Feature

class Feature3(Feature):
    
    '''Single Feature 3'''
    
    def __init__(self, **kargs): Feature.__init__(self, 'fa-coffee', **kargs)
        
    def get(self, request):
        return 'Single Feature 3 Action'