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
                cursor.execute('USE ciscowebkit;')
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
        
    print inf(am.Test1.get('compNic'))
    
    am.delDomain('Test1')
     
    
    
     
    
    
    
        
        
    
    
    
    
    
    
    
    
        







# class Apic(M):
#     
#     class ApicError(E):
#         
#         def __init__(self, msg): E.__init__(self, msg)
#     
#     def __init__(self, domain, ip, name, pwd):
#         ip = ip.replace(' ', '')
#         M.__init__(self, domain=domain, ip=ip, name=name, pwd=pwd, connected=None)
#         sepkv = re.match('^[\d.:]+(?P<sep>[,/&|])', ip)
#         if sepkv: self._apic_ips = L(*ip.split(sepkv.group('sep')))
#         else: self._apic_ips = L(ip)
#         self._apic_session = None
#         self._apic_url = None
#         self.aaaLogin()
#         
#     def aaaLogin(self):
#         self['connected'] = None
#         self._apic_session = None
#         connected = None
#         for ip in self._apic_ips:
#             url = 'https://' + ip + '/api/'
#             session = requests.Session()
#             try:
#                 r = session.post(url + 'aaaLogin.json',
#                                  data=Struct.CODE2JSON(M(aaaUser=M(attributes=M(name=self.name, pwd=self.pwd)))),
#                                  verify=False)
#                 if r.status_code == 200: self._apic_session = session
#                 self._apic_url = url
#                 connected = ip
#                 break
#             except Exception as e: str(e)
#         else: raise Apic.ApicError('Connection Failed')
#         self._apic_ips.remove(connected)
#         self._apic_ips = L(connected, *self._apic_ips)
#         self['connected'] = connected
#         
#     def aaaRefresh(self):
#         if self.connected:
#             r = self._apic_session.get(self._apic_url + 'aaaRefresh.json', verify=False)
#             if r.status_code != 200: self.aaaLogin()
#             
#     def getRawData(self, *targets):
#         if self.connected:
#             ret = L()
#             for target in targets:
#                 if not instof(target, tuple): target = (target, '')
#                 r = self._apic_session.get(self._apic_url + 'class/%s.json%s' % (target), verify=False)
#                 if r.status_code == 200: ret << Struct.JSON2DATA(r.text)
#                 else: ret << None
#             return ret
#         return None
#     
#     def get(self, *targets):
#         if self.connected:
#             ret = L()
#             for target in targets:
#                 if not instof(target, tuple): target = (target, '')
#                 r = self._apic_session.get(self._apic_url + 'class/%s.json%s' % (target), verify=False)
#                 if r.status_code == 200:
#                     imdata = Struct.JSON2DATA(r.text).imdata
#                     wellform = L()
#                     for im in imdata:
#                         for key in im:
#                             attr = im[key].attributes
#                             attr['_model'] = key
#                             attr['_domain'] = self.domain
#                             wellform << attr
#                     ret << wellform
#                 else: ret << None
#             return ret
#         return None
#     
#     def getHealth(self):
#         if self.connected:
#             ret = M(topology=M(), epg=M())
#             total, node, epg = self.get('fabricHealthTotal', 
#                                    'fabricNodeHealth5min', 
#                                    ('healthInst', '?query-target-filter=wcard(healthInst.dn,"^uni/tn-.*/ap-.*/epg-")&order-by=healthInst.dn'))
#             for h in total:
#                 ret.topology[self.domain + '/' + h.dn.replace('/health', '')] = int(h.cur)
#             for h in node:
#                 rns = h.dn.split('/')
#                 ret.topology[self.domain + '/' + rns[0] + '/' + rns[1] + '/' + rns[2]] = int(h.healthAvg)
#             for h in epg:
#                 rns = h.dn.split('/')
#                 ret.epg[self.domain + '/' + rns[1][3:] + '/' + rns[2][3:] + '/' + rns[3][4:]] = int(h.cur)
#                 
#             return ret
#         return None
#         
# class ApicManager(L):
#     
#     class RefreshSession(Task):
#         
#         def __init__(self, am, refresh_sec):
#             Task.__init__(self, refresh_sec, refresh_sec)
#             self.am = am
#             self.start()
#             
#         def task(self):
#             for apic in self.am:
#                 try: apic.aaaRefresh()
#                 except: pass
#                 
#     class Monitoring(Task):
#         
#         def __init__(self, am, monitor_sec):
#             Task.__init__(self, monitor_sec)
#             self._am = am
#             self._mondata = M(topology=M(), epg=M())
#             self._mutex = Mutex()
#             itime = time.time()
#             self._mondata['_tstamp'] = [
#                             time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(itime - (monitor_sec * 11))),
#                             time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(itime - (monitor_sec * 10))),
#                             time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(itime - (monitor_sec * 9))),
#                             time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(itime - (monitor_sec * 8))),
#                             time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(itime - (monitor_sec * 7))),
#                             time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(itime - (monitor_sec * 6))),
#                             time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(itime - (monitor_sec * 5))),
#                             time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(itime - (monitor_sec * 4))),
#                             time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(itime - (monitor_sec * 3))),
#                             time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(itime - (monitor_sec * 2))),
#                             time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(itime - (monitor_sec))),
#                             time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(itime))
#                             ]
#             self.start()
#             
#         def __call__(self):
#             self._mutex.lock()
#             ret = copy.deepcopy(self._mondata)
#             self._mutex.unlock()
#             return ret
#         
#         def task(self):
#             self._mutex.lock()
#             
#             self._mondata._tstamp.append(time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(time.time())))
#             for apic in self._am:
#                 health = apic.getHealth()
#                 for dn in health.topology:
#                     if dn not in self._mondata.topology: self._mondata.topology[dn] = [None, None, None, None, None, None, None, None, None, None, None, None, health.topology[dn]]
#                     else: self._mondata.topology[dn].append(health.topology[dn])
#                 for dn in health.epg:
#                     if dn not in self._mondata.epg: self._mondata.epg[dn] = [None, None, None, None, None, None, None, None, None, None, None, None, health.epg[dn]]
#                     else: self._mondata.epg[dn].append(health.epg[dn])
#             
#             del_list = L()
#             for dn in self._mondata.topology:
#                 self._mondata.topology[dn].pop(0)
#                 if len(self._mondata.topology[dn]) < 12: del_list << dn
#             for dn in del_list: self._mondata.topology >> dn
#             
#             del_list = L()
#             for dn in self._mondata.epg:
#                 self._mondata.epg[dn].pop(0)
#                 if len(self._mondata.epg[dn]) < 12: del_list << dn
#             for dn in del_list: self._mondata.epg>> dn
# 
#             self._mutex.unlock()
#     
#     def __init__(self, refresh_sec=300, monitor_sec=300):
#         L.__init__(self)
#         self.refresh = ApicManager.RefreshSession(self, refresh_sec)
#         self._monitor_sec = monitor_sec
#         self.monitor = M()
#         
#     def __del__(self):
#         self.refresh.stop()
#         self.monitor.stop()
#         
#     def addDomain(self, domain, ip, name, pwd):
#         for dom in self:
#             if dom.domain == domain: return None
#         try:
#             apic = Apic(domain, ip, name, pwd)
#             self << apic
#             self.monitor = ApicManager.Monitoring(self, self._monitor_sec)
#         except: return None
#         return apic
#         
#     def delDomain(self, domain):
#         apic_ref = None
#         for apic in self:
#             if apic.domain == domain:
#                 apic_ref = apic
#                 break
#         if apic_ref: self >> apic_ref
#         
#     def task(self):
#         for apic in self:
#             try: apic.aaaRefresh()
#             except: pass
#             
#     def getRawData(self, *targets):
#         ret = L()
#         result = M()
#         for apic in self: result[apic.domain] = apic.getRawData(*targets)
#         for i in range(0, len(targets)):
#             dom = M(_order=L())
#             for apic in self:
#                 dom._order << apic.domain
#                 dom[apic.domain] = result[apic.domain][i]
#             ret << dom
#         if len(ret) == 1: return ret[0]
#         return ret
#     
#     def get(self, *targets):
#         ret = L()
#         result = M()
#         for apic in self: result[apic.domain] = apic.get(*targets)
#         for i in range(0, len(targets)):
#             dom = M(_order=L())
#             for apic in self:
#                 dom._order << apic.domain
#                 dom[apic.domain] = result[apic.domain][i]
#             ret << dom
#         if len(ret) == 1: return ret[0]
#         return ret
#     
#     
#     
#     #===============================================================================#
#     # #===========================================================================# #
#     # # Presets                                                                   # #
#     # #===========================================================================# #
#     #===============================================================================#
# 
#     def getCntAll(self):
#         cnt = self.get(
#             ('fabricNode', '?query-target-filter=ne(fabricNode.role,"controller")&rsp-subtree-include=count'),
#             ('fvTenant', '?rsp-subtree-include=count'),
#             ('fvBD', '?rsp-subtree-include=count'),
#             ('fvAEPg', '?rsp-subtree-include=count'),
#             ('fvCEp', '?rsp-subtree-include=count'),
#             ('vzFilter', '?rsp-subtree-include=count'),
#             ('vzBrCP', '?rsp-subtree-include=count'),
#             ('vnsCDev', '?rsp-subtree-include=count'),
#             ('vnsGraphInst', '?rsp-subtree-include=count'),
#         )
#         try:
#             for domain in self:
#                 cnt[0][domain.domain] = int(cnt[0][domain.domain][0].count)
#                 cnt[1][domain.domain] = int(cnt[1][domain.domain][0].count)
#                 cnt[2][domain.domain] = int(cnt[2][domain.domain][0].count)
#                 cnt[3][domain.domain] = int(cnt[3][domain.domain][0].count)
#                 cnt[4][domain.domain] = int(cnt[4][domain.domain][0].count)
#                 cnt[5][domain.domain] = int(cnt[5][domain.domain][0].count)
#                 cnt[6][domain.domain] = int(cnt[6][domain.domain][0].count)
#                 cnt[7][domain.domain] = int(cnt[7][domain.domain][0].count)
#                 cnt[8][domain.domain] = int(cnt[8][domain.domain][0].count)
#         except Exception as e:
#             print str(e)
#             print 'Count Data', inf(cnt)
#             raise Apic.ApicError('getCntAll.cnt')
#         
#         rf = self.get(
#             ('faultInfo', '?query-target-filter=eq(faultInfo.severity, "cleared")&rsp-subtree-include=count'),
#             ('faultInfo', '?query-target-filter=eq(faultInfo.severity, "info")&rsp-subtree-include=count'),
#             ('faultInfo', '?query-target-filter=eq(faultInfo.severity, "warning")&rsp-subtree-include=count'),
#             ('faultInfo', '?query-target-filter=eq(faultInfo.severity, "minor")&rsp-subtree-include=count'),
#             ('faultInfo', '?query-target-filter=eq(faultInfo.severity, "major")&rsp-subtree-include=count'),
#             ('faultInfo', '?query-target-filter=eq(faultInfo.severity, "critical")&rsp-subtree-include=count')
#         )
#         try:
#             flt = M(_order=L())
#             for domain in self:
#                 flt._order << domain.domain
#                 flt[domain.domain] = M()
#                 flt[domain.domain]['cleared'] = int(rf[0][domain.domain][0].count)
#                 flt[domain.domain]['info'] = int(rf[1][domain.domain][0].count)
#                 flt[domain.domain]['warning'] = int(rf[2][domain.domain][0].count)
#                 flt[domain.domain]['minor'] = int(rf[3][domain.domain][0].count)
#                 flt[domain.domain]['major'] = int(rf[4][domain.domain][0].count)
#                 flt[domain.domain]['critical'] = int(rf[5][domain.domain][0].count)
#             cnt << flt
#         except Exception as e:
#             print str(e)
#             print 'Fault Data', inf(rf)
#             raise Apic.ApicError('getCntAll.cnt')
#         return cnt
#     
#     def getCntNode(self):
#         counts = self.get(('fabricNode', '?query-target-filter=ne(fabricNode.role,"controller")&rsp-subtree-include=count'))
#         for domain in counts._order: counts[domain] = int(counts[domain][0].count)
#         return counts
#     
#     def getCntTenant(self):
#         counts = self.get(('fvTenant', '?rsp-subtree-include=count'))
#         for domain in counts._order: counts[domain] = int(counts[domain][0].count)
#         return counts
#     
#     def getCntBD(self):
#         counts = self.get(('fvBD', '?rsp-subtree-include=count'))
#         for domain in counts._order: counts[domain] = int(counts[domain][0].count)
#         return counts
#     
#     def getCntEPG(self):
#         counts = self.get(('fvAEPg', '?rsp-subtree-include=count'))
#         for domain in counts._order: counts[domain] = int(counts[domain][0].count)
#         return counts
#     
#     def getCntEP(self):
#         counts = self.get(('fvCEp', '?rsp-subtree-include=count'))
#         for domain in counts._order: counts[domain] = int(counts[domain][0].count)
#         return counts
#     
#     def getCntFilter(self):
#         counts = self.get(('vzFilter', '?rsp-subtree-include=count'))
#         for domain in counts._order: counts[domain] = int(counts[domain][0].count)
#         return counts
#     
#     def getCntContract(self):
#         counts = self.get(('vzBrCP', '?rsp-subtree-include=count'))
#         for domain in counts._order: counts[domain] = int(counts[domain][0].count)
#         return counts
#     
#     def getCntL47Device(self):
#         counts = self.get(('vnsCDev', '?rsp-subtree-include=count'))
#         for domain in counts._order: counts[domain] = int(counts[domain][0].count)
#         return counts
#     
#     def getCntL47Graph(self):
#         counts = self.get(('vnsGraphInst', '?rsp-subtree-include=count'))
#         for domain in counts._order: counts[domain] = int(counts[domain][0].count)
#         return counts
#     
#     def getCntFault(self):
#         rf = self.get(
#             ('faultInfo', '?query-target-filter=eq(faultInfo.severity, "cleared")&rsp-subtree-include=count'),
#             ('faultInfo', '?query-target-filter=eq(faultInfo.severity, "info")&rsp-subtree-include=count'),
#             ('faultInfo', '?query-target-filter=eq(faultInfo.severity, "warning")&rsp-subtree-include=count'),
#             ('faultInfo', '?query-target-filter=eq(faultInfo.severity, "minor")&rsp-subtree-include=count'),
#             ('faultInfo', '?query-target-filter=eq(faultInfo.severity, "major")&rsp-subtree-include=count'),
#             ('faultInfo', '?query-target-filter=eq(faultInfo.severity, "critical")&rsp-subtree-include=count')
#         )
#         flt = M(_order=L())
#         for domain in self:
#             flt._order << domain.domain
#             flt[domain.domain] = M()
#             flt[domain.domain]['cleared'] = int(rf[0][domain.domain][0].count)
#             flt[domain.domain]['info'] = int(rf[1][domain.domain][0].count)
#             flt[domain.domain]['warning'] = int(rf[2][domain.domain][0].count)
#             flt[domain.domain]['minor'] = int(rf[3][domain.domain][0].count)
#             flt[domain.domain]['major'] = int(rf[4][domain.domain][0].count)
#             flt[domain.domain]['critical'] = int(rf[5][domain.domain][0].count)
#         return flt







# if __name__ == '__main__':
    
#     am = ApicManager(monitor_sec=5).addDomain('domain1', '10.72.86.21/10.72.86.22/10.72.86.23', 'admin', '1234Qwer')
#     while True:
#         print inf(am.monitor())
#         time.sleep(1)
#     del am

#     ad = Apic('domain1', '10.72.86.21/10.72.86.22/10.72.86.23', 'admin', '1234Qwer')
#     data = ad.get(('fvRsCons', '?query-target-filter=wcard(fvRsCons.dn,"/out-")'),); print inf(data), len(data[0])
#     data = ad.get(('l3extInstP', ''),); print inf(data), len(data[0])
    
#     data = ad.get('compVNic'); print inf(data), len(data[0])
    
    
    
#     print inf(ad)

#     ret = ad.getAllCount(); print inf(ret)
    
#     ret = ad.getTotalHealthHist(); print inf(ret)

#     data = ad.get('fvTenant', 'fvAEPg')
#     print inf(data)

#     data = ad.getRawData('fabricNode', '?rsp-subtree-include=count')
#     print inf(data)

#     data = ad.getRawData('fvTenant', '?rsp-subtree-include=count')
#     print inf(data)
    
#     data = ad.getRawData('fvBD', '?rsp-subtree-include=count')
#     print inf(data)

#     data = ad.getRawData('fvAEPg', '?rsp-subtree-include=count')
#     print inf(data)
    
#     data = ad.getRawData('fvCEp', '?rsp-subtree-include=count')
#     print inf(data)
    
#     data = ad.getRawData('vzFilter', '?rsp-subtree-include=count')
#     print inf(data)
    
#     data = ad.getRawData('vzBrCP', '?rsp-subtree-include=count')
#     print inf(data)
    
#     data = ad.getRawData('vnsCDev', '?rsp-subtree-include=count')
#     print inf(data)

#     data = ad.getRawData('vnsGraphInst', '?rsp-subtree-include=count')
#     print inf(data)
    
    # severity : cleared info warning minor major critical
#     data = ad.getRawData('faultInfo', '?query-target-filter=eq(faultInfo.severity, "critical")&rsp-subtree-include=count')
#     print inf(data)
#     
#     data = ad.getRawData('faultInfo', '?query-target-filter=eq(faultInfo.severity, "major")&rsp-subtree-include=count')
#     print inf(data)
#     
#     data = ad.getRawData('faultInfo', '?query-target-filter=eq(faultInfo.severity, "minor")&rsp-subtree-include=count')
#     print inf(data)
#     
#     data = ad.getRawData('faultInfo', '?rsp-subtree-include=count')
#     print inf(data)
    
#     data = ad.getRawData('fvTenant')
#     print inf(data)
    
    
    
#     data = ad.get('fabricNodeHealth5min', '')
#     print inf(data)
#     print len(data)
#     
#     data = ad.get('fabricHealthTotal', '')
#     print inf(data)
#     print len(data)
    
#     data = ad.get('fabricNodeHealthHist5min', '?query-target-filter=eq(fabricNodeHealthHist5min.index,"0")')
#     print inf(data)
#     print len(data)
    
#     data = ad.get('fabricNodeHealthHist5min', '?query-target-filter=eq(fabricNodeHealthHist5min.dn,"topology/pod-1/node-1001/sys/HDfabricNodeHealth5min-0")')
#     print inf(data)
#     print len(data)
    
#     data = ad.get('fabricNodeHealth', '?order-by=fabricNodeHealth.dn|desc')
#     print inf(data)
#     print len(data)

#     data = ad.get('fabricOverallHealth', '')
#     print inf(data)
#     print len(data)


#     data = ad.get('fabricNodeHealthHist5min', '?order-by=fabricNodeHealthHist5min.index|desc')
#     print inf(data)
#     print len(data)

#     data = ad.__get__('fvAEPg', '?rsp-subtree-include=health')
#     print inf(data)
#     print len(data)

#     data = ad.get('fvAEPg')
#     print inf(data)
#     print len(data)
    
#     data = ad.get('healthInst', '?query-target-filter=wcard(healthInst.dn,"^uni/tn-.*/ap-.*/epg-")&order-by=healthInst.dn')
#     print inf(data)
#     print len(data)
    
#     data = ad.get('healthInst', '?query-target-filter=wcard(healthInst.dn,"^uni*")')
#     print inf(data)
#     print len(data)

    #===========================================================================
    # Total health 30
    #===========================================================================
#     data = ad.get('fabricOverallHealthHist5min', '?order-by=fabricOverallHealthHist5min.index|desc&page=0&page-size=30')
#     print inf(data)
#     print len(data)
    
     
    















#     #===========================================================================
#     # Raw Data
#     #===========================================================================
#     
#     def getFabricNode(self, query='', domain=None):
#         return self.get('fabricNode', query, domain)
#     
#     def getFvTenant(self, query='', domain=None):
#         return self.get('fvTenant', query, domain)
#     
#     def getFvAEPg(self, query='', domain=None):
#         return self.get('fvAEPg', query, domain)
#     
#     def getFvCEp(self, query='', domain=None):
#         return self.get('fvCEp', query, domain)
#     
#     def getFvSubnet(self, query='', domain=None):
#         return self.get('fvSubnet', query, domain)
#     
#     def getVzBrCP(self, query='', domain=None):
#         return self.get('vzBrCP', query, domain)
#     
#     def getVzSubj(self, query='', domain=None):
#         return self.get('vzSubj', query, domain)
#     
#     def getVzRtCons(self, query='', domain=None):
#         return self.get('vzRtCons', query, domain)
#     
#     def getVzRtProv(self, query='', domain=None):
#         return self.get('vzRtProv', query, domain)
#     
#     def getFirmwareRunning(self, query='', domain=None):
#         return self.get('firmwareRunning', query, domain)
#     
#     def getFirmwareCtrlrRunning(self, query='', domain=None):
#         return self.get('firmwareCtrlrRunning', query, domain)
#     
#     def getTopSystem(self, query='', domain=None):
#         return self.get('topSystem', query, domain)
















# class ApicPreset:
#     
#     LINE = MorrisLine
#     AREA = MorrisArea
#     BAR = MorrisBar
#     DONUT = MorrisDonut
#     
#     @classmethod
#     def getTotalHealthHist(cls, **option):
#         tstamp = time.time()
#         th_data = APIC.get('fabricOverallHealthHist5min', '?order-by=fabricOverallHealthHist5min.index|desc&page=0&page-size=12')
#         th_form = cls.LINE(*th_data._order, **option).grid(0, 100)
#         for idx in range(0, 12):
#             y = L()
#             x = time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(tstamp - (300 * (11 - idx))))
#             for domain in th_data._order:
#                 pnt = len(th_data[domain]) - (12 - idx)
#                 if pnt >= 0: y << th_data[domain][pnt].healthAvg
#                 else: y << None
#             th_form.add(x, *y)
#         return th_form
#     
#     @classmethod
#     def getNodeHealthHist(cls, **option):
#         tstamp = time.time()
#         node_data = APIC.get('fabricNodeHealthHist5min', '?order-by=fabricNodeHealthHist5min.index|desc,fabricNodeHealthHist5min.dn')
#         ylabel = L()
#         for domain in node_data._order:
#             dom_node_data = node_data[domain]
#             ncount = len(dom_node_data) / 12
#             for n in range(0, ncount):
#                 rns = dom_node_data[n].dn.split('/')
#                 ylabel << domain + '/' + rns[1] + '/' + rns[2]
#         node_form = cls.LINE(*ylabel, **option).grid(0, 100)
#         for idx in range(0, 12):
#             y = L()
#             x = time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(tstamp - (300 * (11 - idx))))
#             for domain in node_data._order:
#                 dom_node_data = node_data[domain]
#                 ncount = len(dom_node_data) / 12
#                 for n in range(0, ncount):
#                     try: y << dom_node_data[ncount * idx + n].healthAvg
#                     except: y << None
#             node_form.add(x, *y)
#         return node_form
#         
#     @classmethod
#     def getNodeHealthCurr(cls, **option):
#         node_count = APIC.getNoNode()
#         node_data = APIC.get('fabricNodeHealthHist5min', '?order-by=fabricNodeHealthHist5min.index|desc,fabricNodeHealthHist5min.dn')
#         node_bar = cls.BAR(**option).grid(0, 100)
#         for domain in node_data._order:
#             dom_node_data = node_data[domain]
#             dom_node_count = node_count[domain]
#             for n in reversed(range(1, dom_node_count + 1)):
#                 rns = dom_node_data[-n].dn.split('/')
#                 avg = dom_node_data[-n].healthAvg
#                 node_bar.add(domain + '/' + rns[1] + '/' + rns[2], avg)
#         return node_bar
#     
#     @classmethod
#     def getEpgHealthCurr(cls, **option):
#         epg_data = APIC.get('healthInst', '?query-target-filter=wcard(healthInst.dn,"^uni/tn-.*/ap-.*/epg-")&order-by=healthInst.dn')
#         epg_form = cls.BAR(**option).grid(0, 100)
#         for domain in epg_data._order:
#             dom_epg_data = epg_data[domain]
#             for epg in dom_epg_data:
#                 rns = epg.dn.split('/')
#                 epg_form.add(domain + '/' + rns[1][3:] + '/' + rns[2][3:] + '/' + rns[3][4:], epg.cur)
#         return epg_form
#     
#     def getSubnet(self):
#         subnets = L()
#         sn_list = self.get_fvSubnet('?order-by=fvSubnet.scope|desc,fvSubnet.dn')
#         for sn in sn_list:
#             rn_list = sn.dn.split('/')
#             subnets << M(_domain = sn._domain,
#                          _model = sn._model,
#                          cidr=sn.ip,
#                          tenant=rn_list[1][3:],
#                          bd=rn_list[2][3:],
#                          preferred=sn.preferred,
#                          scope=sn.scope)
#         return subnets
#     
#     def getContract(self):
#         contracts = L()
#         cp_data = self.get_with_domain('vzBrCP', '?order-by=vzBrCP.modTs')
#         subj_data = self.get_with_domain('vzSubj')
#         cons_data = self.get_with_domain('vzRtCons')
#         prov_data = self.get_with_domain('vzRtProv')
#         for domain in cp_data._order:
#             cp_list = cp_data[domain]
#             dcontracts = L()
#             for cp in cp_list:
#                 rn_list = cp.dn.split('/')
#                 dcontracts << M(_domain=cp._domain,
#                                 _model=cp._model,
#                                 dn=cp.dn,
#                                 name=cp.name,
#                                 scope=cp.scope,
#                                 tenant=rn_list[1][3:],
#                                 rn=rn_list[2],
#                                 subject='',
#                                 cons=L(),
#                                 prov=L(),
#                                 num_cons=0,
#                                 num_prov=0)
#             for contract in dcontracts:
#                 for subj in subj_data[domain]:
#                     if contract.rn in subj.dn:
#                         contract['subject'] = subj.name 
#                 for cons in cons_data[domain]:
#                     if contract.rn in cons.dn:
#                         trn_list = cons.tDn.split('/')
#                         contract.cons << contract.tenant + '/' + trn_list[2][3:] + '/' + trn_list[3][4:]
#                         contract['num_cons'] += 1
#                 for prov in prov_data[domain]:
#                     if contract.rn in prov.dn:
#                         trn_list = prov.tDn.split('/')
#                         contract.prov << contract.tenant + '/' + trn_list[2][3:] + '/' + trn_list[3][4:]
#                         contract['num_prov'] += 1
#             contracts + dcontracts
#         return contracts