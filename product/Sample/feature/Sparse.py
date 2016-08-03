'''
Created on 2016. 8. 1.

@author: "comfact"
'''

from ciscowebkit.common import *

class Sparse(Feature):
    
    '''Sparse Elements'''
    
    def __init__(self, **kargs):
        Feature.__init__(self, 3, 'fa-archive', **kargs)
        
    def get(self, request, *cmd):
        lo = Layout(
            Row(Panel('Justgage',
                JustGage(75, 0, 100, desc="SampleGage", height=500)
                ))
            )
        return lo
        
        
        