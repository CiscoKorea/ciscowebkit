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
Created on 2016. 7. 5.

@author: "comfact"
'''

from ciscowebkit.common import *
from django.utils.translation import ugettext_lazy as _

class Show(Feature):
    
    def __init__(self): Feature.__init__(self, 0, 'fa-eye')

class Device(SubFeature):
    
    '''Devices Information'''
    
    def __init__(self): SubFeature.__init__(self, icon='fa-cogs')
    
    def get(self, request, *cmd):

        if len(ACI._order) == 0:
            return InfoBlock(LC('No Data'), LC('There is no associated APIC. Add APIC connection in Setting menu.'))
        
        lo = Layout()
        
        node_data, cfrm_data, sfrm_data, tsys_data = ACI.get(
                                                             ('fabricNode', 'order-by=fabricNode.role,fabricNode.name'),
                                                             'firmwareCtrlrRunning',
                                                             'firmwareRunning',
                                                             'topSystem'
                                                              )
        
        for domain in ACI._order:
            ctrl = Table('ID', 'Name', 'Model', 'Serial', 'Version', 'INB Mgmt IP', 'OOB Mgmt IP', 'State', 'Uptime', title='Controller')
            spne = Table('ID', 'Name', 'Model', 'Serial', 'Version', 'INB Mgmt IP', 'OOB Mgmt IP', 'State', 'Uptime', title='Spine')
            leaf = Table('ID', 'Name', 'Model', 'Serial', 'Version', 'INB Mgmt IP', 'OOB Mgmt IP', 'State', 'Uptime', title='Leaf')
            
            cnt_ctrl = 0
            cnt_spne = 0
            cnt_leaf = 0
            
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
                    cnt_ctrl += 1
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
                    cnt_spne += 1
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
                    cnt_leaf += 1
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
            lo(
                Row(Panel(domain, Layout(
                    Row(
                        Col(InfoPanel('Controller', cnt_ctrl, panel=Panel.BLUE, icon='fa-map-signs'), (Col.SMALL, 4), (Col.MIDIUM, 4), (Col.LARGE, 4)),
                        Col(InfoPanel('Spine', cnt_spne, panel=Panel.BLUE, icon='fa-tree'), (Col.SMALL, 4), (Col.MIDIUM, 4), (Col.LARGE, 4)),
                        Col(InfoPanel('Leaf', cnt_leaf, panel=Panel.BLUE, icon='fa-leaf'), (Col.SMALL, 4), (Col.MIDIUM, 4), (Col.LARGE, 4))
                    ),
                    Row(ctrl),
                    Row(spne),
                    Row(leaf)
                ), icon='fa-table'))
            )
            
        return lo
    
class Tenant(SubFeature):
    
    '''Tenants Informantion'''
    
    def __init__(self): SubFeature.__init__(self, icon='fa-users')
    
    def get(self, request, *cmd):
        
        if len(ACI._order) == 0:
            return InfoBlock(LC('No Data'), LC('There is no associated APIC. Add APIC connection in Setting menu.'))
        
        tns, eps, bds, ctxs, ctrs, flts, epgs = ACI.get(
                                                        ('fvTenant', 'rsp-prop-include=naming-only'),
                                                        ('fvTenant', 'query-target=subtree&target-subtree-class=fvCEp&rsp-prop-include=naming-only'),
                                                        ('fvTenant', 'query-target=subtree&target-subtree-class=fvBD&rsp-prop-include=naming-only'),
                                                        ('fvTenant', 'query-target=subtree&target-subtree-class=fvCtx&rsp-prop-include=naming-only'),
                                                        ('fvTenant', 'query-target=subtree&target-subtree-class=vzBrCP&rsp-prop-include=naming-only'),
                                                        ('fvTenant', 'query-target=subtree&target-subtree-class=vzFilter&rsp-prop-include=naming-only'),
                                                        ('fvTenant', 'query-target=subtree&target-subtree-class=fvAEPg&rsp-prop-include=naming-only'),
                                                        )
        
        tn_table = Table('Domain', 'Name', 'EPG', 'EP', 'Bridge Domain', 'Context', 'Contract', 'Filter')
        tn_cnt = 0
        
        for domain in ACI._order:
            
            for tn in tns[domain]:
                tn_cnt += 1
                name = tn.name
                bd_data = '<ul style="padding-left:10px">'
                ctx_data = '<ul style="padding-left:10px">'
                ctr_data = '<ul style="padding-left:10px">'
                flt_data = '<ul style="padding-left:10px">'
                ep_data = '<ul style="padding-left:10px">'
                epg_data = '<ul style="padding-left:10px">'
                
                
                for bd in bds[domain]:
                    if tn.dn in bd.dn: bd_data += '<li><small>' + bd.name + '</small></li>'
                
                for ctx in ctxs[domain]:
                    if tn.dn in ctx.dn: ctx_data += '<li><small>' + ctx.name + '</small></li>'
                    
                for ctr in ctrs[domain]:
                    if tn.dn in ctr.dn: ctr_data += '<li><small>' + ctr.name + '</small></li>'
                    
                for flt in flts[domain]:
                    if tn.dn in flt.dn: flt_data += '<li><small>' + flt.name + '</small></li>'
                    
                for epg in epgs[domain]:
                    if tn.dn in epg.dn: epg_data += '<li><small>' + epg.name + '</small></li>'
                    
                for ep in eps[domain]:
                    if tn.dn in ep.dn: ep_data += '<li><small>' + ep.name + '</small></li>'
                    
                bd_data += '</ul>'
                ctx_data += '</ul>'
                ctr_data += '</ul>'
                flt_data += '</ul>'
                ep_data += '</ul>'
                epg_data += '</ul>'
                
                tn_table.add(domain, name, epg_data, ep_data, bd_data, ctx_data, ctr_data, flt_data)
        
        return Layout(
            Row(InfoPanel('Tenants', tn_cnt, panel=Panel.BLUE, icon='fa-users')),
            Row(Plain(tn_table))
        )
    
class EPG(SubFeature):
    
    '''End-Point Groups Informantion'''
    
    def __init__(self): SubFeature.__init__(self, icon='fa-object-group')
    
    def get(self, request, *cmd):
        
        if len(ACI._order) == 0:
            return InfoBlock(LC('No Data'), LC('There is no associated APIC. Add APIC connection in Setting menu.'))
        
        epgs, ctxs, bds, provs, conss, paths = ACI.get(
                                                       ('fvAEPg', 'order-by=fvAEPg.dn'),
                                                       'fvCtx',
                                                       'fvBD',
                                                       'vzRtProv',
                                                       'vzRtCons',
                                                       'fvRsPathAtt'
                                                       )
        
        eg_table = Table('Domain', 'EPG', 'Tenant', 'App Profile', 'Bridge Domain', 'Context', 'Provided Contract', 'Consumed Contract', 'Binding Path', 'Encap')
        eg_cnt = 0
        
        for domain in ACI._order:
            
            for epg in epgs[domain]:
                eg_cnt += 1
                rns = epg.dn.split('/')
                name = epg.name
                tenant = rns[1][3:]
                app = rns[2][3:]
                bd_data = ''
                ctx_data = ''
                provided = '<ul style="padding-left:10px">'
                consumed = '<ul style="padding-left:10px">'
                binding = '<ul style="padding-left:10px">'
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
                        provided += '<li><small>' + prov.dn.split('/')[2][4:] + '</small></li>'
                
                for cons in conss[domain]:
                    if epg.dn == cons.tDn:
                        consumed += '<li><small>' + cons.dn.split('/')[2][4:] + '</small></li>'
                
                for path in paths[domain]:
                    if epg.dn in path.dn:
                        trns = path.tDn.split('/')
                        binding += '<li><small>' + trns[1][4:] + '/' + (trns[2][10:] if 'protpaths' in trns[2] else trns[2][6:]) + '/' + path.tDn.split('[')[1][:-1] + '</small></li>'
                        if encap == ' ': encap = path.encap
                        
                provided += '</ul>'
                consumed += '</ul>'
                binding += '</ul>'
                
                eg_table.add(domain, name, tenant, app, bd_data, ctx_data, provided, consumed, binding, encap)
                
        return Layout(
            Row(InfoPanel('End-Point Groups', eg_cnt, panel=Panel.BLUE, icon='fa-object-group')),
            Row(Plain(eg_table))
        )
    
class EP(SubFeature):
    
    '''End-Point Informantion'''
    
    def __init__(self): SubFeature.__init__(self, icon='fa-plug')
    
    def get(self, request, *cmd):
        
        if len(ACI._order) == 0:
            return InfoBlock(LC('No Data'), LC('There is no associated APIC. Add APIC connection in Setting menu.'))
        
        ceps, paths, nics = ACI.get(
                                    ('fvCEp', 'order-by=fvCEp.dn'),
                                    'fvRsCEpToPathEp',
                                    'compNic'
                                    )
        
        ep_table = Table('Domain', 'Mac', 'EPG', 'IP', 'Interface', 'Encap', 'Nic Type', 'Computing')
        ep_cnt = 0
        dnic_cnt = 0
        mgmt_cnt = 0
        hnic_cnt = 0
        pnic_cnt = 0
        vnic_cnt = 0
        
        for domain in ACI._order:
            
            for cep in ceps[domain]:
                ep_cnt += 1
                rns = cep.dn.split('/')
                epg = rns[1][3:] + '/' + rns[2][3:] + '/' + rns[3][4:]
                mac = cep.mac
                ip = cep.ip
                intf = None
                encap = cep.encap
                nic_type = '<ul style="padding-left:10px">'
                comp = '<ul style="padding-left:10px">'
                
                for path in paths[domain]:
                    if cep.dn in path.dn:
                        path_trns = path.tDn.split('/')
                        intf = path_trns[1][4:] + '/' + (path_trns[2][10:] if 'protpaths' in path_trns[2] else path_trns[2][6:]) + '/' + path.tDn.split('[')[1][:-1]
                        break
                    
                for nic in nics[domain]:
                    if cep.mac == nic.mac:
                        if nic._model == 'compDNic':
                            nic_type += '<li><small>Discovered</small></li>'
                            comp += '<li> </li>'
                            dnic_cnt += 1
                        elif nic._model == 'compMgmtNic':
                            nic_type += '<li><small>Management</small></li>'
                            nic_rns = nic.dn.split('/')
                            comp += '<li><small>' + nic_rns[1][5:] + '/' + nic_rns[2].split(']')[1][1:] + '/' + nic_rns[3][3:] + '/' + nic.tType + '</small></li>'
                            mgmt_cnt += 1
                        elif nic._model == 'compHpNic':
                            nic_type += '<li><small>Hypervisor</small></li>'
                            nic_rns = nic.dn.split('/')
                            comp += '<li><small>' + nic_rns[1][5:] + '/' + nic_rns[2].split(']')[1][1:] + '/' + nic_rns[3][3:] + '/' + nic_rns[4][6:] + '</small></li>'
                            hnic_cnt += 1
                        elif nic._model == 'compPpNic':
                            nic_type += '<li><small>Pysical</small></li>'
                            comp += '<li> </li>'
                            pnic_cnt += 1
                        elif nic._model == 'compVNic':
                            nic_type += '<li><small>Virtual</small></li>'
                            nic_rns = nic.dn.split('/')
                            comp += '<li><small>' + nic_rns[1][5:] + '/' + nic_rns[2].split(']')[1][1:] + '/' + nic_rns[3][3:] + ('/"%s"' % nic.name) + '</small></li>'
                            vnic_cnt += 1
                
                nic_type += '</ul>'
                comp += '</ul>'
                
                ep_table.add(domain, mac, epg, ip, intf, encap, nic_type, comp)
        
        return Layout(
            Row(
                Col(InfoPanel('EP', ep_cnt, panel=Panel.BLUE, icon='fa-plug'), (Col.SMALL, 2), (Col.MIDIUM, 2), (Col.LARGE, 2)),
                Col(InfoPanel('Discovered', dnic_cnt, panel=Panel.BLUE, icon='fa-flag-checkered'), (Col.SMALL, 2), (Col.MIDIUM, 2), (Col.LARGE, 2)),
                Col(InfoPanel('Management', mgmt_cnt, panel=Panel.BLUE, icon='fa-cog'), (Col.SMALL, 2), (Col.MIDIUM, 2), (Col.LARGE, 2)),
                Col(InfoPanel('Physical', pnic_cnt, panel=Panel.BLUE, icon='fa-server'), (Col.SMALL, 2), (Col.MIDIUM, 2), (Col.LARGE, 2)),
                Col(InfoPanel('Hypervisor', hnic_cnt, panel=Panel.BLUE, icon='fa-cubes'), (Col.SMALL, 2), (Col.MIDIUM, 2), (Col.LARGE, 2)),
                Col(InfoPanel('Virtual', vnic_cnt, panel=Panel.BLUE, icon='fa-cube'), (Col.SMALL, 2), (Col.MIDIUM, 2), (Col.LARGE, 2))
            ),
            Row(Plain(ep_table))
        )

class Contract(SubFeature):
    
    '''Contracts Information'''
    
    def __init__(self): SubFeature.__init__(self, icon='fa-ticket')
    
    def get(self, request, *cmd):
        
        if len(ACI._order) == 0:
            return InfoBlock(LC('No Data'), LC('There is no associated APIC. Add APIC connection in Setting menu.'))
        
        cps, subjs, conss, provs = ACI.get(
                                           ('vzBrCP', 'order-by=vzBrCP.modTs'),
                                           'vzSubj',
                                           'vzRtCons',
                                           'vzRtProv'
                                           )
        
        ctr_table = Table('Domain', 'Name', 'Tenant', 'Scope', 'Subject', 'Provider', 'Consumer')
        ctr_cnt = 0
        prv_cnt = 0
        con_cnt = 0
        
        for domain in ACI._order:
            
            for cp in cps[domain]:
                ctr_cnt += 1
                rns = cp.dn.split('/')
                rn = rns[2]
                tenant = rns[1][3:]
                
                ctr_name = cp.name
                ctr_tnt = tenant
                ctr_scope = cp.scope
                ctr_subj = ' '
                ctr_prov = '<ul style="padding-left:10px">'
                ctr_cons = '<ul style="padding-left:10px">'
                
                for subj in subjs[domain]:
                    if rn in subj.dn:
                        ctr_subj = subj.name

                for prov in provs[domain]:
                    if rn in prov.dn:
                        trns = prov.tDn.split('/')
                        ctr_prov += '<li><small>' + tenant + '/' + trns[2][3:] + '/' + trns[3][4:] + '</small></li>'
                        prv_cnt += 1
                ctr_prov += '</ul>'
                
                for cons in conss[domain]:
                    if rn in cons.dn:
                        trns = cons.tDn.split('/')
                        ctr_cons += '<li><small>' + tenant + '/' + trns[2][3:] + '/' + trns[3][4:] + '</small></li>'
                        con_cnt += 1
                ctr_cons += '</ul>'
                
                ctr_table.add(domain, ctr_name, ctr_tnt, ctr_scope, ctr_subj, ctr_prov, ctr_cons)
        
        return Layout(
            Row(
                Col(InfoPanel('Contracts', ctr_cnt, panel=Panel.BLUE, icon='fa-ticket'), (Col.SMALL, 4), (Col.MIDIUM, 4), (Col.LARGE, 4)),
                Col(InfoPanel('Provider', prv_cnt, panel=Panel.BLUE, icon='fa-truck'), (Col.SMALL, 4), (Col.MIDIUM, 4), (Col.LARGE, 4)),
                Col(InfoPanel('Consumer', con_cnt, panel=Panel.BLUE, icon='fa-shopping-cart'), (Col.SMALL, 4), (Col.MIDIUM, 4), (Col.LARGE, 4))
            ),
            Row(Plain(ctr_table))
        )

class L3_External(SubFeature):
    
    '''L3 External Network Information'''
    
    def __init__(self): SubFeature.__init__(self, icon='fa-cloud')
    
    def get(self, request, *cmd):
        
        if len(ACI._order) == 0:
            return InfoBlock(LC('No Data'), LC('There is no associated APIC. Add APIC connection in Setting menu.'))
        
        insps, isubs, ctxs, provs, conss = ACI.get(
                                                   'l3extInstP',
                                                   'l3extSubnet',
                                                   'fvCtx',
                                                   ('fvRsProv', 'query-target-filter=wcard(fvRsProv.dn,"/out-")'),
                                                   ('fvRsCons', 'query-target-filter=wcard(fvRsCons.dn,"/out-")')
                                                   )
        
        l3_table = Table('Domain', 'L3 External', 'Tenant', 'Context', 'L3 Outside', 'Subnets', 'Provided Contract', 'Consumed Contract')
        l3_cnt = 0
        
        for domain in ACI._order:
            
            for insp in insps[domain]:
                l3_cnt += 1
                rns = insp.dn.split('/')
                name = insp.name
                tenant = rns[1][3:]
                context = ' '
                l3_out = rns[2][4:]
                subnet = '<ul style="padding-left:10px">'
                provided = '<ul style="padding-left:10px">'
                consumed = '<ul style="padding-left:10px">'
                
                for ctx in ctxs[domain]:
                    if insp.scope == ctx.scope:
                        context = ctx.name
                        break
                    
                for isub in isubs[domain]:
                    if insp.dn in isub.dn:
                        subnet += '<li><small>%s</small></li>' % isub.ip
                
                for prov in provs[domain]:
                    if insp.dn in prov.dn:
                        provided += '<li><small>%s</small></li>' % prov.tDn.split('/brc-')[1]
                
                for cons in conss[domain]:
                    if insp.dn in cons.dn:
                        consumed += '<li><small>%s</small></li>' % cons.tDn.split('/brc-')[1]
                        
                subnet += '</ul>'
                provided += '</ul>'
                consumed += '</ul>'
                
                l3_table.add(domain, name, tenant, context, l3_out, subnet, provided, consumed)
                
        return Layout(
            Row(InfoPanel('L3 External', l3_cnt, panel=Panel.BLUE, icon='fa-cloud')),
            Row(Plain(l3_table))
        )

class Fault(SubFeature):
    
    '''Faults Information'''
    
    def __init__(self): SubFeature.__init__(self, icon='fa-warning')
    
    def get(self, request, *cmd):
        
        if len(ACI._order) == 0:
            return InfoBlock(LC('No Data'), LC('There is no associated APIC. Add APIC connection in Setting menu.'))
        
        cris, majs, mins, wars = ACI.get(
                                         ('faultInfo', 'query-target-filter=eq(faultInfo.severity, "critical")&order-by=faultInfo.created|desc'),
                                         ('faultInfo', 'query-target-filter=eq(faultInfo.severity, "major")&order-by=faultInfo.created|desc'),
                                         ('faultInfo', 'query-target-filter=eq(faultInfo.severity, "minor")&order-by=faultInfo.created|desc'),
                                         ('faultInfo', 'query-target-filter=eq(faultInfo.severity, "warning")&order-by=faultInfo.created|desc')
                                         )
        
        ft_table = Table('Type', 'Domain', 'Subject', 'Time Stamp', 'Object', 'Status', 'Description', 'Code')
        cri_cnt = 0
        maj_cnt = 0
        min_cnt = 0
        war_cnt = 0
        
        for domain in ACI._order:
            
            for cri in cris[domain]:
                tstamp = cri.created.split('T')
                ft_table.add('Critical', domain, cri.subject.upper(), tstamp[0] + ' ' + tstamp[1][:8], cri.dn.split('/fault-')[0], cri.lc, cri.descr, cri.code, type=Table.DANGER)
                cri_cnt += 1
        
            for maj in majs[domain]:
                tstamp = maj.created.split('T')
                ft_table.add('Major', domain, maj.subject.upper(), tstamp[0] + ' ' + tstamp[1][:8], maj.dn.split('/fault-')[0], maj.lc, maj.descr, maj.code, type=Table.DANGER)
                maj_cnt += 1
                
            for min in mins[domain]:
                tstamp = min.created.split('T')
                ft_table.add('Minor', domain, min.subject.upper(), tstamp[0] + ' ' + tstamp[1][:8], min.dn.split('/fault-')[0], min.lc, min.descr, min.code, type=Table.WARNING)
                min_cnt += 1
                
            for war in wars[domain]:
                tstamp = war.created.split('T')
                ft_table.add('Warning', domain, war.subject.upper(), tstamp[0] + ' ' + tstamp[1][:8], war.dn.split('/fault-')[0], war.lc, war.descr, war.code, type=Table.WARNING)
                war_cnt += 1
        
        return Layout(
            Row(
                Col(InfoPanel('CRITICAL', cri_cnt, panel=Panel.RED, icon='fa-bolt'), (Col.SMALL, 3), (Col.MIDIUM, 3), (Col.LARGE, 3)),
                Col(InfoPanel('MAJOR', maj_cnt, panel=Panel.DANGER, icon='fa-exclamation-triangle'), (Col.SMALL, 3), (Col.MIDIUM, 3), (Col.LARGE, 3)),
                Col(InfoPanel('MINOR', min_cnt, panel=Panel.YELLOW, icon='fa-exclamation-circle'), (Col.SMALL, 3), (Col.MIDIUM, 3), (Col.LARGE, 3)),
                Col(InfoPanel('WARNING', war_cnt, panel=Panel.WARNING, icon='fa-exclamation'), (Col.SMALL, 3), (Col.MIDIUM, 3), (Col.LARGE, 3))
            ),
            Row(Plain(ft_table))
        )
