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
Created on 2016. 7. 27.

@author: "comfact"
'''

from ciscowebkit.common import *

class Setting(Feature):
    
    def __init__(self): Feature.__init__(self, icon='fa-wrench')
 
class Domain(SubFeature):
    
    def __init__(self):
        SubFeature.__init__(self, icon='fa-wrench')
        
        form = Form('Connect')
        form.addText('domain', 'Domain', 'input unique domain name')
        form.addText('ips', 'APIC Address', 'x.x.x.x/y.y.y.y/z.z.z.z')
        form.addText('user', 'User', 'input admin name')
        form.addPassword('pwd', 'Password', 'input admin password')
        self.form_panel = Panel('Add Connection', form, icon='fa-asterisk')
            
        self.info = None;
        
    def get(self, request, *cmd):
        
        if self.info:
            lo = Layout(Row(Col(self.info)))
            self.info = None
        else: lo = Layout()
        
        apic_table = Table('Domain', 'Address', 'User', 'Password', 'Connected')
        for domain in ACI._order: apic_table.add(domain, str(ACI[domain].ips), ACI[domain].user, '*******', ACI[domain].connected, did=domain)

        return lo(
            Row(self.form_panel),
            Row(Panel('Connection List', apic_table, icon='fa-table'))
        )
    
    def post(self, request, data, *cmd):
        
        if request.user.is_superuser:
            apic = ACI.addDomain(data.domain, data.ips, data.user, data.pwd)
            if apic: 
                self.info = InfoBlock(LC('Connection succeeded'),
                                      LC('The APIC %(domain)s is connected %(connected)s.', domain=apic.domain, connected=apic.connected)) 
            else: 
                self.info = InfoBlock(LC('Connection Failed'),
                                      LC('The APIC connection failed. Check the connection information.'))
        else:
            self.info = InfoBlock(LC('Access Denied'), LC('user "%(user)s" has not access authentication', user=str(request.user)))
        
        return self.get(request, *cmd)
    
    def delete(self, request, data, *cmd):
        
        if request.user.is_superuser:
            ACI.delDomain(data)

            self.info = InfoBlock(LC('Connection Deleted'),
                                  LC('The connection %(data)s has been removed.', data=data))
        
        else:
            self.info = InfoBlock(LC('Access Denied'), LC('user "%(user)s" has not access authentication', user=str(request.user)))
        
        return self.get(request, *cmd)

class User_Access(SubFeature):
     
    def __init__(self):
        SubFeature.__init__(self, icon='fa-wrench')
         
        form = Form('Register')
        form.addText('user', 'User', 'input user id')
        form.addText('domain', 'Domain', 'input domain name allowed')
        self.form_panel = Panel('Add User Access', form, icon='fa-asterisk')
         
        self.info = None;
        
    def get(self, request, *cmd):
        
        if self.info:
            lo = Layout(Row(Col(self.info)))
            self.info = None
        else: lo = Layout()
        
        ud_table = Table('User', 'Domain')
        ud_list = ACI.getAccess()
        for ud in ud_list: ud_table.add(ud.user, ud.domain, did=ud.id)

        return lo(
            Row(self.form_panel),
            Row(Panel('User Access List', ud_table, icon='fa-table'))
        )
    
    def post(self, request, data, *cmd):
        
        if request.user.is_superuser:
            
            if ACI.addAccess(data.user, data.domain):
                self.info = InfoBlock(LC('Register succeeded'), LC(''))
            else:
                self.info = InfoBlock(LC('Register Failed'), LC('User Access already Exist.'))
        
        else:
            self.info = InfoBlock(LC('Access Denied'), LC('user "%(user)s" has not access authentication', user=str(request.user)))
        
        return self.get(request, *cmd)
    
    def delete(self, request, data, *cmd):
        
        if request.user.is_superuser:
            
            if ACI.delAccess(data):
                self.info = InfoBlock(LC('Removing succeeded'), LC(''))
            else:
                self.info = InfoBlock(LC('Removing Failed'), LC('User Access already Deleted.'))
        
        else:
            self.info = InfoBlock(LC('Access Denied'), LC('user "%(user)s" has not access authentication', user=str(request.user)))
        
        return self.get(request, *cmd) 