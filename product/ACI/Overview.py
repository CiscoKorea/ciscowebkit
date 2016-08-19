#!/usr/bin/env python
# -*- coding: utf-8 -*-
################################################################################
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
Created on 2016. 7. 27.

@author: "comfact"
'''

import re
import time
from ciscowebkit.common import *
from django.utils import translation
from django.utils.translation import ugettext_lazy as _
 
class Overview(Feature):
     
    def __init__(self):
        Feature.__init__(self, 10, 'fa-dashboard')
     
    def get(self, request, *cmd):
        
        #user_language = 'en'
        #translation.activate(user_language)
        
        msg1 = _('No Data')
        msg2 = _('There is no associated APIC. Add APIC connection in Setting menu.')
        
        MSG1 = msg1.encode("utf-8") 
        MSG2 = msg2.encode("utf-8")

        if len(ACI._order) == 0: return InfoBlock(MSG1,MSG2)
        lo = Layout()
        
        cnt_nd, cnt_tnt, cnt_bd, cnt_epg, cnt_ep, cnt_flt, cnt_ctr, cnt_47d, cnt_47g, cnt_f_cri, cnt_f_maj, cnt_f_min, cnt_f_war = ACI.getCount(('fabricNode', 'query-target-filter=ne(fabricNode.role,"controller")'),
                                                                                                                                                'fvTenant',
                                                                                                                                                'fvBD',
                                                                                                                                                'fvAEPg',
                                                                                                                                                'fvCEp',
                                                                                                                                                'vzFilter',
                                                                                                                                                'vzBrCP',
                                                                                                                                                'vnsCDev',
                                                                                                                                                'vnsGraphInst',
                                                                                                                                                ('faultInfo', 'query-target-filter=eq(faultInfo.severity,"critical")&rsp-subtree-include=count'),
                                                                                                                                                ('faultInfo', 'query-target-filter=eq(faultInfo.severity,"major")&rsp-subtree-include=count'),
                                                                                                                                                ('faultInfo', 'query-target-filter=eq(faultInfo.severity,"minor")&rsp-subtree-include=count'),
                                                                                                                                                ('faultInfo', 'query-target-filter=eq(faultInfo.severity,"warning")&rsp-subtree-include=count'))
        health = ACI.getHealthHist()
        
        #=======================================================================
        # Topology Health
        #=======================================================================
        
        total_lines = L()
        node_lines = L()
        total_rows = L()
        node_rows = L()
        node_rows_now = L()
        node_data_now = L()
        last_idx = ACI.mon_cnt - 1
        for domain in ACI._order:
            for i in range(0, ACI.mon_cnt):
                total_row = L(health._tstamp[i])
                node_row = L(health._tstamp[i])
                for dn in health[domain].topology:
                    if re.search('^pod-�d+$', dn):
                        if i == 0: total_lines << (domain + '/' + dn)
                        total_row << health[domain].topology[dn][i]
                    elif 'node-' in dn:
                        if i == 0: node_lines << (domain + '/' + dn)
                        elif i == last_idx: node_rows_now << health[domain].topology[dn][i]
                        node_row << health[domain].topology[dn][i]
                if i == 0: total_lines << (domain + '/total')
                total_row << health[domain].topology.total[i]
                total_rows << total_row
                node_rows << node_row
        total_health = ChartistArea(*total_lines, height=300).grid(0, 100).ani()
        for row in total_rows: total_health.add(*row)
        node_health = ChartistLine(*node_lines, height=150).grid(0, 100).ani()
        for row in node_rows: node_health.add(*row)
        node_health_now = ChartistBar(height=150).grid(0, 100)
        for i in range(0, len(node_lines)): node_data_now << (node_lines[i], node_rows_now[i])
        node_data_now = sorted(node_data_now, key=lambda node: node[1])
        node_data_now_len = len(node_data_now)
        for i in range(0, node_data_now_len if node_data_now_len < 20 else 20): node_health_now.add(node_data_now[i][0], node_data_now[i][1])
        
        #=======================================================================
        # EPG Health
        #=======================================================================
        
        lines = L()
        rows = L()
        rows_now = L()
        data_now = L()
        for domain in ACI._order:
            for i in range(0, ACI.mon_cnt):
                row = L(health._tstamp[i])
                for dn in health[domain].tenant:
                    if 'epg-' in dn:
                        if i == 0: lines << (domain + '/' + dn)
                        elif i == last_idx: rows_now << health[domain].tenant[dn][i]
                        row << health[domain].tenant[dn][i]
                rows << row
        epg_health = ChartistLine(*lines, height=200).grid(0, 100).ani()
        for row in rows: epg_health.add(*row)
        epg_health_now = ChartistBar(height=200).grid(0, 100)
        for i in range(0, len(lines)): data_now << (lines[i], rows_now[i])
        data_now = sorted(data_now, key=lambda node: node[1])
        data_now_len = len(data_now)
        for i in range(0, data_now_len if data_now_len < 20 else 20): epg_health_now.add(data_now[i][0], data_now[i][1])
        
        def resolution(data, res):
            div = data / res
            return data, res * div, res * (div + 1)
        
        cnt_size = [(Col.SMALL, 3), (Col.MIDIUM, 2), (Col.LARGE, 1)]
        for domain in ACI._order:
            lo(
                Row(Panel(domain, Layout(
                    Row(
                        Col(JustGage(*resolution(cnt_nd[domain], 100), desc="Nodes", height=100, link=(PRODUCTS.aci.show.device, None)), *cnt_size),
                        Col(JustGage(*resolution(cnt_tnt[domain], 100), desc="Tenants", height=100, link=(PRODUCTS.aci.show.tenant, None)), *cnt_size),
                        Col(JustGage(*resolution(cnt_bd[domain], 100), desc="BDs", height=100), *cnt_size),
                        Col(JustGage(*resolution(cnt_epg[domain], 100), desc="EPGs", height=100, link=(PRODUCTS.aci.show.epg, None)), *cnt_size),
                        Col(JustGage(*resolution(cnt_ep[domain], 100), desc="EPs", height=100, link=(PRODUCTS.aci.show.ep, None)), *cnt_size),
                        Col(JustGage(*resolution(cnt_flt[domain], 100), desc="Filters", height=100), *cnt_size),
                        Col(JustGage(*resolution(cnt_ctr[domain], 100), desc="Contracts", height=100, link=(PRODUCTS.aci.show.contract, None)), *cnt_size),
                        Col(JustGage(*resolution(cnt_47d[domain], 100), desc="L4/7Devices", height=100), *cnt_size),
                        Col(JustGage(*resolution(cnt_47g[domain], 100), desc="L4/7Graphs", height=100), *cnt_size),
                        Col(Empty(), (Col.SMALL, 4), (Col.MIDIUM, 2), (Col.LARGE, 1)),
                        Col(Layout(
                            Row(
                                Col(Text(''), (Col.SMALL, 4)),
                                Col(JustGage(*resolution(cnt_f_cri[domain], 100), desc="Critical", height=50, link=(PRODUCTS.aci.show.fault, None)), (Col.SMALL, 4)),
                                Col(JustGage(*resolution(cnt_f_maj[domain], 100), desc="Major", height=50, link=(PRODUCTS.aci.show.fault, None)), (Col.SMALL, 4))
                            ),
                            Row(
                                Col(Text(''), (Col.SMALL, 4)),
                                Col(JustGage(*resolution(cnt_f_min[domain], 100), desc="Minor", height=50, link=(PRODUCTS.aci.show.fault, None)), (Col.SMALL, 4)),
                                Col(JustGage(*resolution(cnt_f_war[domain], 100), desc="Warning", height=50, link=(PRODUCTS.aci.show.fault, None)), (Col.SMALL, 4))
                            )
                        ), (Col.SMALL, 5), (Col.MIDIUM, 4), (Col.LARGE, 3))
                    )
                ), icon='fa-retweet'))
            )
            
        lo(
            Row(
                Col(Panel('Total Health', total_health, icon='fa-retweet'), (Col.SMALL, 12), (Col.MIDIUM, 4), (Col.LARGE, 4)),
                Col(Panel('Node Health', Layout(
                    Row(node_health),
                    Row(node_health_now)
                ), icon='fa-retweet'), (Col.SMALL, 12), (Col.MIDIUM, 8), (Col.LARGE, 8))
            ),
            Row(Panel('EPG Health', Layout(
                Row(
                    Col(epg_health, (Col.SMALL, 12), (Col.MIDIUM, 4), (Col.LARGE, 4)),
                    Col(epg_health_now, (Col.SMALL, 12), (Col.MIDIUM, 8), (Col.LARGE, 8))
                )
            ), icon='fa-retweet'))
        )

        return lo
