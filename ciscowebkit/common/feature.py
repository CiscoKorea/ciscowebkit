'''
Created on 2016. 7. 27.

@author: "comfact"
'''

from ciscowebkit.common.abstract import __Feature__

class Feature(__Feature__):
    
    def __init__(self, tick=0, icon='fa-file'):
        __Feature__.__init__(self, tick, icon)
        
class SubFeature(Feature):
    
    def __init__(self, tick=0, icon='fa-file'):
        Feature.__init__(self, tick, icon)