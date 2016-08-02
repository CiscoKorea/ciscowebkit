#-*- coding: utf-8 -*-
'''
Created on 2016. 7. 11.

@author: "comfact"
'''

from ciscowebkit.common import *

class Morris(Feature):
    
    '''Morris Elements'''
    
    def __init__(self, **kargs):
        Feature.__init__(self, 3, 'fa-archive', **kargs)
        
    def get(self, requset, *cmd):
        lo = Layout(
            Row(Panel('MorrisLine', Layout(
                Row(
                    Col(MorrisLine('Line1', 'Line2').add('2016 Q1', 10, 20).add('2016 Q2', 20, 15).add('2016 Q3', 5, 12).add('2016 Q4', 1, 20)),
                    Col(MorrisLine('Line1', 'Line2').grid(0, 100).add('2016 Q1', 10, 20).add('2016 Q2', 20, 15).add('2016 Q3', 5, 12).add('2016 Q4', 1, 20))
                    )
                ))),
            Row(Panel('MorrisArea', Layout(
                Row(
                    Col(MorrisArea('Line1', 'Line2').add('2016 Q1', 10, 20).add('2016 Q2', 20, 15).add('2016 Q3', 5, 12).add('2016 Q4', 1, 20)),
                    Col(MorrisArea('Line1', 'Line2').grid(0, 100).add('2016 Q1', 10, 20).add('2016 Q2', 20, 15).add('2016 Q3', 5, 12).add('2016 Q4', 1, 20))
                    )
                ))),
            Row(Panel('MorrisBar', Layout(
                Row(
                    Col(MorrisBar('Bar1', 'Bar2').add('2016 Q1', 10, 20).add('2016 Q2', 20, 15).add('2016 Q3', 5, 12).add('2016 Q4', 1, 20)),
                    Col(MorrisBar('Bar1', 'Bar2').grid(0, 100).add('2016 Q1', 10, 20).add('2016 Q2', 20, 15).add('2016 Q3', 5, 12).add('2016 Q4', 1, 20))
                    )
                ))),
            Row(Panel('MorrisDonut',
                MorrisDonut(height=150).add('Jaws', 15).add('Screw', 2).add('Candy', 29).add('Dwaeji', 10).add('Babam', 20)
                ))
            )
        return lo
