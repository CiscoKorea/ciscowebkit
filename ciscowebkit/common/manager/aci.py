'''
Created on 2016. 7. 20.

@author: "comfact"
'''

import re
import time
import requests
from ciscowebkit.common import *

class Apic(M):
    
    class ApicError(E):
        
        def __init__(self, msg): E.__init__(self, msg)
    
    def __init__(self, domain, ip, name, pwd):
        ip = ip.replace(' ', '')
        M.__init__(self, domain=domain, ip=ip, name=name, pwd=pwd, connected=None)
        sepkv = re.match('^[\d.:]+(?P<sep>[,/&|])', ip)
        if sepkv: self._apic_ips = L(*ip.split(sepkv.group('sep')))
        else: self._apic_ips = L(ip)
        self._apic_session = None
        self._apic_url = None
        self.aaaLogin()
        
    def aaaLogin(self):
        self['connected'] = None
        self._apic_session = None
        connected = None
        for ip in self._apic_ips:
            url = 'https://' + ip + '/api/'
            session = requests.Session()
            try:
                r = session.post(url + 'aaaLogin.json',
                                 data=Struct.CODE2JSON(M(aaaUser=M(attributes=M(name=self.name, pwd=self.pwd)))),
                                 verify=False)
                if r.status_code == 200: self._apic_session = session
                self._apic_url = url
                connected = ip
                break
            except Exception as e: str(e)
        else: raise Apic.ApicError('Connection Failed')
        self._apic_ips.remove(connected)
        self._apic_ips = L(connected, *self._apic_ips)
        self['connected'] = connected
        
    def aaaRefresh(self):
        if self.connected:
            r = self._apic_session.get(self._apic_url + 'aaaRefresh.json', verify=False)
            if r.status_code != 200: self.aaaLogin()
            
    def getRawData(self, *targets):
        if self.connected:
            ret = L()
            for target in targets:
                if not instof(target, tuple): target = (target, '')
                r = self._apic_session.get(self._apic_url + 'class/%s.json%s' % (target), verify=False)
                if r.status_code == 200: ret << Struct.JSON2DATA(r.text)
                else: ret << None
            return ret
        return None
    
    def get(self, *targets):
        if self.connected:
            ret = L()
            for target in targets:
                if not instof(target, tuple): target = (target, '')
                r = self._apic_session.get(self._apic_url + 'class/%s.json%s' % (target), verify=False)
                if r.status_code == 200:
                    imdata = Struct.JSON2DATA(r.text).imdata
                    wellform = L()
                    for im in imdata:
                        for key in im:
                            attr = im[key].attributes
                            attr['_model'] = key
                            attr['_domain'] = self.domain
                            wellform << attr
                    ret << wellform
                else: ret << None
            return ret
        return None
    
    def getHealth(self):
        if self.connected:
            ret = M()
            total, node, epg = self.get('fabricHealthTotal', 
                                   'fabricNodeHealth5min', 
                                   ('healthInst', '?query-target-filter=wcard(healthInst.dn,"^uni/tn-.*/ap-.*/epg-")&order-by=healthInst.dn'))
            for h in total: ret[self.domain + '/' + h.dn.replace('/health', '')] = int(h.cur)
            for h in node:
                rns = h.dn.split('/')
                ret[self.domain + '/' + rns[0] + '/' + rns[1] + '/' + rns[2]] = int(h.healthAvg)
            for h in epg:
                ret[self.domain + '/' + h.dn.replace('/health', '')] = int(h.cur)
            return ret
        return None
        
class ApicManager(L):
    
    class RefreshSession(Task):
        
        def __init__(self, am, refresh_sec):
            Task.__init__(self, refresh_sec, refresh_sec)
            self.am = am
            self.start()
            
        def task(self):
            for apic in self.am:
                try: apic.aaaRefresh()
                except: pass
                
    class Monitoring(Task, M):
        
        def __init__(self, am, monitor_sec):
            Task.__init__(self, monitor_sec)
            M.__init__(self)
            self._am = am
            itime = time.time()
            self._tstamp = [
                            time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(itime - (monitor_sec * 11))),
                            time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(itime - (monitor_sec * 10))),
                            time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(itime - (monitor_sec * 9))),
                            time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(itime - (monitor_sec * 8))),
                            time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(itime - (monitor_sec * 7))),
                            time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(itime - (monitor_sec * 6))),
                            time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(itime - (monitor_sec * 5))),
                            time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(itime - (monitor_sec * 4))),
                            time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(itime - (monitor_sec * 3))),
                            time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(itime - (monitor_sec * 2))),
                            time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(itime - (monitor_sec))),
                            time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(itime))
                            ]
            self.start()
            
        def __call__(self):
            return self
        
        def task(self):
            self._tstamp.append(time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(time.time())))
            for apic in self._am:
                health = apic.getHealth()
                for dn in health:
                    if dn not in self: self[dn] = [None, None, None, None, None, None, None, None, None, None, None, health[dn]]
                    else:
                        self[dn].append(health[dn])
                        self[dn] = self[dn][1:]
            self._tstamp = self._tstamp[1:]
    
    def __init__(self, refresh_sec=300, monitor_sec=300):
        L.__init__(self)
        self.refresh = ApicManager.RefreshSession(self, refresh_sec)
        self._monitor_sec = monitor_sec
        self.monitor = M()
        
    def __del__(self):
        self.refresh.stop()
        self.monitor.stop()
        
    def addDomain(self, domain, ip, name, pwd):
        for dom in self:
            if dom.domain == domain: return None
        try:
            apic = Apic(domain, ip, name, pwd)
            self << apic
            self.monitor = ApicManager.Monitoring(self, self._monitor_sec)
        except: pass
        return self
        
    def delDomain(self, domain):
        apic_ref = None
        for apic in self:
            if apic.domain == domain:
                apic_ref = apic
                break
        if apic_ref: self >> apic_ref
        
    def task(self):
        for apic in self:
            try: apic.aaaRefresh()
            except: pass
            
    def getRawData(self, *targets):
        ret = L()
        result = M()
        for apic in self: result[apic.domain] = apic.getRawData(*targets)
        for i in range(0, len(targets)):
            dom = M(_order=L())
            for apic in self:
                dom._order << apic.domain
                dom[apic.domain] = result[apic.domain][i]
            ret << dom
        if len(ret) == 1: return ret[0]
        return ret
    
    def get(self, *targets):
        ret = L()
        result = M()
        for apic in self: result[apic.domain] = apic.get(*targets)
        for i in range(0, len(targets)):
            dom = M(_order=L())
            for apic in self:
                dom._order << apic.domain
                dom[apic.domain] = result[apic.domain][i]
            ret << dom
        if len(ret) == 1: return ret[0]
        return ret
    
    
    
    #===============================================================================#
    # #===========================================================================# #
    # # Presets                                                                   # #
    # #===========================================================================# #
    #===============================================================================#

    def getCntAll(self):
        cnt = self.get(
            ('fabricNode', '?query-target-filter=ne(fabricNode.role,"controller")&rsp-subtree-include=count'),
            ('fvTenant', '?rsp-subtree-include=count'),
            ('fvBD', '?rsp-subtree-include=count'),
            ('fvAEPg', '?rsp-subtree-include=count'),
            ('fvCEp', '?rsp-subtree-include=count'),
            ('vzFilter', '?rsp-subtree-include=count'),
            ('vzBrCP', '?rsp-subtree-include=count'),
            ('vnsCDev', '?rsp-subtree-include=count'),
            ('vnsGraphInst', '?rsp-subtree-include=count'),
        )
        try:
            for domain in self:
                cnt[0][domain.domain] = int(cnt[0][domain.domain][0].count)
                cnt[1][domain.domain] = int(cnt[1][domain.domain][0].count)
                cnt[2][domain.domain] = int(cnt[2][domain.domain][0].count)
                cnt[3][domain.domain] = int(cnt[3][domain.domain][0].count)
                cnt[4][domain.domain] = int(cnt[4][domain.domain][0].count)
                cnt[5][domain.domain] = int(cnt[5][domain.domain][0].count)
                cnt[6][domain.domain] = int(cnt[6][domain.domain][0].count)
                cnt[7][domain.domain] = int(cnt[7][domain.domain][0].count)
                cnt[8][domain.domain] = int(cnt[8][domain.domain][0].count)
        except Exception as e:
            print inf(self)
            print str(e)
            print 'Count Data', inf(cnt)
            raise Apic.ApicError('getCntAll.cnt')
        
        rf = self.get(
            ('faultInfo', '?query-target-filter=eq(faultInfo.severity, "cleared")&rsp-subtree-include=count'),
            ('faultInfo', '?query-target-filter=eq(faultInfo.severity, "info")&rsp-subtree-include=count'),
            ('faultInfo', '?query-target-filter=eq(faultInfo.severity, "warning")&rsp-subtree-include=count'),
            ('faultInfo', '?query-target-filter=eq(faultInfo.severity, "minor")&rsp-subtree-include=count'),
            ('faultInfo', '?query-target-filter=eq(faultInfo.severity, "major")&rsp-subtree-include=count'),
            ('faultInfo', '?query-target-filter=eq(faultInfo.severity, "critical")&rsp-subtree-include=count')
        )
        try:
            flt = M(_order=L())
            for domain in self:
                flt._order << domain.domain
                flt[domain.domain] = M()
                flt[domain.domain]['cleared'] = int(rf[0][domain.domain][0].count)
                flt[domain.domain]['info'] = int(rf[1][domain.domain][0].count)
                flt[domain.domain]['warning'] = int(rf[2][domain.domain][0].count)
                flt[domain.domain]['minor'] = int(rf[3][domain.domain][0].count)
                flt[domain.domain]['major'] = int(rf[4][domain.domain][0].count)
                flt[domain.domain]['critical'] = int(rf[5][domain.domain][0].count)
            cnt << flt
        except Exception as e:
            print inf(self)
            print str(e)
            print 'Fault Data', inf(rf)
            raise Apic.ApicError('getCntAll.cnt')
        return cnt
    
    def getCntNode(self):
        counts = self.get(('fabricNode', '?query-target-filter=ne(fabricNode.role,"controller")&rsp-subtree-include=count'))
        for domain in counts._order: counts[domain] = int(counts[domain][0].count)
        return counts
    
    def getCntTenant(self):
        counts = self.get(('fvTenant', '?rsp-subtree-include=count'))
        for domain in counts._order: counts[domain] = int(counts[domain][0].count)
        return counts
    
    def getCntBD(self):
        counts = self.get(('fvBD', '?rsp-subtree-include=count'))
        for domain in counts._order: counts[domain] = int(counts[domain][0].count)
        return counts
    
    def getCntEPG(self):
        counts = self.get(('fvAEPg', '?rsp-subtree-include=count'))
        for domain in counts._order: counts[domain] = int(counts[domain][0].count)
        return counts
    
    def getCntEP(self):
        counts = self.get(('fvCEp', '?rsp-subtree-include=count'))
        for domain in counts._order: counts[domain] = int(counts[domain][0].count)
        return counts
    
    def getCntFilter(self):
        counts = self.get(('vzFilter', '?rsp-subtree-include=count'))
        for domain in counts._order: counts[domain] = int(counts[domain][0].count)
        return counts
    
    def getCntContract(self):
        counts = self.get(('vzBrCP', '?rsp-subtree-include=count'))
        for domain in counts._order: counts[domain] = int(counts[domain][0].count)
        return counts
    
    def getCntL47Device(self):
        counts = self.get(('vnsCDev', '?rsp-subtree-include=count'))
        for domain in counts._order: counts[domain] = int(counts[domain][0].count)
        return counts
    
    def getCntL47Graph(self):
        counts = self.get(('vnsGraphInst', '?rsp-subtree-include=count'))
        for domain in counts._order: counts[domain] = int(counts[domain][0].count)
        return counts
    
    def getCntFault(self):
        rf = self.get(
            ('faultInfo', '?query-target-filter=eq(faultInfo.severity, "cleared")&rsp-subtree-include=count'),
            ('faultInfo', '?query-target-filter=eq(faultInfo.severity, "info")&rsp-subtree-include=count'),
            ('faultInfo', '?query-target-filter=eq(faultInfo.severity, "warning")&rsp-subtree-include=count'),
            ('faultInfo', '?query-target-filter=eq(faultInfo.severity, "minor")&rsp-subtree-include=count'),
            ('faultInfo', '?query-target-filter=eq(faultInfo.severity, "major")&rsp-subtree-include=count'),
            ('faultInfo', '?query-target-filter=eq(faultInfo.severity, "critical")&rsp-subtree-include=count')
        )
        flt = M(_order=L())
        for domain in self:
            flt._order << domain.domain
            flt[domain.domain] = M()
            flt[domain.domain]['cleared'] = int(rf[0][domain.domain][0].count)
            flt[domain.domain]['info'] = int(rf[1][domain.domain][0].count)
            flt[domain.domain]['warning'] = int(rf[2][domain.domain][0].count)
            flt[domain.domain]['minor'] = int(rf[3][domain.domain][0].count)
            flt[domain.domain]['major'] = int(rf[4][domain.domain][0].count)
            flt[domain.domain]['critical'] = int(rf[5][domain.domain][0].count)
        return flt

if __name__ == '__main__':
    
    am = ApicManager(monitor_sec=5).addDomain('domain1', '10.72.86.21/10.72.86.22/10.72.86.23', 'admin', '1234Qwer')
    
#     data = am.get(('healthInst', '?query-target-filter=wcard(healthInst.dn,"^uni/tn-.*/ap-.*/epg-")&order-by=healthInst.dn'))
#     print inf(data)
    
#     data = am.getCntL47Graph(); print inf(data)
    
    while True:
        print inf(am.monitor())
        time.sleep(1)
    
    del am
    
    
#     ad = Apic('domain1', '10.72.86.21/10.72.86.22/10.72.86.23', 'admin', '1234Qwer')
#     data = ad.get('fabricHealthTotal'); print inf(data)
#     data = ad.get('fabricNodeHealth5min'); print inf(data)
    
    
    
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