'''
Created on 2016. 7. 5.

@author: "comfact"
'''

from ciscowebkit.common import *

class Feature4(Feature):

    def __init__(self): Feature.__init__(self, 0, 'fa-tree')

class Object_1(SubFeature):
    
    '''Sub Feature Object 1'''
    
    def __init__(self): SubFeature.__init__(self, 0, 'fa-umbrella')
        
    def get(self, request):
        return Text('Sub Feature Object 1 Action')
    
class Object_2(SubFeature):
    
    '''Sub Feature Object 2'''
    
    def __init__(self): SubFeature.__init__(self, 0, 'fa-trophy')
    
    def get(self, request):
        return Text('Sub Feature Object 2 Action')