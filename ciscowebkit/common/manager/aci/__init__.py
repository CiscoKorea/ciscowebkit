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
Created on 2016. 7. 20.

@author: "comfact"
'''

import re
import json
import time
import copy
import requests

from ciscowebkit.models import *

from ciscowebkit.common.pygics import *
from ciscowebkit.common.manager.aci import acitoolkit as acitool
from ciscowebkit.common.manager.aci.eptracker import EPTracker
from ciscowebkit.common.manager.aci.healthmon import HealthMon

class ACIManager(M):
     
    class APIC(M):
        
        class APIC_CONNECTION_FAILED(E):
            def __init__(self, apic): E.__init__(self, 'Connection Failed %s@%s:%s' % (apic.user, str(apic.ips), apic.pwd))
             
        class ACITOOLKIT_CLASS_WRAPPER(object):
            
            class ACITOOLKIT_METHOD_WRAPPER:
                def __init__(self, apic, cls, key): self.apic = apic; self.cls = cls; self.key = key
                def __call__(self, *argv):
                    return getattr(self.cls, self.key)(self.apic._mo_session, *argv)
            
            def __init__(self, apic, cls):
                for key in cls.__dict__:
                    if re.search('^[_A-Za-z][A-Za-z]\w*', key):
                        if typeof(cls.__dict__[key]) == 'classmethod':
                            self.__setattr__(key, ACIManager.APIC.ACITOOLKIT_CLASS_WRAPPER.ACITOOLKIT_METHOD_WRAPPER(apic, cls, key))
            
        def __init__(self, mng, domain, ips, user, pwd):
            M.__init__(self, domain=domain, user=user, pwd=pwd)
            self._mng = mng
            sepkv = re.match('^[\d.:]+(?P<sep>[,/&|])', ips)
            if sepkv: self['ips'] = L(*ips.split(sepkv.group('sep')))
            else: self['ips'] = L(ips)
             
            #===================================================================
            # Connect APIC
            #===================================================================
            
            for ip in self.ips:
                self._session = acitool.Session('https://%s' % ip, user, pwd)
                resp = self._session.login()
                if resp.ok:
                    self._mo_session = acitool.Session('https://%s' % ip, user, pwd)
                    resp = self._mo_session.login()
                    if resp.ok:
                        self['connected'] = ip
                        self._url = 'https://%s/api/' % ip
                        self.eptracker = EPTracker(self)
                        self.healthmon = HealthMon(self)
                        break
                    else:
                        self._mo_session.close()
                        self._session.close()
                else:
                    self._session.close()
            else: raise ACIManager.APIC.APIC_CONNECTION_FAILED(self)
            
            for key in acitool.__dict__:
                if re.search('^[A-Z]+\w*', key):
                    self.__setattr__(key, ACIManager.APIC.ACITOOLKIT_CLASS_WRAPPER(self, acitool.__dict__[key]))
                    
        def __del__(self):
            self.healthmon.__del__()
            self.eptracker.__del__()
            self._mo_session.close()
            self._session.close()
            
        def get(self, *targets):
            if self.connected:
                ret = L()
                for target in targets:
                    if not instof(target, tuple): target = (target, '')
                    else: target = (target[0], '?' + target[1])
                    resp = self._session.get('/api/class/%s.json%s' % target)
                    if resp.status_code == 200:
                        imdata = Struct.JSON2DATA(resp.text).imdata
                        wellform = L()
                        for im in imdata:
                            for key in im:
                                attr = im[key].attributes
                                attr['_model'] = key
                                wellform << attr
                        ret << wellform
                    else: ret << None
                if len(targets) == 1: return ret[0]
                else: return ret
            return None
        
        def getCount(self, *targets):
            if self.connected:
                ret = L()
                for target in targets:
                    if not instof(target, tuple): target = (target, '')
                    else: target = (target[0], '&' + target[1])
                    resp = self._session.get('/api/class/%s.json?rsp-subtree-include=count%s' % target)
                    if resp.status_code == 200:
                        ret << int(json.loads(resp.text)['imdata'][0]['moCount']['attributes']['count'])
                    else: ret << None
                if len(targets) == 1: return ret[0]
                else: return ret
            return None
        
        def getHealthHist(self):
            if self.connected:
                return M(_tstamp=self._mng.healthmon.health._tstamp,
                         topology=self._mng.healthmon.health[self.domain].topology,
                         tenant=self._mng.healthmon.health[self.domain].tenant)
            return None
        
        def getHealthNow(self):
            if self.connected:
                ret = M(topology=M(), tenant=M())
                health_hist = self._mng.healthmon.health[self.domain]
                for dn in health_hist.topology: ret.topology[dn] = health_hist.topology[dn][-1]
                for dn in health_hist.tenant: ret.tenant[dn] = health_hist.tenant[dn][-1]
                return ret
            return None
        
        def getFault(self):
            if self.connected:
                ret = M(critical=L(), major=L(), minor=L(), warning=L())
                resp = self._session.get('/api/class/faultInfo.json?query-target-filter=eq(faultInfo.severity,"critical")')
                if resp.status_code == 200:
                    imdata = Struct.JSON2DATA(resp.text).imdata
                    for im in imdata:
                        for key in im:
                            attr = im[key].attributes
                            attr['_model'] = key
                            ret.critical << attr
                resp = self._session.get('/api/class/faultInfo.json?query-target-filter=eq(faultInfo.severity,"major")')
                if resp.status_code == 200:
                    imdata = Struct.JSON2DATA(resp.text).imdata
                    for im in imdata:
                        for key in im:
                            attr = im[key].attributes
                            attr['_model'] = key
                            ret.major << attr
                resp = self._session.get('/api/class/faultInfo.json?query-target-filter=eq(faultInfo.severity,"minor")')
                if resp.status_code == 200:
                    imdata = Struct.JSON2DATA(resp.text).imdata
                    for im in imdata:
                        for key in im:
                            attr = im[key].attributes
                            attr['_model'] = key
                            ret.minor << attr
                resp = self._session.get('/api/class/faultInfo.json?query-target-filter=eq(faultInfo.severity,"warning")')
                if resp.status_code == 200:
                    imdata = Struct.JSON2DATA(resp.text).imdata
                    for im in imdata:
                        for key in im:
                            attr = im[key].attributes
                            attr['_model'] = key
                            ret.warning << attr
                return ret
            return None
        
        def getFaultCount(self):
            if self.connected:
                ret = M()
                resp = self._session.get('/api/class/faultInfo.json?query-target-filter=eq(faultInfo.severity,"critical")&rsp-subtree-include=count')
                if resp.status_code == 200: ret['critical'] = int(json.loads(resp.text)['imdata'][0]['moCount']['attributes']['count'])
                else: ret['critical'] = None
                resp = self._session.get('/api/class/faultInfo.json?query-target-filter=eq(faultInfo.severity,"major")&rsp-subtree-include=count')
                if resp.status_code == 200: ret['major'] = int(json.loads(resp.text)['imdata'][0]['moCount']['attributes']['count'])
                else: ret['major'] = None
                resp = self._session.get('/api/class/faultInfo.json?query-target-filter=eq(faultInfo.severity,"minor")&rsp-subtree-include=count')
                if resp.status_code == 200: ret['minor'] = int(json.loads(resp.text)['imdata'][0]['moCount']['attributes']['count'])
                else: ret['minor'] = None
                resp = self._session.get('/api/class/faultInfo.json?query-target-filter=eq(faultInfo.severity,"warning")&rsp-subtree-include=count')
                if resp.status_code == 200: ret['warning'] = int(json.loads(resp.text)['imdata'][0]['moCount']['attributes']['count'])
                else: ret['warning'] = None
                return ret
            return None
        
        def getEPTrack(self):
            if self.connected:
                return self.eptracker()
            return None
        
    class HealthTracker(Task):
        
        def __init__(self, mng, mon_sec, mon_cnt):
            Task.__init__(self, mon_sec, mon_sec)
            self.mng = mng
            self.mon_sec = mon_sec
            self.mon_cnt = mon_cnt
            init_time = time.time()
            _tstamp = L()
            self.template = L()
            for i in reversed(range(0, mon_cnt)):
                _tstamp << time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(init_time - (mon_sec * (i + 1))))
                self.template << None
            self.health = M(_tstamp=_tstamp)
            self.updateHealth()
            self.start()
            
        def __del__(self):
            self.stop()
            
        def updateHealth(self):
            try:
                health_now = copy.deepcopy(self.health)
                health_now._tstamp << time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(time.time()))
                health_now._tstamp.pop(0)
                health_data = M()
                for domain in self.mng._order: health_data[domain] = self.mng[domain].healthmon()
                for domain in self.mng._order:
                    if domain not in health_now: health_now[domain] = M(topology=M(), tenant=M())
                    for dn in health_data[domain].topology:
                        if dn not in health_now[domain].topology: health_now[domain].topology[dn] = copy.deepcopy(self.template)
                        health_now[domain].topology[dn] << health_data[domain].topology[dn]
                        health_now[domain].topology[dn].pop(0)
                    del_list = L()
                    for dn in health_now[domain].topology:
                        if dn not in health_data[domain].topology: del_list << dn
                    for dn in del_list: health_now[domain].topology >> dn
                    for dn in health_data[domain].tenant:
                        if dn not in health_now[domain].tenant: health_now[domain].tenant[dn] = copy.deepcopy(self.template)
                        health_now[domain].tenant[dn] << health_data[domain].tenant[dn]
                        health_now[domain].tenant[dn].pop(0)
                    del_list = L()
                    for dn in health_now[domain].tenant:
                        if dn not in health_data[domain].tenant: del_list << dn
                    for dn in del_list: health_now[domain].tenant >> dn
                self.health = health_now
            except Exception as e:
                print str(e)
            
        def task(self):
            self.updateHealth()

    def __init__(self, mon_sec=60, mon_cnt=10):
        M.__init__(self, _order=L())
        self.mon_sec = mon_sec
        self.mon_cnt = mon_cnt
        self.healthmon = None
        
        for dom in ACI_Domain.objects.all():
            self.addDomain(dom.name, dom.controllers, dom.user, dom.password)
        
    def addDomain(self, domain, ips, user, pwd):
        if domain in self._order: return None
        try:
            apic = ACIManager.APIC(self, domain, ips, user, pwd)
            self[domain] = apic
            self._order << domain
            if self.healthmon == None: self.healthmon = ACIManager.HealthTracker(self, self.mon_sec, self.mon_cnt)
            ACI_Domain.objects.create(name=domain, controllers=ips, user=user, password=pwd)
            return apic
        except Exception as e:
            print str(e)
            return None
    
    def delDomain(self, domain):
        if domain not in self._order: return False
        self._order >> domain
        self[domain].__del__()
        self >> domain
        if len(self._order) == 0:
            self.healthmon.__del__()
            self.healthmon = None
        try: ACI_Domain.objects.get(name=domain).delete()
        except: pass
        return True
    
    def addAccess(self, user, domain):
        for ud in ACI_UserDomain.objects.filter(user=user, domain=domain):
            return False
        ACI_UserDomain.objects.create(user=user, domain=domain)
        return True
    
    def delAccess(self, id):
        
        try: ud_obj = ACI_UserDomain.objects.get(id=data)
        except ACI_UserDomain.DoesNotExist:
            self.info = InfoBlock(LC('Removing Failed'), LC('User Access already Deleted.'))
        else:
            ud_obj.delete()
    
    def get(self, *targets):
        ret = L()
        for target in targets:
            tres = M()
            for domain in self._order: tres[domain] = self[domain].get(target)
            ret << tres
        if len(targets) == 1: return ret[0]
        else: return ret
    
    def getCount(self, *targets):
        ret = L()
        for target in targets:
            tres = M()
            for domain in self._order: tres[domain] = self[domain].getCount(target)
            ret << tres
        if len(targets) == 1: return ret[0]
        else: return ret
    
    def getHealthHist(self):
        if self.healthmon != None: return self.healthmon.health
        return None
    
    def getHealthNow(self):
        if self.healthmon != None:
            ret = M()
            health_hist = self.healthmon.health
            for domain in self._order:
                ret[domain] = M(topology=M(), tenant=M())
                for dn in health_hist[domain].topology: ret[domain].topology[dn] = health_hist[domain].topology[dn][-1]
                for dn in health_hist[domain].tenant: ret[domain].tenant[dn] = health_hist[domain].tenant[dn][-1]
            return ret
        return None
    
    def getFault(self):
        ret = M()
        for domain in self._order: ret[domain] = self[domain].getFault()
        return ret
    
    def getFaultCount(self):
        ret = M()
        for domain in self._order: ret[domain] = self[domain].getFaultCount()
        return ret
    
    def getEPTrack(self):
        ret = M()
        for domain in self._order: ret[domain] = self[domain].getEPTrack()
        return ret

if __name__ == '__main__':
    
    am = ACIManager(60, 5)
    
    am.addDomain('Test1', '10.72.86.21/10.72.86.22', 'admin', '1234Qwer')
    
#     print inf(am.Test1.getHealthHist())
#     print inf(am.getHealthHist())
#     print inf(am.Test1.getHealthNow())
#     print inf(am.getHealthNow())
    
#     print inf(am.Test1.getFault())
#     print inf(am.getFault())
#     print inf(am.Test1.getFaultCount())
#     print inf(am.getFaultCount())
    
#     print am.Test1.getCount('fvTenant', 'fvCEp')
#     print am.getCount('fvTenant', 'fvCEp')

#     print inf(am.Test1.getEPTrack())
#     print inf(am.getEPTrack())

#     print inf(am.Test1.getCount(('fabricNode', 'query-target-filter=ne(fabricNode.role,"controller")')))
        
#     print inf(am.Test1.get('l2IngrBytes5min'))
#     print inf(am.Test1.get(('l2IngrBytesAg15min', 'query-target-filter=wcard(l2IngrBytesAg15min.dn,"uni/tn-.*/ap-.*/epg-.*")'))[0])

#     print inf(am.Test1.get('l1PhysIf'))
    
    
#     objs = am.Test1.get('faultInfo')
#     for obj in objs:
#         if 'po3' in obj.dn:
#             print obj.dn
    print inf(am.Test1.get('fvABDPol'))
#     print inf(am.Test1.get(('eqptIngrTotalHist5min', 'query-target-filter=wcard(eqptIngrTotalHist5min.dn,"sys/phys-.*/HDeqptIngrTotal5min-0")')))
#     objs = am.Test1.get(('eqptEgrTotalHist5min', 'query-target-filter=wcard(eqptEgrTotalHist5min.dn,"sys/phys-.*/HDeqptEgrTotal5min-0")'))
#     print inf(objs)
#     print len(objs)
    
    am.delDomain('Test1')
    
     
    
    
     
    
    
    
        
        
    
    
    
    
    
    
    
    
        



