'''
Created on 2016. 7. 11.

@author: "comfact"
'''

from ciscowebkit.common import *

class Feature3(Feature):
    
    '''Single Feature 3'''
    
    def __init__(self, **kargs): Feature.__init__(self, 0, 'fa-coffee', **kargs)
        
    def get(self, request):
        return Text('Single Feature 3 Action')