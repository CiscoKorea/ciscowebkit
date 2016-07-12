#-*- coding: utf-8 -*-
'''
Created on 2016. 7. 11.

@author: "comfact"
'''

from ciscowebkit.common.pygics import inf
from ciscowebkit.common import Feature
from ciscowebkit.common.platform import Manager

class ChartTest(Feature):
    
    '''Single Feature 1'''
    
    def __init__(self, **kargs):
        Feature.__init__(self, 'fa-archive', **kargs)
        
    def get(self, request):
        
        data1 = Manager.TableData('Feature 1-1', panel=Manager.PANEL.INFO)
        data1.setHead('Col1', 'Col2', 'Col3')
        data1.addData('1', '2', '3', type=Manager.TableData.ACTIVE)
        data1.addData('A', 'B', 'C', type=Manager.TableData.DANGER)
        data1.addData('a', 'b', 'c')
        data1.addData('가', '나', '다')
        
        data2 = Manager.TableData('Feature 1-2', panel=Manager.PANEL.DANGER)
        data2.setHead('Col1', 'Col2', 'Col3')
        data2.addData('1', '2', '3', type=Manager.TableData.SUCCESS)
        data2.addData('A', 'B', 'C', type=Manager.TableData.WARNING)
        data2.addData('a', 'b', 'c')
        data1.addData('가', '나', '다')
        
        line = Manager.LineData('LineData', panel=Manager.PANEL.SUCCESS)
        line.setXY(0, 5, 1, 0, 100, 10)
        line.addLine('Line1')
        line.addData('Line1', 1, 10)
        line.addData('Line1', 2, 20)
        line.addData('Line1', 3, 30)
        line.addLine('Line2')
        line.addData('Line2', 1, 50)
        line.addData('Line2', 2, 70)
        line.addData('Line2', 3, 90)
        
        donut = Manager.DonutData('DonutData', panel=Manager.PANEL.WARN)
        donut.addData('Dunkin', 30, 'red')
        donut.addData('Crispy', 40, 'blue')
        
        lv = Manager.ListView()
        lv.addView(data1)
        lv.addView(data2)
        lv.addView(line)
        lv.addView(donut)
        
        return Manager.render(lv)
