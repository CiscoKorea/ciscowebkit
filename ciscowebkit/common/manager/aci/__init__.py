'''
Created on 2016. 7. 20.

@author: "comfact"
'''

import re
import json
import time
import copy
import warnings
import requests
from ciscowebkit.common.pygics import *

import pymysql
from ciscowebkit.common.manager.aci import acitoolkit as acitool

class ACIManager(M):
     
    class APIC(M):
        
        class APIC_CONNECTION_FAILED(E):
            def __init__(self, apic): E.__init__(self, 'Connection Failed %s@%s:%s' % (apic.user, str(apic.ips), apic.pwd))
             
        class APIC_PERSISTENT_ERROR(E):
            def __init__(self): E.__init__(self, 'Access Denied Persistent Data')
            
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
            
        class HealthMon:
            
            def __init__(self, apic):
                self._apic = apic
                self._session = acitool.Session('https://%s' % apic.connected, apic.user, apic.pwd)
                resp = self._session.login()
                if not resp.ok:
                    self._session.close()
                    raise ACIManager.APIC.APIC_CONNECTION_FAILED(apic)
                
            def __del__(self):
                self._session.close()
                
            def __call__(self):
                topology = acitool.HealthScore.get_topology_health(self._session)
                tenant = acitool.HealthScore.get_tenant_health(self._session)
                return M(topology=topology, tenant=tenant)
                
        class EPTracker(Task):
            
            def __init__(self, apic):
                Task.__init__(self, 2, 2)
                self._apic = apic
                self._session = acitool.Session('https://%s' % apic.connected, apic.user, apic.pwd)
                resp = self._session.login()
                if not resp.ok:
                    self._session.close()
                    raise ACIManager.APIC.APIC_CONNECTION_FAILED(apic)
                
                self._table_name = 'aci_%s_eptracker' % apic.domain
                try:
                    self._db = pymysql.connect(user='cisco', password='cisco123', host='localhost')
                    self._cursor = self._db.cursor()
                    self._cursor.execute('USE ciscowebkit;')
                except:
                    self._db.close()
                    self._session.close()
                    raise ACIManager.APIC.APIC_PERSISTENT_ERROR()
                with warnings.catch_warnings():
                    warnings.filterwarnings('ignore')
                    self._cursor.execute('''CREATE TABLE IF NOT EXISTS %s (
                                            mac       CHAR(18) NOT NULL,
                                            ip        CHAR(16),
                                            tenant    CHAR(100) NOT NULL,
                                            app       CHAR(100) NOT NULL,
                                            epg       CHAR(100) NOT NULL,
                                            interface CHAR(100) NOT NULL,
                                            timestart TIMESTAMP NOT NULL,
                                            timestop  TIMESTAMP);''' % self._table_name)
                    self._db.commit()
                endpoints = acitool.Endpoint.get(self._session)
                for ep in endpoints:
                    try: epg = ep.get_parent()
                    except AttributeError: continue
                    app_profile = epg.get_parent()
                    tenant = app_profile.get_parent()
                    if ep.if_dn:
                        for dn in ep.if_dn:
                            match = re.match('protpaths-(\d+)-(\d+)', dn.split('/')[2])
                            if match:
                                if match.group(1) and match.group(2):
                                    int_name = "Nodes: " + match.group(1) + "-" + match.group(2) + " " + ep.if_name
                                    pass
                    else: int_name = ep.if_name
                    try: data = (self._table_name, ep.mac, ep.ip, tenant.name, app_profile.name, epg.name, int_name, self.convert_timestamp_to_mysql(ep.timestamp))
                    except ValueError, e: print str(e); continue
                    ep_exists = self._cursor.execute('''SELECT * FROM %s WHERE mac="%s" AND timestop="0000-00-00 00:00:00";''' % (self._table_name, ep.mac))
                    self._cursor.fetchall()
                    if not ep_exists:
                        self._cursor.execute('''INSERT INTO %s (mac, ip, tenant, app, epg, interface, timestart) VALUES ("%s", "%s", "%s", "%s", "%s", "%s", "%s");''' % data)
                        self._db.commit()
                acitool.Endpoint.subscribe(self._session)
                self.start()
            
            def __del__(self):
                self.stop()
                self._db.close()
                self._session.close()
                
            def __call__(self):
                ret = L()
                cursor = self._db.cursor()
                try:
                    cursor.execute('USE ciscowebkit;')
                    cursor.execute('SELECT * FROM %s;' % self._table_name)
                except:
                    self._db.close()
                    self._db = pymysql.connect(user='cisco', password='cisco123', host='localhost')
                    self._cursor = self._db.cursor()
                    self._cursor.execute('USE ciscowebkit;')
                    cursor.execute('SELECT * FROM %s;' % self._table_name)
                for row in cursor: ret << M(mac=row[0], epg=row[2] + '/' + row[3] + '/' + row[4], ip=row[1], interface=row[5], timestart=str(row[6]), timestop=str(row[7]))
                cursor.close()
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
                                data = (self._table_name, self.convert_timestamp_to_mysql(ep.timestamp), ep.mac, tenant.name)
                                self._cursor.execute('''UPDATE %s SET timestop="%s", timestart=timestart WHERE mac="%s" AND tenant="%s" AND timestop="0000-00-00 00:00:00";''' % data)
                            else:
                                if ep.if_dn:
                                    for dn in ep.if_dn:
                                        match = re.match('protpaths-(\d+)-(\d+)', dn.split('/')[2])
                                        if match:
                                            if match.group(1) and match.group(2):
                                                int_name = "Nodes: " + match.group(1) + "-" + match.group(2) + " " + ep.if_name
                                                pass
                                else: int_name = ep.if_name
                                data = (self._table_name, ep.mac, ep.ip, tenant.name, app_profile.name, epg.name, int_name, self.convert_timestamp_to_mysql(ep.timestamp))
                                self._cursor.execute('''SELECT COUNT(*) FROM %s WHERE mac="%s" AND ip="%s" AND tenant="%s" AND app="%s" AND epg="%s" AND interface="%s" AND timestart="%s";''' % data)
                                for count in self._cursor:
                                    if not count[0]:
                                        self._cursor.execute('''INSERT INTO %s (mac, ip, tenant, app, epg, interface, timestart) VALUES ("%s", "%s", "%s", "%s", "%s", "%s", "%s");''' % data)
                            self._db.commit()
                        else: break
                    except: break
            
            def convert_timestamp_to_mysql(self, timestamp):
                (resp_ts, remaining) = timestamp.split('T')
                resp_ts += ' '
                resp_ts = resp_ts + remaining.split('+')[0].split('.')[0]
                return resp_ts
        
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
                        self.eptracker = ACIManager.APIC.EPTracker(self)
                        self.healthmon = ACIManager.APIC.HealthMon(self)
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
                _tstamp << time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime(init_time - (mon_sec * (i + 1))))
                self.template << None
            self.health = M(_tstamp=_tstamp)
            self.updateHealth()
            self.start()
            
        def __del__(self):
            self.stop()
            
        def updateHealth(self):
            try:
                health_now = copy.deepcopy(self.health)
                health_now._tstamp << time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime(time.time()))
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
        
    def addDomain(self, domain, ips, user, pwd):
        if domain in self._order: return None
        try:
            apic = ACIManager.APIC(self, domain, ips, user, pwd)
            self[domain] = apic
            self._order << domain
            if self.healthmon == None: self.healthmon = ACIManager.HealthTracker(self, self.mon_sec, self.mon_cnt)
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
        return True
    
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
    
     
    
    
     
    
    
    
        
        
    
    
    
    
    
    
    
    
        



