#!/usr/bin/env python
# -*- coding: utf-8 -*-
################################################################################
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
Created on 2016. 8. 2.

@author: "comfact"
'''

from ciscowebkit.common.pygics import L, M
from ciscowebkit.common.abstract import __View__

class JustGage(__View__):
    
    def __init__(self, value, min=0, max=100, **option):
        __View__.__init__(self, 'justgage', value=value, min=min, max=max, opts=M())
        if 'desc' in option: self.opts['title'] = option['desc']
        self._link = self.__create_link__(option['link']) if 'link' in option else ''
        self._title = '<h3 class="cw-css-elem-title">%s</h3>' % option['title'] if 'title' in option else ''
        self._height = ' style="height:%dpx;"' % option['height'] if 'height' in option else ''
        
    def __render__(self):
        return '<div>%s<div id="cw-view-%s"%s%s></div></div>' % (self._title, self._id, self._link, self._height)
