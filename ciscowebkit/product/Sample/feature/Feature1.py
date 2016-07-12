'''
Created on 2016. 7. 11.

@author: "comfact"
'''

from ciscowebkit.common import Feature

class Feature1(Feature):
    
    '''Single Feature 1'''
    
    def __init__(self, **kargs): Feature.__init__(self, 'fa-beer', **kargs)
        
    def get(self, request):
        return 'Single Feature 1 Action'
