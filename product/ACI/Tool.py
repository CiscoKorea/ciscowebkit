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
Created on 2016. 8. 12.

@author: "comfact"
'''

from ciscowebkit.common import *
from django.utils import translation
from django.utils.translation import ugettext_lazy as _

class Tool(Feature):
    
    def __init__(self): Feature.__init__(self, 0, 'fa-cutlery')

class Console(SubFeature):
    
    '''APIC Terminal Interface'''
    
    def __init__(self):
        SubFeature.__init__(self, icon='fa-terminal')
        self.greeting = '''
###############################################################################
#           _    ____ ___ _____           _ _    _ _    ____ _     ___        #
#          / \  / ___|_ _|_   _|__   ___ | | | _(_) |_ / ___| |   |_ _|       #
#         / _ \| |    | |  | |/ _ \ / _ \| | |/ / | __| |   | |    | |        #
#        / ___ \ |___ | |  | | (_) | (_) | |   <| | |_| |___| |___ | |        #
#       /_/   \_\____|___| |_|\___/ \___/|_|_|\_\_|\__|\____|_____|___|       #
#                                                                             #
###############################################################################
#                                                                             #
# Copyright (c) 2015 Cisco Systems                                            #
# All Rights Reserved.                                                        #
#                                                                             #
#    Licensed under the Apache License, Version 2.0 (the "License"); you may  #
#    not use this file except in compliance with the License. You may obtain  #
#    a copy of the License at                                                 #
#                                                                             #
#         http://www.apache.org/licenses/LICENSE-2.0                          #
#                                                                             #
#    Unless required by applicable law or agreed to in writing, software      #
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT#
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the #
#    License for the specific language governing permissions and limitations  #
#    under the License.                                                       #
#                                                                             #
###############################################################################
'''
        self.terminal = Terminal(self.greeting, '')
    
    def get(self, request, *cmd):
        msg1 = _('No Data')
        msg2 = _('There is no associated APIC. Add APIC connection in Setting menu.')
        
        MSG1 = msg1.encode("utf-8") 
        MSG2 = msg2.encode("utf-8")

        if len(ACI._order) == 0: return InfoBlock(MSG1,MSG2)
        lo = Layout(
            Row(self.terminal)
        )
        
        return lo
        
    def post(self, request, data, *cmd):
        msg1 = _('No Data')
        msg2 = _('There is no associated APIC. Add APIC connection in Setting menu.')
        
        MSG1 = msg1.encode("utf-8") 
        MSG2 = msg2.encode("utf-8")

        if len(ACI._order) == 0: return InfoBlock(MSG1,MSG2)
        if data.cmd == '':
            self.terminal.addScreen('''%s$ 
''' % self.terminal.location)
        elif data.cmd == 'exit':
            del self.terminal
            self.terminal = Terminal(self.greeting, '')
        elif data.cmd == 'clear':
            self.terminal.setScreen(self.greeting)
        else:
            self.terminal.addScreen('''%s$ %s

This is just testing console
Not Implemented Yet!
Have a Nice Day!

''' % (self.terminal.location, data.cmd))
        
        lo = Layout(
            Row(self.terminal)
        )
        
        return lo
        
        
        