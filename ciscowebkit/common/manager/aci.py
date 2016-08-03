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
        self.aaaLogin()
        
    def aaaLogin(self):
        self['connected'] = None
        connected = None
        for ip in self._apic_ips:
            url = 'https://' + ip + '/api/'
            session = requests.Session()
            try:
                r = session.post(url + 'aaaLogin.json',
                                 data=Struct.CODE2JSON(M(aaaUser=M(attributes=M(name=self.name, pwd=self.pwd)))),
                                 verify=False)
                if r.status_code == 200:
                    self._apic_session = session
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
        
    def getRawData(self, target, query=''):
        if self.connected:
            r = self._apic_session.get(self._apic_url + 'class/%s.json%s' % (target, query), verify=False)
            if r.status_code == 200: return Struct.JSON2DATA(r.text)
        return None
        
    def get(self, target, query=''):
        if self.connected:
            r = self._apic_session.get(self._apic_url + 'class/%s.json%s' % (target, query), verify=False)
            if r.status_code == 200:
                md_list = Struct.JSON2DATA(r.text).imdata
                ret = L()
                for md in md_list:
                    for key in md:
                        attr = md[key].attributes
                        attr['_model'] = key
                        attr['_domain'] = self.domain
                        ret << attr
                return ret
            else: print r.status_code
        return None

class ApicManager(Task, L):
    
    def __init__(self, refresh_sec=300):
        Task.__init__(self, refresh_sec, refresh_sec)
        L.__init__(self)
        
    def __del__(self):
        self.stop()
        
    def addDomain(self, domain, ip, name, pwd):
        for dom in self:
            if dom.domain == domain: return None
        try:
            apic = Apic(domain, ip, name, pwd)
            self << apic
            self.start()
        except: return None
        return apic
        
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
            
    def getRawData(self, target, query='', domain=None):
        if domain: return self[domain].getRawData(target, query)
        ret = M(_order=L())
        for apic in self:
            try:
                ret._order << apic.domain
                ret[apic.domain] = apic.getRawData(target, query)
            except: pass
        return ret
    
    def get(self, target, query='', domain=None):
        if domain: return self[domain].get(target, query)
        ret = M(_order=L())
        for apic in self:
            try:
                ret._order << apic.domain 
                ret[apic.domain] = apic.get(target, query)
            except: pass
        return ret
    
    def getMerged(self, target, query=''):
        ret = L()
        for apic in self:
            try: ret + apic.get(target, query)
            except: pass
        return ret

    #===========================================================================
    # Raw Data
    #===========================================================================
    
    def getFabricNode(self, query='', domain=None):
        return self.get('fabricNode', query, domain)
    
    def getFvTenant(self, query='', domain=None):
        return self.get('fvTenant', query, domain)
    
    def getFvAEPg(self, query='', domain=None):
        return self.get('fvAEPg', query, domain)
    
    def getFvCEp(self, query='', domain=None):
        return self.get('fvCEp', query, domain)
    
    def getFvSubnet(self, query='', domain=None):
        return self.get('fvSubnet', query, domain)
    
    def getVzBrCP(self, query='', domain=None):
        return self.get('vzBrCP', query, domain)
    
    def getVzSubj(self, query='', domain=None):
        return self.get('vzSubj', query, domain)
    
    def getVzRtCons(self, query='', domain=None):
        return self.get('vzRtCons', query, domain)
    
    def getVzRtProv(self, query='', domain=None):
        return self.get('vzRtProv', query, domain)
    
    def getFirmwareRunning(self, query='', domain=None):
        return self.get('firmwareRunning', query, domain)
    
    def getFirmwareCtrlrRunning(self, query='', domain=None):
        return self.get('firmwareCtrlrRunning', query, domain)
    
    def getTopSystem(self, query='', domain=None):
        return self.get('topSystem', query, domain)
    
    #===========================================================================
    # Count Data
    #===========================================================================
    
    def getNoNode(self):
        counts = self.get('fabricNode', '?query-target-filter=ne(fabricNode.role,"controller")&rsp-subtree-include=count')
        for domain in counts._order: counts[domain] = int(counts[domain][0].count)
        return counts
    
    def getNoTenant(self):
        counts = self.get('fvTenant', '?rsp-subtree-include=count')
        for domain in counts._order: counts[domain] = int(counts[domain][0].count)
        return counts
    
    def getNoBD(self):
        counts = self.get('fvBD', '?rsp-subtree-include=count')
        for domain in counts._order: counts[domain] = int(counts[domain][0].count)
        return counts
    
    def getNoEPG(self):
        counts = self.get('fvAEPg', '?rsp-subtree-include=count')
        for domain in counts._order: counts[domain] = int(counts[domain][0].count)
        return counts
    
    def getNoEP(self):
        counts = self.get('fvCEp', '?rsp-subtree-include=count')
        for domain in counts._order: counts[domain] = int(counts[domain][0].count)
        return counts
    
    def getNoFilter(self):
        counts = self.get('vzFilter', '?rsp-subtree-include=count')
        for domain in counts._order: counts[domain] = int(counts[domain][0].count)
        return counts
    
    def getNoContract(self):
        counts = self.get('vzBrCP', '?rsp-subtree-include=count')
        for domain in counts._order: counts[domain] = int(counts[domain][0].count)
        return counts
    
    def getNoL47Device(self):
        counts = self.get('vnsCDev', '?rsp-subtree-include=count')
        for domain in counts._order: counts[domain] = int(counts[domain][0].count)
        return counts
    
    def getNoL47Graph(self):
        counts = self.get('vnsGraphInst', '?rsp-subtree-include=count')
        for domain in counts._order: counts[domain] = int(counts[domain][0].count)
        return counts
    
    def getNoFault(self):
        # severity : cleared info warning minor major critical
        cnt_cleared = APIC.get('faultInfo', '?query-target-filter=eq(faultInfo.severity, "cleared")&rsp-subtree-include=count')
        cnt_info = APIC.get('faultInfo', '?query-target-filter=eq(faultInfo.severity, "info")&rsp-subtree-include=count')
        cnt_warning = APIC.get('faultInfo', '?query-target-filter=eq(faultInfo.severity, "warning")&rsp-subtree-include=count')
        cnt_minor = APIC.get('faultInfo', '?query-target-filter=eq(faultInfo.severity, "minor")&rsp-subtree-include=count')
        cnt_major = APIC.get('faultInfo', '?query-target-filter=eq(faultInfo.severity, "major")&rsp-subtree-include=count')
        cnt_critical = APIC.get('faultInfo', '?query-target-filter=eq(faultInfo.severity, "critical")&rsp-subtree-include=count')
        ret = M()
        for domain in self:
            ret[domain.domain] = M()
            ret[domain.domain]['cleared'] = int(cnt_cleared[domain.domain][0].count)
            ret[domain.domain]['info'] = int(cnt_info[domain.domain][0].count)
            ret[domain.domain]['warning'] = int(cnt_warning[domain.domain][0].count)
            ret[domain.domain]['minor'] = int(cnt_minor[domain.domain][0].count)
            ret[domain.domain]['major'] = int(cnt_major[domain.domain][0].count)
            ret[domain.domain]['critical'] = int(cnt_critical[domain.domain][0].count)
        return ret
    
class ApicPreset:
    
    LINE = MorrisLine
    AREA = MorrisArea
    BAR = MorrisBar
    DONUT = MorrisDonut
    
    @classmethod
    def getDevices(cls):
        node_data = APIC.get('fabricNode', '?order-by=fabricNode.role,fabricNode.name')
        cfrm_data = APIC.get('firmwareCtrlrRunning')
        sfrm_data = APIC.get('firmwareRunning')
        tsys_data = APIC.get('topSystem')
        
        lo = Layout()
        
        for domain in node_data._order:
            ctrl = Table('ID', 'Name', 'Model', 'Serial', 'Version', 'INB Mgmt IP', 'OOB Mgmt IP', 'State', 'Uptime', title='Controller')
            spne = Table('ID', 'Name', 'Model', 'Serial', 'Version', 'INB Mgmt IP', 'OOB Mgmt IP', 'State', 'Uptime', title='Spine')
            leaf = Table('ID', 'Name', 'Model', 'Serial', 'Version', 'INB Mgmt IP', 'OOB Mgmt IP', 'State', 'Uptime', title='Leaf')
            for node in node_data[domain]:
                for tsys in tsys_data[domain]:
                    if node.dn + '/' in tsys.dn:
                        id = tsys.id
                        inb = tsys.inbMgmtAddr
                        oob = tsys.oobMgmtAddr
                        state = tsys.state
                        uptime = tsys.systemUpTime
                        break
                if node.role == 'controller':
                    for firm in cfrm_data[domain]:
                        if node.dn + '/' in firm.dn:
                            ctrl.add(id,
                                     node.name,
                                     node.model,
                                     node.serial,
                                     firm.version,
                                     inb,
                                     oob,
                                     'Service' if state == 'in-service' else 'Enormal',
                                     uptime[:-5])
                            break
                elif node.role == 'spine':
                    for firm in sfrm_data[domain]:
                        if node.dn + '/' in firm.dn:
                            spne.add(id,
                                     node.name,
                                     node.model,
                                     node.serial,
                                     firm.version,
                                     inb,
                                     oob,
                                     'Service' if state == 'in-service' else 'Enormal',
                                     uptime[:-4])
                            break
                elif node.role == 'leaf':
                    for firm in sfrm_data[domain]:
                        if node.dn + '/' in firm.dn:
                            leaf.add(id,
                                     node.name,
                                     node.model,
                                     node.serial,
                                     firm.version,
                                     inb,
                                     oob,
                                     'Service' if state == 'in-service' else 'Enormal',
                                     uptime[:-4])
                            break
                        
            lo.add(Row(Panel(domain, Layout(
                Row(ctrl),
                Row(spne),
                Row(leaf)
                ))))
        return lo
        
    @classmethod
    def getTotalHealthHist(cls, **option):
        tstamp = time.time()
        th_data = APIC.get('fabricOverallHealthHist5min', '?order-by=fabricOverallHealthHist5min.index|desc&page=0&page-size=12')
        th_form = cls.LINE(*th_data._order, **option).grid(0, 100)
        for idx in range(0, 12):
            y = L()
            x = time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(tstamp - (300 * (11 - idx))))
            for domain in th_data._order:
                pnt = len(th_data[domain]) - (12 - idx)
                if pnt >= 0: y << th_data[domain][pnt].healthAvg
                else: y << None
            th_form.add(x, *y)
        return th_form
    
    @classmethod
    def getNodeHealthHist(cls, **option):
        tstamp = time.time()
        node_data = APIC.get('fabricNodeHealthHist5min', '?order-by=fabricNodeHealthHist5min.index|desc,fabricNodeHealthHist5min.dn')
        ylabel = L()
        for domain in node_data._order:
            dom_node_data = node_data[domain]
            ncount = len(dom_node_data) / 12
            for n in range(0, ncount):
                rns = dom_node_data[n].dn.split('/')
                ylabel << domain + '/' + rns[1] + '/' + rns[2]
        node_form = cls.LINE(*ylabel, **option).grid(0, 100)
        for idx in range(0, 12):
            y = L()
            x = time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(tstamp - (300 * (11 - idx))))
            for domain in node_data._order:
                dom_node_data = node_data[domain]
                ncount = len(dom_node_data) / 12
                for n in range(0, ncount):
                    try: y << dom_node_data[ncount * idx + n].healthAvg
                    except: y << None
            node_form.add(x, *y)
        return node_form
        
    @classmethod
    def getNodeHealthCurr(cls, **option):
        node_count = APIC.getNoNode()
        node_data = APIC.get('fabricNodeHealthHist5min', '?order-by=fabricNodeHealthHist5min.index|desc,fabricNodeHealthHist5min.dn')
        node_bar = cls.BAR(**option).grid(0, 100)
        for domain in node_data._order:
            dom_node_data = node_data[domain]
            dom_node_count = node_count[domain]
            for n in reversed(range(1, dom_node_count + 1)):
                rns = dom_node_data[-n].dn.split('/')
                avg = dom_node_data[-n].healthAvg
                node_bar.add(domain + '/' + rns[1] + '/' + rns[2], avg)
        return node_bar
    
    @classmethod
    def getEpgHealthCurr(cls, **option):
        epg_data = APIC.get('healthInst', '?query-target-filter=wcard(healthInst.dn,"^uni/tn-.*/ap-.*/epg-")&order-by=healthInst.dn')
        epg_form = cls.BAR(**option).grid(0, 100)
        for domain in epg_data._order:
            dom_epg_data = epg_data[domain]
            for epg in dom_epg_data:
                rns = epg.dn.split('/')
                epg_form.add(domain + '/' + rns[1][3:] + '/' + rns[2][3:] + '/' + rns[3][4:], epg.cur)
        return epg_form
    
    
    
    
    
        
        
    
    
    
    
    
    
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

if __name__ == '__main__':
    
    
    ad = Apic('domain1', '10.72.86.21/10.72.86.22/10.72.86.23', 'admin', '1234Qwer')
#     print inf(ad)

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
    
    data = ad.getRawData('faultInfo')
    print inf(data)
    
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
    
     
    
