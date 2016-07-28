#-*- coding: utf-8 -*-
'''
Created on 2016. 7. 27.

@author: "comfact"
'''

import time
from ciscowebkit.common import *
 
class Impl_Overview(Feature):
     
    def __init__(self):
        Feature.__init__(self, 10)
     
    def get(self, request, *cmd):
        if len(APIC) == 0: return InfoBlock('데이터 없음', '연결된 APIC이 없습니다. Setting 메뉴에서 APIC 연결을 추가하세요.')
        
        tstamp = time.time()
        lo = Layout()
        lo.addRow()
        
        #=======================================================================
        # Total Health
        #=======================================================================
        th_data = APIC.get_with_domain('fabricOverallHealthHist5min', '?order-by=fabricOverallHealthHist5min.index|desc&page=0&page-size=12')
        th_form = ChartistLine(*th_data._order).ani().grid(0, 100)
        for idx in range(0, 12):
            y = L()
            x = time.strftime("%H:%M", time.localtime(tstamp - (300 * (11 - idx))))
            for domain in th_data._order:
                pnt = len(th_data[domain]) - (12 - idx)
                if pnt >= 0: y << th_data[domain][pnt].healthAvg
                else: y << None
            th_form.add(x, *y)
        lo.addCol(Panel('ACI Total Health', th_form), scr=Layout.SMALL, size=4)
         
        #=======================================================================
        # Node Health
        #=======================================================================
        node_data = APIC.get_with_domain('fabricNodeHealthHist5min', '?order-by=fabricNodeHealthHist5min.index|desc,fabricNodeHealthHist5min.dn')
        ylabel = L()
        for domain in node_data._order:
            dom_node_data = node_data[domain]
            ncount = len(dom_node_data) / 12
            for n in range(0, ncount):
                rns = dom_node_data[n].dn.split('/')
                ylabel << domain + '/' + rns[1] + '/' + rns[2]
        node_form = ChartistLine(*ylabel).ani().grid(0, 100)
        for idx in range(0, 12):
            y = L()
            x = time.strftime("%H:%M", time.localtime(tstamp - (300 * (11 - idx))))
            for domain in node_data._order:
                dom_node_data = node_data[domain]
                ncount = len(dom_node_data) / 12
                for n in range(0, ncount):
                    try: y << dom_node_data[ncount * idx + n].healthAvg
                    except: y << None
            node_form.add(x, *y)
        lo.addCol(Panel('1Hr Node Health History', node_form), scr=Layout.SMALL, size=5)
        
        node_bar = ChartistVBar().grid(0, 100).stroke(5, 5)
        for domain in node_data._order:
            dom_node_data = node_data[domain]
            ncount = len(dom_node_data) / 12
            for n in range(1, ncount + 1):
                rns = dom_node_data[-n].dn.split('/')
                avg = dom_node_data[-n].healthAvg
                node_bar.add(domain + '/' + rns[1] + '/' + rns[2], avg)
        lo.addCol(Panel('Current Node Health', node_bar), scr=Layout.SMALL, size=3)
         
        #=======================================================================
        # EPG Health
        #=======================================================================
        epg_data = APIC.get_with_domain('healthInst', '?query-target-filter=wcard(healthInst.dn,"^uni/tn-.*/ap-.*/epg-")&order-by=healthInst.dn')
        epg_form = ChartistVBar().grid(0, 100)
        for domain in epg_data._order:
            dom_epg_data = epg_data[domain]
            for epg in dom_epg_data:
                rns = epg.dn.split('/')
                epg_form.add(domain + '/' + rns[1][3:] + '/' + rns[2][3:] + '/' + rns[3][4:], epg.cur)
        lo.addRow().addCol(Panel('EPG Health', epg_form))
         
        return lo