#-*- coding: utf-8 -*-
'''
Created on 2016. 7. 5.

@author: "comfact"
'''

from ciscowebkit.common import *

class Show(Feature):
    
    def __init__(self): Feature.__init__(self, 0, 'fa-eye')

class Device(SubFeature):
    
    '''Devices Information'''
    
    def __init__(self): SubFeature.__init__(self, icon='fa-cogs')
    
    def get(self, request, *cmd):
        if len(APIC) == 0: return InfoBlock('데이터 없음', '연결된 APIC이 없습니다. Setting 메뉴에서 APIC 연결을 추가하세요.')
        
        node_data, cfrm_data, sfrm_data, tsys_data = APIC.get(
                                                              ('fabricNode', '?order-by=fabricNode.role,fabricNode.name'),
                                                              'firmwareCtrlrRunning',
                                                              'firmwareRunning',
                                                              'topSystem'
                                                              )
        
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
            lo(Row(Panel(domain, Layout(Row(ctrl), Row(spne), Row(leaf)))))
            
        return lo
    
class EPG(SubFeature):
    
    '''End-Point Groups Informantion'''
    
    def __init__(self): SubFeature.__init__(self, icon='fa-object-group')
    
class EP(SubFeature):
    
    '''End-Point Informantion'''
    
    def __init__(self): SubFeature.__init__(self, icon='fa-dot-circle-o')

class Contract(SubFeature):
    
    '''Contracts Information'''
    
    def __init__(self): SubFeature.__init__(self, icon='fa-ticket')
    
    def get(self, request, *cmd):
        if len(APIC) == 0: return InfoBlock('데이터 없음', '연결된 APIC이 없습니다. Setting 메뉴에서 APIC 연결을 추가하세요.')
        
        cps, subjs, conss, provs = APIC.get(
                                        ('vzBrCP', '?order-by=vzBrCP.modTs'),
                                        'vzSubj',
                                        'vzRtCons',
                                        'vzRtProv'
                                        )
        
        lo = Layout()
        
        for domain in cps._order:
            ctr_table = Table('Name', 'Tenant', 'Scope', 'Subject', 'Provider', 'Consumer')
            for cp in cps[domain]:
                ctr_rec = L()
                rns = cp.dn.split('/')
                rn = rns[2]
                tenant = rns[1][3:]
                ctr_rec << cp.name << tenant << cp.scope << '' << '' << ''
                for subj in subjs[domain]:
                    if rn in subj.dn:
                        ctr_rec[3] = subj.name
                ctr_rec[4] += '<ul>'
                for prov in provs[domain]:
                    if rn in prov.dn:
                        trns = prov.tDn.split('/')
                        ctr_rec[4] += '<li><small>' + tenant + '/' + trns[2][3:] + '/' + trns[3][4:] + '</small></li>'
                ctr_rec[4] += '</ul>'
                ctr_rec[5] += '<ul>'
                for cons in conss[domain]:
                    if rn in cons.dn:
                        trns = cons.tDn.split('/')
                        ctr_rec[5] += '<li><small>' + tenant + '/' + trns[2][3:] + '/' + trns[3][4:] + '</small></li>'
                ctr_rec[5] += '</ul>'
                ctr_table.add(*ctr_rec)
            lo(Row(Panel(domain, Layout(Row(ctr_table)))))
        
        return lo
