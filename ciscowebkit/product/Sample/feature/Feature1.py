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
        
        data1 = Manager.TableData('Feature 1-1')
        data1.setHead('Col1', 'Col2', 'Col3')
        data1.addData('1', '2', '3', type='warning')
        data1.addData('A', 'B', 'C', type='danger')
        data1.addData('a', 'b', 'c')
        
        data2 = Manager.TableData('Feature 1-2')
        data2.setHead('Col1', 'Col2', 'Col3')
        data2.addData('1', '2', '3', type='warning')
        data2.addData('A', 'B', 'C', type='danger')
        data2.addData('a', 'b', 'c')
        
        lv = Manager.ListView()
        lv.addView(data1)
        lv.addView(data2)
        
        return Manager.render(lv)
