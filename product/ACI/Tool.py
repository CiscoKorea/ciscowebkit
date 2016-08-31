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
# Copyright (c) 2015 Cisco Systems                                             #
# All Rights Reserved.                                                         #
#                                                                              #
#    Licensed under the Apache License, Version 2.0 (the "License"); you may   #
#    not use this file except in compliance with the License. You may obtain   #
#    a copy of the License at                                                  #
#                                                                              #
#         http://www.apache.org/licenses/LICENSE-2.0                           #
#                                                                              #
#    Unless required by applicable law or agreed to in writing, software       #
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT #
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the  #
#    License for the specific language governing permissions and limitations   #
#    under the License.                                                        #
#                                                                              #
################################################################################
'''
        self.terminal = Terminal(self.greeting, '')
    
    def get(self, request, *cmd):
        #user_language = 'en'
        #translation.activate(user_language)
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
        #user_language = 'en'
        #translation.activate(user_language)
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
        
class Object_Finder(SubFeature):
    
    '''APIC Object Finder'''
    
    def __init__(self):
        SubFeature.__init__(self, icon='fa-search')
        
        form = Form('Search')
        form.addText('object', 'Object')
        form.addText('query', 'Query')
        self.form_panel = Panel('Finder', form, icon='fa-search')
        
    def get(self, request, *cmd):
        return Layout(Row(self.form_panel))
    
    def post(self, request, data, *cmd):
        lo = Layout(Row(self.form_panel))
        
        objs = ACI.get((data.object, data.query))
        try: keys = objs[ACI._order[0]][0].keys()
        except: keys = []
        
        for domain in ACI._order:
            if objs[domain] == None: continue
            table = Table(*keys)
            for obj in objs[domain]:
                vals = L()
                for key in keys:
                    val = obj[key]
                    if val == '' or val == None: vals << ' '
                    else: vals << val
                table.add(*vals)
            lo(Row(Panel(domain, table, icon='fa-table')))
        
        return lo
    