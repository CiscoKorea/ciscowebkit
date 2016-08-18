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
