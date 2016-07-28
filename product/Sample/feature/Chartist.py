#-*- coding: utf-8 -*-
'''
Created on 2016. 7. 19.

@author: "comfact"
'''

from ciscowebkit.common import *

class Chartist(Feature):
    
    '''Chartist Elements'''
    
    def __init__(self, **kargs):
        Feature.__init__(self, 3, 'fa-archive', **kargs)
        
    def get(self, requset, *cmd):
        lo = Layout()
        
        lo.addRow()
        p1 = ChartistPie(title='Pie Pure').add('Jaws', 15).add('Screw', 2).add('Candy', 29).add('Dwaeji', 10).add('Babam', 20)
        p2 = ChartistPie(title='Pie Ani').add('Jaws', 15).add('Screw', 2).add('Candy', 29).add('Dwaeji', 10).add('Babam', 20).ani()
        d1 = ChartistPie(title='Donut Pure').add('Jaws', 15).add('Screw', 2).add('Candy', 29).add('Dwaeji', 10).add('Babam', 20)
        d2 = ChartistPie(title='Donut Stroke Ani').add('Jaws', 15).add('Screw', 2).add('Candy', 29).add('Dwaeji', 10).add('Babam', 20).stroke(40).ani()
        lo.addCol(Panel('Chartist Hbar', Layout().addRow().addCol(p1).addRow().addCol(p2)), scr=Layout.SMALL, size=6)
        lo.addCol(Panel('Chartist Hbar', Layout().addRow().addCol(d1).addRow().addCol(d2)), scr=Layout.SMALL, size=6)
        
        lo.addRow()
        cl = ChartistLine('Line1', 'Line2', 'Line3', title='Sample Line').grid(0, 100).ani()
        cl.add('1', 10, 20, 15).add('2', 11, 19, 2).add('3', 12, 18, 29).add('4', 13, 17, 10).add('5', 14, 16, 20)
        ca = ChartistArea('Line1', 'Line2', 'Line3', title='Sample Area').ani()
        ca.add('1', 10, 20, 15).add('2', 11, 19, 2).add('3', 12, 18, 29).add('4', 13, 17, 10).add('5', 14, 16, 20)
        lo.addCol(Panel('Chartist Line', Layout().addRow().addCol(cl).addRow().addCol(ca)))
        
        lo.addRow()
        vb1 = ChartistVBar('Line1', 'Line2', 'Line3', title='VBar Pure')
        vb1.add('1', 10, 20, 15).add('2', 11, 19, 2).add('3', 12, 18, 29).add('4', 13, 17, 10).add('5', 14, 16, 20)
        vb2 = ChartistVBar('Line1', 'Line2', 'Line3', title='VBar Grid & Stroke').grid(0, 100).stroke(40, 20).ani()
        vb2.add('1', 10, 20, 15).add('2', 11, 19, 2).add('3', 12, 18, 29).add('4', 13, 17, 10).add('5', 14, 16, 20)
        vb3 = ChartistVBar('Line1', 'Line2', 'Line3', title='VBar Stack').stack()
        vb3.add('1', 10, 20, 15).add('2', 11, 19, 2).add('3', 12, 18, 29).add('4', 13, 17, 10).add('5', 14, 16, 20)
        vb4 = ChartistVBar(title='VBar Linear').ani()
        vb4.add('Jaws', 15).add('Screw', 2).add('Candy', 29).add('Dwaeji', 10).add('Babam', 20)
        lo.addCol(Panel('Chartist Vbar', Layout().addRow().addCol(vb1).addRow().addCol(vb2).addRow().addCol(vb3).addRow().addCol(vb4)))
        
        lo.addRow()
        hb1 = ChartistHBar('Line1', 'Line2', 'Line3',title='HBar Pure')
        hb1.add('1', 10, 20, 15).add('2', 11, 19, 2).add('3', 12, 18, 29).add('4', 13, 17, 10).add('5', 14, 16, 20)
        hb2 = ChartistHBar('Line1', 'Line2', 'Line3', title='HBar Grid & Stroke').grid(0, 100).stroke(10, 10).ani()
        hb2.add('1', 10, 20, 15).add('2', 11, 19, 2).add('3', 12, 18, 29).add('4', 13, 17, 10).add('5', 14, 16, 20)
        hb3 = ChartistHBar('Line1', 'Line2', 'Line3', title='HBar Stack').stack()
        hb3.add('1', 10, 20, 15).add('2', 11, 19, 2).add('3', 12, 18, 29).add('4', 13, 17, 10).add('5', 14, 16, 20)
        hb4 = ChartistHBar(title='HBar Linear').ani()
        hb4.add('Jaws', 15).add('Screw', 2).add('Candy', 29).add('Dwaeji', 10).add('Babam', 20)
        lo.addCol(Panel('Chartist Hbar', Layout().addRow().addCol(hb1).addRow().addCol(hb2).addRow().addCol(hb3).addRow().addCol(hb4)))
        
        return lo
        
        
        