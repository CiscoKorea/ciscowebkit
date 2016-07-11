'''
Created on 2016. 7. 5.

@author: "comfact"
'''

from ciscowebkit.common import Feature, SubFeature

class Feature2(Feature):

    def __init__(self): Feature.__init__(self, 'fa-car')

class Object_1(SubFeature):
    
    '''Sub Feature Object 1'''
    
    def __init__(self): SubFeature.__init__(self, 'fa-truck')
        
    def action(self, request):
        return 'Sub Feature Object 1 Action'
    
class Object_2(SubFeature):
    
    '''Sub Feature Object 2'''
    
    def __init__(self): SubFeature.__init__(self, 'fa-bus')
    
    def action(self, request):
        return 'Sub Feature Object 2 Action'
