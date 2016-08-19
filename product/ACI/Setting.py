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
Created on 2016. 7. 27.

@author: "comfact"
'''

from ciscowebkit.common import *
from django.utils import translation
from django.utils.translation import ugettext_lazy as _

 
class Setting(Feature):
    
    def __init__(self):
        Feature.__init__(self, icon='fa-wrench')
        
        form = Form('Connect')
        form.addText('domain', 'Domain', 'input unique domain name')
        form.addText('ips', 'APIC Address', 'x.x.x.x/y.y.y.y/z.z.z.z')
        form.addText('user', 'User', 'input admin name')
        form.addText('pwd', 'Password', 'input admin password')
        self.form_panel = Panel('Add Connection', form, icon='fa-asterisk')
        
        self.info = None;
        
    def get(self, request, *cmd):
        apic_table = Table('Domain', 'Address', 'User', 'Password', 'Connected')
        for domain in ACI._order: apic_table.add(domain, str(ACI[domain].ips), ACI[domain].user, '*******', ACI[domain].connected, did=domain)
        
        if self.info:
            lo = Layout(Row(Col(self.info)))
            self.info = None
        else: lo = Layout()
        
        lo(
            Row(self.form_panel),
            Row(Panel('Connection List', apic_table, icon='fa-table'))
        )
        
        return lo
    
    def post(self, request, data, *cmd):
        apic = ACI.addDomain(data.domain, data.ips, data.user, data.pwd)
        
        
        #user_language = 'en'
        #translation.activate(user_language)
        msg1 = _('Connection Failed')
        msg2 = _('The APIC connection failed. Check the connection information.')
        msg3 = _('Connection succeeded')
        msg4 = _('The APIC %(domain)s is connected %(connected)s.') % {'domain': apic.domain, 'connected': apic.connected}
        
        MSG1 = msg1.encode("utf-8") 
        MSG2 = msg2.encode("utf-8")
        MSG3 = msg3.encode("utf-8") 
        MSG4 = msg4.encode("utf-8")
        
        if apic: self.info = InfoBlock(MSG3, MSG4) 
        else: self.info = InfoBlock(MSG1, MSG2)
        return self.get(request, *cmd)
    
    def delete(self, request, data, *cmd):
        ACI.delDomain(data)
        msg5 = _('Connection Deleted')
        msg6 = _('The connection %(data)s has been removed.') % {'data': data}

        MSG5 = msg5.encode("utf-8")
        
        self.info = InfoBlock(msg5, MSG6)
        return self.get(request, *cmd)