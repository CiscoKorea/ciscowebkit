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
        
        lo = Layout()
        
        node_data, cfrm_data, sfrm_data, tsys_data = APIC.get(
                                                              ('fabricNode', '?order-by=fabricNode.role,fabricNode.name'),
                                                              'firmwareCtrlrRunning',
                                                              'firmwareRunning',
                                                              'topSystem'
                                                              )
        
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
            lo(Row(Panel(domain, Layout(Row(ctrl), Row(spne), Row(leaf)), icon='fa-table')))
            
        return lo
    
class EPG(SubFeature):
    
    '''End-Point Groups Informantion'''
    
    def __init__(self): SubFeature.__init__(self, icon='fa-object-group')
    
    def get(self, request, *cmd):
        if len(APIC) == 0: return InfoBlock('데이터 없음', '연결된 APIC이 없습니다. Setting 메뉴에서 APIC 연결을 추가하세요.')
        
        lo = Layout()
        
        epgs, ctxs, bds, provs, conss, paths = APIC.get(
                                                        ('fvAEPg', '?order-by=fvAEPg.dn'),
                                                        'fvCtx',
                                                        'fvBD',
                                                        'vzRtProv',
                                                        'vzRtCons',
                                                        'fvRsPathAtt'
                                                        )
        
        for domain in epgs._order:
            egtable = Table('EPG', 'Tenant', 'App Profile', 'Bridge Domain', 'Context', 'Provided Contract', 'Consumed Contract', 'Binding Path', 'Encap') 
            
            for epg in epgs[domain]:
                rns = epg.dn.split('/')
                name = epg.name
                tenant = rns[1][3:]
                app = rns[2][3:]
                bd_data = ''
                ctx_data = ''
                provided = '<ul style="margin:0px">'
                consumed = '<ul style="margin:0px">'
                binding = '<ul style="margin:0px">'
                encap = ' '
                
                for bd in bds[domain]:
                    if epg.scope == bd.scope:
                        bd_data = bd.name
                        break
                
                for ctx in ctxs[domain]:
                    if epg.scope == ctx.scope:
                        ctx_data = ctx.name
                        break
                    
                for prov in provs[domain]:
                    if epg.dn == prov.tDn:
                        provided += '<li>' + prov.dn.split('/')[2][4:] + '</li>'
                
                for cons in conss[domain]:
                    if epg.dn == cons.tDn:
                        consumed += '<li>' + cons.dn.split('/')[2][4:] + '</li>'
                
                for path in paths[domain]:
                    if epg.dn in path.dn:
                        trns = path.tDn.split('/')
                        binding += '<li>' + trns[1][4:] + '/' + (trns[2][10:] if 'protpaths' in trns[2] else trns[2][6:]) + '/' + path.tDn.split('[')[1][:-1] + '</li>'
                        if encap == ' ': encap = path.encap
                        
                provided += '</ul>'
                consumed += '</ul>'
                binding += '</ul>'
                
                egtable.add(name, tenant, app, bd_data, ctx_data, provided, consumed, binding, encap)
            
            lo(Row(Panel(domain, egtable, icon='fa-table')))
        
        return lo
    
class EP(SubFeature):
    
    '''End-Point Informantion'''
    
    def __init__(self): SubFeature.__init__(self, icon='fa-dot-circle-o')
    
    def get(self, request, *cmd):
        if len(APIC) == 0: return InfoBlock('데이터 없음', '연결된 APIC이 없습니다. Setting 메뉴에서 APIC 연결을 추가하세요.')
        
        lo = Layout()
        
        ceps, paths, nics = APIC.get(
                                     ('fvCEp', '?order-by=fvCEp.dn'),
                                     'fvRsCEpToPathEp',
                                     'compNic'
                                     )
        
        for domain in ceps._order:
            eptable = Table('Mac', 'EPG', 'IP', 'Interface', 'Encap', 'Nic Type', 'Computing')
            
            for cep in ceps[domain]:
                rns = cep.dn.split('/')
                epg = rns[1][3:] + '/' + rns[2][3:] + '/' + rns[3][4:]
                mac = cep.mac
                ip = cep.ip
                intf = None
                encap = cep.encap
                nic_type = '<ul style="margin:0px">'
                comp = '<ul style="margin:0px">'
                
                for path in paths[domain]:
                    if cep.dn in path.dn:
                        path_trns = path.tDn.split('/')
                        intf = path_trns[1][4:] + '/' + (path_trns[2][10:] if 'protpaths' in path_trns[2] else path_trns[2][6:]) + '/' + path.tDn.split('[')[1][:-1]
                        break
                
                for nic in nics[domain]:
                    if cep.mac == nic.mac:
                        if nic._model == 'compDNic':
                            nic_type += '<li>Discovered</li>'
                            comp += '<li> </li>'
                        elif nic._model == 'compMgmtNic':
                            nic_type += '<li>Management</li>'
                            nic_rns = nic.dn.split('/')
                            comp += '<li>' + nic_rns[1][5:] + '/' + nic_rns[2].split(']')[1][1:] + '/' + nic_rns[3][3:] + '/' + nic.tType + '</li>'
                        elif nic._model == 'compHpNic':
                            nic_type += '<li>Hypervisor</li>'
                            nic_rns = nic.dn.split('/')
                            comp += '<li>' + nic_rns[1][5:] + '/' + nic_rns[2].split(']')[1][1:] + '/' + nic_rns[3][3:] + '/' + nic_rns[4][6:] + '</li>'
                        elif nic._model == 'compPpNic':
                            nic_type += '<li>Pysical</li>'
                            comp += '<li> </li>'
                        elif nic._model == 'compVNic':
                            nic_type += '<li>Virtual</li>'
                            nic_rns = nic.dn.split('/')
                            comp += '<li>' + nic_rns[1][5:] + '/' + nic_rns[2].split(']')[1][1:] + '/' + nic_rns[3][3:] + ('/"%s"' % nic.name) + '</li>'
                
                nic_type += '</ul>'
                comp += '</ul>'
                
                eptable.add(mac, epg, ip, intf, encap, nic_type, comp)
            
            lo(Row(Panel(domain, eptable, icon='fa-table')))
                
        return lo

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
                ctr_rec[4] += '<ul style="margin:0px">'
                for prov in provs[domain]:
                    if rn in prov.dn:
                        trns = prov.tDn.split('/')
                        ctr_rec[4] += '<li><small>' + tenant + '/' + trns[2][3:] + '/' + trns[3][4:] + '</small></li>'
                ctr_rec[4] += '</ul>'
                ctr_rec[5] += '<ul style="margin:0px">'
                for cons in conss[domain]:
                    if rn in cons.dn:
                        trns = cons.tDn.split('/')
                        ctr_rec[5] += '<li><small>' + tenant + '/' + trns[2][3:] + '/' + trns[3][4:] + '</small></li>'
                ctr_rec[5] += '</ul>'
                ctr_table.add(*ctr_rec)
            lo(Row(Panel(domain, Layout(Row(ctr_table)), icon='fa-table')))
        
        return lo
