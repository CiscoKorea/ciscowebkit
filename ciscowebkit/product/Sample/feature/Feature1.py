'''
Created on 2016. 7. 11.

@author: "comfact"
'''

from ciscowebkit.common import Feature
from ciscowebkit.product.Sample.models import Info, InfoData
from ciscowebkit.common.platform import Manager

class Feature1(Feature):
    
    '''Single Feature 1'''
    
    def __init__(self, **kargs):
        Feature.__init__(self, 'fa-beer', **kargs)
        
    def get(self, request):
        
        data = Manager.TableData()
        data.setTitle('Feature1')
        data.setHead('Col1', 'Col2', 'Col3')
        data.addData('1', '2', '3', type='warning')
        data.addData('A', 'B', 'C', type='danger')
        data.addData('a', 'b', 'c')
        
        return Manager.render(data)
