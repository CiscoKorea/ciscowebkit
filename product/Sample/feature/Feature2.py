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
Created on 2016. 7. 5.

@author: "comfact"
'''

from ciscowebkit.common import *

class Feature2(Feature):

    def __init__(self): Feature.__init__(self, 0, 'fa-car')

class Object_1(SubFeature):
    
    '''Sub Feature Object 1'''
    
    def __init__(self): SubFeature.__init__(self, 0, 'fa-truck')
        
    def get(self, request):
        return Text('Sub Feature Object 1 Action')
    
class Object_2(SubFeature):
    
    '''Sub Feature Object 2'''
    
    def __init__(self): SubFeature.__init__(self, 0, 'fa-bus')
    
    def get(self, request):
        return Text('Sub Feature Object 2 Action')
