#-*- coding: utf-8 -*-
'''
Created on 2016. 7. 11.

@author: "comfact"
'''

from ciscowebkit.common import *

class Morris(Feature):
    
    '''Morris Elements'''
    
    def __init__(self, **kargs):
        Feature.__init__(self, 0, 'fa-archive', **kargs)
        
    def view(self):
        mv = Layout.View()
        
        mv.addRow().addCol(MorrisLine.View('Line Pure', panel=Panel.INFO))
        mv.addRow().addCol(MorrisLine.View('Line Opts', panel=Panel.INFO).optArea().optSmooth().optGrid(0, 40))
        mv.addRow().addCol(MorrisBar.View('Bar Pure', panel=Panel.INFO))
        mv.addRow().addCol(MorrisBar.View('Bar Opts', panel=Panel.INFO).optGrid(-10, 30))
        mv.addRow().addCol(MorrisDonut.View('Donut', panel=Panel.INFO))
        
        return mv
    
    def get(self, requset, *cmd):
        md = Layout.Data()
        
        md.add(MorrisLine.Data('Quater', 'Line1', 'Line2').add('2016 Q1', 10, 20).add('2016 Q2', 20, 15).add('2016 Q3', 5, 12).add('2016 Q4', 1, 20))
        md.add(MorrisLine.Data('Quater', 'Line1', 'Line2').add('2016 Q1', 10, 20).add('2016 Q2', 20, 15).add('2016 Q3', 5, 12).add('2016 Q4', 1, 20))
        md.add(MorrisBar.Data('IceCreate', 'Tasty', 'Visual').add('Jaws', 10, 20).add('Screw', 20, 15).add('Candy', 5, 12).add('Dwaji', 1, 20).add('Left', 20, 0).add('Right', 0, 20))
        md.add(MorrisBar.Data('IceCreate', 'Tasty', 'Visual').add('Jaws', 10, 20).add('Screw', 20, 15).add('Candy', 5, 12).add('Dwaji', 1, 20).add('Left', 20, 0).add('Right', 0, 20))
        md.add(MorrisDonut.Data().add('Dunkin', 30).add('Crispy', 40).add('Homemade', 20))

        return md
