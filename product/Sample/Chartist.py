#!/usr/bin/env python
# -*- coding: utf-8 -*-
################################################################################
#        _____ _                  _____           _                            #
#       / ____(_)                / ____|         | |                           #
#      | |     _ ___  ___ ___   | (___  _   _ ___| |_ ___ _ __ ___  ___        #
#      | |    | / __|/ __/ _ \   \___ \| | | / __| __/ _ \ '_ ` _ \/ __|       #
#      | |____| \__ \ (_| (_) |  ____) | |_| \__ \ ||  __/ | | | | \__ \       #
#       \_____|_|___/\___\___/  |_____/ \__, |___/\__\___|_| |_| |_|___/       #
#                                        __/ |                                 #
#                                       |___/                                  #
#           _  __                       _____       _  _____ ______            #
#          | |/ /                      / ____|     | |/ ____|  ____|           #
#          | ' / ___  _ __ ___  __ _  | (___   ___ | | (___ | |__              #
#          |  < / _ \| '__/ _ \/ _` |  \___ \ / _ \| |\___ \|  __|             #
#          | . \ (_) | | |  __/ (_| |  ____) | (_) | |____) | |____            #
#          |_|\_\___/|_|  \___|\__,_| |_____/ \___/|_|_____/|______|           #
#                                                                              #
################################################################################
#                                                                              #
# Copyright (c) 2016 Cisco Systems                                             #
# All Rights Reserved.                                                         #
#                                                                              #
# Licensed under the Apache License, Version 2.0 (the "License"); you may      #
# not use this file except in compliance with the License. You may obtain      #
# a copy of the License at                                                     #
#                                                                              #
# http://www.apache.org/licenses/LICENSE-2.0                                   #
#                                                                              #
# Unless required by applicable law or agreed to in writing, software          #
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT #
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the  #
#    License for the specific language governing permissions and limitations   #
#    under the License.                                                        #
#                                                                              #
################################################################################

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
        
        
        