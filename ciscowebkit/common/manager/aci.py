'''
Created on 2016. 7. 20.

@author: "comfact"
'''

import re
import requests
from ciscowebkit.common.pygics import *

class Apic(M):
    
    class ApicError(E):

        def __init__(self, msg):
            E.__init__(self, msg)
    
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
            except: pass
        else: raise Apic.ApicError('Connection Failed')
        self._apic_ips.remove(connected)
        self._apic_ips = L(connected, *self._apic_ips)
        self['connected'] = connected
            
    def aaaRefresh(self):
        if self.connected:
            r = self._apic_session.get(self._apic_url + 'aaaRefresh.json', verify=False)
            if r.status_code == 200: return
        self.aaaLogin()
        
    def __get__(self, target, query=''):
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
            elif r.status_code == 400: return None
            elif r.status_code == 401: return self.get(target, query)
            else:
                print r.status_code
        return None
    
class ApicDomain(Task, L):
    
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
            
    def __get__(self, target, query=''):
        ret = M(_order=L())
        for apic in self:
            try:
                ret._order << apic.domain
                ret[apic.domain] = apic.__get__(target, query)
            except: pass
        return ret
            
    def get(self, target, query=''):
        ret = L()
        for apic in self:
            try: ret + apic.get(target, query)
            except: pass
        return ret
    
    def get_with_domain(self, target, query=''):
        ret = M(_order=L())
        for apic in self:
            try:
                ret._order << apic.domain 
                ret[apic.domain] = apic.get(target, query)
            except: pass
        return ret

    #===========================================================================
    # Raw Data
    #===========================================================================
    
    def get_fabricNode(self, query=''):
        return self.get('fabricNode', query)
    
    def get_fvTenant(self, query=''):
        return self.get('fvTenant', query)
    
    def get_fvAEPg(self, query=''):
        return self.get('fvAEPg', query)
    
    def get_fvCEp(self, query=''):
        return self.get('fvCEp', query)
    
    def get_fvSubnet(self, query=''):
        return self.get('fvSubnet', query)
    
    def get_vzBrCP(self, query=''):
        return self.get('vzBrCP', query)
    
    def get_vzSubj(self, query=''):
        return self.get('vzSubj', query)
    
    def get_vzRtCons(self, query=''):
        return self.get('vzRtCons', query)
    
    def get_vzRtProv(self, query=''):
        return self.get('vzRtProv', query)
    
    def get_firmwareRunning(self, query=''):
        return self.get('firmwareRunning', query)
    
    def get_firmwareCtrlrRunning(self, query=''):
        return self.get('firmwareCtrlrRunning', query)
    
    def get_topSystem(self, query=''):
        return self.get('topSystem', query)
    
    #===========================================================================
    # Mining Data
    #===========================================================================
    
    def getSubnet(self):
        subnets = L()
        sn_list = self.get_fvSubnet('?order-by=fvSubnet.scope|desc,fvSubnet.dn')
        for sn in sn_list:
            rn_list = sn.dn.split('/')
            subnets << M(_domain = sn._domain,
                         _model = sn._model,
                         cidr=sn.ip,
                         tenant=rn_list[1][3:],
                         bd=rn_list[2][3:],
                         preferred=sn.preferred,
                         scope=sn.scope)
        return subnets
    
    def getContract(self):
        contracts = L()
        cp_data = self.get_with_domain('vzBrCP', '?order-by=vzBrCP.modTs')
        subj_data = self.get_with_domain('vzSubj')
        cons_data = self.get_with_domain('vzRtCons')
        prov_data = self.get_with_domain('vzRtProv')
        for domain in cp_data._order:
            cp_list = cp_data[domain]
            dcontracts = L()
            for cp in cp_list:
                rn_list = cp.dn.split('/')
                dcontracts << M(_domain=cp._domain,
                                _model=cp._model,
                                dn=cp.dn,
                                name=cp.name,
                                scope=cp.scope,
                                tenant=rn_list[1][3:],
                                rn=rn_list[2],
                                subject='',
                                cons=L(),
                                prov=L(),
                                num_cons=0,
                                num_prov=0)
            for contract in dcontracts:
                for subj in subj_data[domain]:
                    if contract.rn in subj.dn:
                        contract['subject'] = subj.name 
                for cons in cons_data[domain]:
                    if contract.rn in cons.dn:
                        trn_list = cons.tDn.split('/')
                        contract.cons << contract.tenant + '/' + trn_list[2][3:] + '/' + trn_list[3][4:]
                        contract['num_cons'] += 1
                for prov in prov_data[domain]:
                    if contract.rn in prov.dn:
                        trn_list = prov.tDn.split('/')
                        contract.prov << contract.tenant + '/' + trn_list[2][3:] + '/' + trn_list[3][4:]
                        contract['num_prov'] += 1
            contracts + dcontracts
        return contracts

if __name__ == '__main__':
    
#     ad = ApicDomain()
#     ad.addDomain('domain1', '10.72.86.21/10.72.86.22/10.72.86.23', 'admin', '1234Qwer')
#     ad.stop()
    
    ad = Apic('domain1', '10.72.86.21/10.72.86.22/10.72.86.23', 'admin', '1234Qwer')
#     print inf(ad)
    
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
    
    data = ad.get('healthInst', '?query-target-filter=wcard(healthInst.dn,"^uni/tn-.*/ap-.*/epg-")&order-by=healthInst.dn')
    print inf(data)
    print len(data)
    
#     data = ad.get('healthInst', '?query-target-filter=wcard(healthInst.dn,"^uni*")')
#     print inf(data)
#     print len(data)

    #===========================================================================
    # Total health 30
    #===========================================================================
#     data = ad.get('fabricOverallHealthHist5min', '?order-by=fabricOverallHealthHist5min.index|desc&page=0&page-size=30')
#     print inf(data)
#     print len(data)
    
     
    
