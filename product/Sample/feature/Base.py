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

#-*- coding: utf-8 -*-
'''
Created on 2016. 7. 11.

@author: "comfact"
'''

from ciscowebkit.common import *

class Base(Feature):
    
    '''Base Elements'''
    
    def __init__(self, **kargs):
        Feature.__init__(self, 3, 'fa-archive', **kargs)
        self.inum = 0
        self.itable = Table('ID', 'Name', 'Data')
        self.ipanel = Panel("Input Data", self.itable)
        
    def get(self, requset, *cmd):
        lo = Layout(
            Row(
                Col(Panel("T1", Text("This is Text 1", link=(None, 't1'))), (Col.SMALL, 6), (Col.LARGE, 6)),
                Col(Panel("T2", Text("This is Text 2", link=(None, 't2'))), (Col.SMALL, 6), (Col.LARGE, 6))
                ),
            Row(Plain(HList().add('t1', 't1', 'fa-bus', 't1').add('t2', 't2', 'fa-plane', 't2'))),
            Row(
                Col(InfoBlock('Test Info 1', 'This is Test Msg 1')),
                Col(InfoBlock('Test Info 2', 'This is Test Msg 2'))
                ),
            Row(
                Col(InfoPanel('Info Panel', 100, 'link to self', link=(self, None)), (Col.SMALL, 6)),
                Col(InfoDoc('''This is information document.
This page is chart samples

Let's start sample view models !!!'''), (Col.SMALL, 6))
                ),
            Row(
                Col(VList().add('t1', 't1', 'fa-bus', 't1').add('t2', 't2', 'fa-plane', 't2'), (Col.SMALL, 6)),
                Col(HList().add('t1', 't1', 'fa-bus', 't1').add('t2', 't2', 'fa-plane', 't2'), (Col.SMALL, 6))
                ),
            Row(Panel('Tables', Layout(
                Row(Table('Col1', 'Col2', 'Col3', title='Table 1').add('1', '2', '3', link=(None, 't1')).add('a', 'b', 'c', link=(None, 't2')).add('A', 'B', 'C', link=(None, 't1')).add('가', '나', '다', link=(None, 't2'))),
                Row(Table('Col1', 'Col2', 'Col3', title='Table 2').add('1', '2', '3', did='t1').add('a', 'b', 'c', did='t2').add('A', 'B', 'C', did='t3').add('가', '나', '다', did='t4'))
                ))),
            Row(Panel('Form', Form('Submit').addText('test1', 'TextInput1').addText('test2', 'TextInput2'))),
            Row(self.ipanel)
            )
        return lo
    
    def post(self, request, data, *cmd):
        print 'Call Post', data
        self.itable.add(str(self.inum), data.test1, data.test2)
        self.inum += 1
        return self.get(request, *cmd)

    def delete(self, request, data, *cmd):
        print 'Call Delete', data
        return self.get(request, *cmd)
