#-*- coding: utf-8 -*-
'''
Created on 2016. 7. 27.

@author: "comfact"
'''

import re
import time
from ciscowebkit.common import *
 
class Impl_Overview(Feature):
     
    def __init__(self):
        Feature.__init__(self, 10)
     
    def get(self, request, *cmd):
        if len(APIC) == 0: return InfoBlock('데이터 없음', '연결된 APIC이 없습니다. Setting 메뉴에서 APIC 연결을 추가하세요.')
        
        lo = Layout()
        
        try: cnt_nd, cnt_tnt, cnt_bd, cnt_epg, cnt_ep, cnt_flt, cnt_ctr, cnt_47d, cnt_47g, cnt_ft = APIC.getCntAll()
        except: return Error('getCntAll')
        cnt_size = [(Col.SMALL, 3), (Col.MIDIUM, 2), (Col.LARGE, 1)]
        
        health = APIC.monitor()
        
        lines = L()
        rows = L()
        for i in range(0, 12):
            row = L()
            for dn in health:
                if re.search('topology(/pod-\d)*$', dn):
                    if dn not in lines: lines << dn
                    row << health[dn][i]
            rows << row
        total_health = ChartistArea(*lines, height=350).grid(0, 100).ani()
        idx = 0
        for row in rows:
            total_health.add(health._tstamp[idx], *row); idx += 1
        
        lines = L()
        rows = L()
        for i in range(0, 12):
            row = L()
            for dn in health:
                if re.search('node-[\w\W]+$', dn):
                    if dn not in lines: lines << dn
                    row << health[dn][i]
            rows << row
        node_health = ChartistLine(*lines, height=150).grid(0, 100).ani()
        idx = 0
        for row in rows:
            node_health.add(health._tstamp[idx], *row); idx += 1
            
        node_health_cur = ChartistBar('Node', height=200).grid(0, 100)
        idx = 0
        for line in lines:
            node_health_cur.add(line, rows[-1][idx]); idx += 1
                
        lines = L()
        rows = L()
        for i in range(0, 12):
            row = L()
            for dn in health:
                if re.search('epg-[\w\W]+$', dn):
                    if dn not in lines: lines << dn
                    row << health[dn][i]
            rows << row
        epg_health = ChartistLine(*lines, height=200).grid(0, 100).ani()
        idx = 0
        for row in rows:
            epg_health.add(health._tstamp[idx], *row); idx += 1
        epg_health_cur = ChartistBar('EPG', height=200).grid(0, 100)
        idx = 0
        for line in lines:
            epg_health_cur.add(line, rows[-1][idx]); idx += 1
        
        for domain in APIC:
            lo(
                Row(Panel(domain.domain, Layout(
                    Row(
                        Col(JustGage(cnt_nd[domain.domain], 0, 1000, desc="Nodes", height=100), *cnt_size),
                        Col(JustGage(cnt_tnt[domain.domain], 0, 1000, desc="Tenants", height=100), *cnt_size),
                        Col(JustGage(cnt_bd[domain.domain], 0, 1000, desc="BDs", height=100), *cnt_size),
                        Col(JustGage(cnt_epg[domain.domain], 0, 1000, desc="EPGs", height=100), *cnt_size),
                        Col(JustGage(cnt_ep[domain.domain], 0, 1000, desc="EPs", height=100), *cnt_size),
                        Col(JustGage(cnt_flt[domain.domain], 0, 1000, desc="Filters", height=100), *cnt_size),
                        Col(JustGage(cnt_ctr[domain.domain], 0, 1000, desc="Contracts", height=100), *cnt_size),
                        Col(JustGage(cnt_47d[domain.domain], 0, 1000, desc="L4/7Devices", height=100), *cnt_size),
                        Col(JustGage(cnt_47g[domain.domain], 0, 1000, desc="L4/7Graphs", height=100), *cnt_size),
                        Col(Empty(), (Col.SMALL, 4), (Col.MIDIUM, 2), (Col.LARGE, 1)),
                        Col(Layout(
                            Row(
                                Col(Text(''), (Col.SMALL, 4)),
                                Col(JustGage(cnt_ft[domain.domain]['critical'], 0, 100, desc="Critical", height=50), (Col.SMALL, 4)),
                                Col(JustGage(cnt_ft[domain.domain]['major'], 0, 100, desc="Major", height=50), (Col.SMALL, 4))
                            ),
                            Row(
                                Col(Text(''), (Col.SMALL, 4)),
                                Col(JustGage(cnt_ft[domain.domain]['minor'], 0, 100, desc="Minor", height=50), (Col.SMALL, 4)),
                                Col(JustGage(cnt_ft[domain.domain]['warning'], 0, 100, desc="Warning", height=50), (Col.SMALL, 4))
                            )
                        ), (Col.SMALL, 5), (Col.MIDIUM, 4), (Col.LARGE, 3))
                    )
                )))
            )
            
        lo(
            Row(
                Col(Panel('TotalHealth', total_health), (Col.SMALL, 12), (Col.MIDIUM, 4), (Col.LARGE, 4)),
                Col(Panel('NodeHealth', Layout(
                    Row(node_health),
                    Row(node_health_cur)
                )), (Col.SMALL, 12), (Col.MIDIUM, 8), (Col.LARGE, 8))
            ),
            Row(Panel('EpgHealth', Layout(
                Row(
                    Col(epg_health, (Col.SMALL, 12), (Col.MIDIUM, 6), (Col.LARGE, 6)),
                    Col(epg_health_cur, (Col.SMALL, 12), (Col.MIDIUM, 6), (Col.LARGE, 6))
                )
            )))
        )

        return lo
