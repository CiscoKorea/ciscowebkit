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
Created on 2016. 8. 17.

@author: "comfact"
'''

import re

from ciscowebkit.common.pygics import *
from ciscowebkit.common.manager.aci import acitoolkit as acitool
from ciscowebkit.models import *

class EPTracker(Task):
    
    class APIC_CONNECTION_FAILED(E):
        def __init__(self, apic): E.__init__(self, 'Connection Failed %s@%s:%s' % (apic.user, str(apic.ips), apic.pwd))
         
    def __init__(self, apic):
        Task.__init__(self, 2, 2)
        self.apic = apic
        self.domain = apic.domain
        self.session = acitool.Session('https://%s' % apic.connected, apic.user, apic.pwd)
        resp = self.session.login()
        if not resp.ok:
            self.session.close()
            raise EPTracker.APIC.APIC_CONNECTION_FAILED(apic)
        
        endpoints = acitool.Endpoint.get(self.session)
        for ep in endpoints:
            
            try: epg = ep.get_parent()
            except AttributeError: continue
            app_profile = epg.get_parent()
            tenant = app_profile.get_parent()
            if ep.if_dn:
                for dn in ep.if_dn:
                    rns = dn.split('/')
                    intf_name = rns[1][4:] + '/' + (rns[2][10:] if 'protpaths' in rns[2] else rns[2][6:]) + '/' + dn.split('[')[1][:-1]
            else:
                dvs = ep.if_name.split(' ')
                rns = dvs[1].split('/')
                intf_name = rns[0] + '/' + rns[1] + '/' + dvs[0] + '/' + rns[2] + '/' + rns[3]
            
            try: ACI_EPTracker.objects.get(mac=ep.mac, domain=self.domain, stop='0000-00-00 00:00:00')
            except ACI_EPTracker.DoesNotExist:
                ACI_EPTracker.objects.create(mac=ep.mac,
                                             ip=ep.ip,
                                             domain=self.domain,
                                             tenant=tenant.name,
                                             app=app_profile.name,
                                             epg=epg.name,
                                             intf=intf_name,
                                             start=self.convert_timestamp_to_mysql(ep.timestamp),
                                             stop='0000-00-00 00:00:00')

        acitool.Endpoint.subscribe(self.session)
        self.start()
    
    def __del__(self):
        self.stop()
        self.session.close()
        
    def __call__(self):
        ret = L()
        try: epts = ACI_EPTracker.objects.filter(domain=self.domain)
        except ACI_EPTracker.DoesNotExist: pass
        else:
            for ept in epts:
                ret << M(mac=ept.mac,
                         ip=ept.ip,
                         domain=ept.domain,
                         app=ept.app,
                         epg=ept.epg,
                         intf=ept.intf,
                         start=ept.start,
                         stop=ept.stop)
        return ret
        
    def task(self):
        while True:
            try:
                if acitool.Endpoint.has_events(self._session):
                    ep = acitool.Endpoint.get_event(self._session)
                    try: epg = ep.get_parent()
                    except AttributeError: continue
                    app_profile = epg.get_parent()
                    tenant = app_profile.get_parent()
                    if ep.is_deleted():
                        ep.if_name = None
                        try:
                            ept = ACI_EPTracker.objects.get(mac=ep.mac, domain=self.domain, tenant=tenant.name, stop='0000-00-00 00:00:00')
                            ept.update(stop=self.convert_timestamp_to_mysql(ep.timestamp))
                        except: pass
                    else:
                        if ep.if_dn:
                            for dn in ep.if_dn:
                                rns = dn.split('/')
                                intf_name = rns[1][4:] + '/' + (rns[2][10:] if 'protpaths' in rns[2] else rns[2][6:]) + '/' + dn.split('[')[1][:-1]
                        else:
                            dvs = ep.if_name.split(' ')
                            rns = dvs[1].split('/')
                            intf_name = rns[0] + '/' + rns[1] + '/' + dvs[0] + '/' + rns[2] + '/' + rns[3]
                        
                        try: ACI_EPTracker.objects.get(mac=ep.mac, domain=self.domain, stop='0000-00-00 00:00:00')
                        except ACI_EPTracker.DoesNotExist:
                            ACI_EPTracker.objects.create(mac=ep.mac,
                                                         ip=ep.ip,
                                                         domain=self.domain,
                                                         tenant=tenant.name,
                                                         app=app_profile.name,
                                                         epg=epg.name,
                                                         intf=intf_name,
                                                         start=self.convert_timestamp_to_mysql(ep.timestamp),
                                                         stop='0000-00-00 00:00:00')
                else: break
            except: break
    
    def convert_timestamp_to_mysql(self, timestamp):
        (resp_ts, remaining) = timestamp.split('T')
        resp_ts += ' '
        resp_ts = resp_ts + remaining.split('+')[0].split('.')[0]
        return resp_ts
