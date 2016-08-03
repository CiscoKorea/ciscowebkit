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
        lo = Layout(
            Row(
                Col(Panel('Chartist Pie', Layout(
                    Row(ChartistDonut(title='Pie Pure', height=150).add('Jaws', 15).add('Screw', 2).add('Candy', 29).add('Dwaeji', 10).add('Babam', 20)),
                    Row(ChartistDonut(title='Pie Ani', height=150).add('Jaws', 15).add('Screw', 2).add('Candy', 29).add('Dwaeji', 10).add('Babam', 20).ani()),
                    )), (Col.SMALL, 6)),
                Col(Panel('Chartist Donut', Layout(
                    Row(ChartistDonut(title='Donut Pure', height=150).add('Jaws', 15).add('Screw', 2).add('Candy', 29).add('Dwaeji', 10).add('Babam', 20)),
                    Row(ChartistDonut(title='Donut Stroke Ani', height=150).add('Jaws', 15).add('Screw', 2).add('Candy', 29).add('Dwaeji', 10).add('Babam', 20).stroke(40).ani()),    
                    )), (Col.SMALL, 6))
                ),
            Row(
                Panel('Chartist Line', Layout(
                Row(ChartistLine('Line1', 'Line2', 'Line3', title='Sample Line').grid(0, 100).ani().add('1', 10, 20, 15).add('2', 11, 19, 2).add('3', 12, 18, 29).add('4', 13, 17, 10).add('5', 14, 16, 20)),
                Row(ChartistArea('Line1', 'Line2', 'Line3', title='Sample Area').ani().add('1', 10, 20, 15).add('2', 11, 19, 2).add('3', 12, 18, 29).add('4', 13, 17, 10).add('5', 14, 16, 20))
                ))),
            Row(
                Panel('Chartist VBar', Layout(
                Row(ChartistBar('Line1', 'Line2', 'Line3', title='VBar Pure').add('1', 10, 20, 15).add('2', 11, 19, 2).add('3', 12, 18, 29).add('4', 13, 17, 10).add('5', 14, 16, 20)),
                Row(ChartistBar('Line1', 'Line2', 'Line3', title='VBar Grid & Stroke').grid(0, 100).stroke(40, 20).ani().add('1', 10, 20, 15).add('2', 11, 19, 2).add('3', 12, 18, 29).add('4', 13, 17, 10).add('5', 14, 16, 20)),
                Row(ChartistBar('Line1', 'Line2', 'Line3', title='VBar Stack').stack().add('1', 10, 20, 15).add('2', 11, 19, 2).add('3', 12, 18, 29).add('4', 13, 17, 10).add('5', 14, 16, 20)),
                Row(ChartistBar(title='VBar Linear').ani().add('Jaws', 15).add('Screw', 2).add('Candy', 29).add('Dwaeji', 10).add('Babam', 20))
                ))),
            Row(
                Panel('Chartist HBar', Layout(
                Row(ChartistSlide('Line1', 'Line2', 'Line3',title='HBar Pure').add('1', 10, 20, 15).add('2', 11, 19, 2).add('3', 12, 18, 29).add('4', 13, 17, 10).add('5', 14, 16, 20)),
                Row(ChartistSlide('Line1', 'Line2', 'Line3', title='HBar Grid & Stroke').grid(0, 100).stroke(10, 10).ani().add('1', 10, 20, 15).add('2', 11, 19, 2).add('3', 12, 18, 29).add('4', 13, 17, 10).add('5', 14, 16, 20)),
                Row(ChartistSlide('Line1', 'Line2', 'Line3', title='HBar Stack').stack().add('1', 10, 20, 15).add('2', 11, 19, 2).add('3', 12, 18, 29).add('4', 13, 17, 10).add('5', 14, 16, 20)),
                Row(ChartistSlide(title='HBar Linear').ani().add('Jaws', 15).add('Screw', 2).add('Candy', 29).add('Dwaeji', 10).add('Babam', 20))
                )))
            )
        
        return lo
        
        
        