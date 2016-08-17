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
Created on 2016. 8. 12.

@author: "comfact"
'''

from ciscowebkit.common import *

class Stats(Feature):
    
    def __init__(self): Feature.__init__(self, 0, 'fa-heartbeat')
    
class Interface_Utilization(SubFeature):
    
    '''Statistics of Interface Utilization'''
    
    def __init__(self): SubFeature.__init__(self, 10, 'fa-plug')
    
    def get(self, request, *cmd):
        if len(ACI._order) == 0: return InfoBlock('데이터 없음', '연결된 APIC이 없습니다. Setting 메뉴에서 APIC 연결을 추가하세요.')
        
        lo = Layout()
        
        ingrs, egrs, phyis = ACI.get(('eqptIngrTotalHist5min', 'query-target-filter=wcard(eqptIngrTotalHist5min.dn,"sys/phys-.*/HDeqptIngrTotal5min-0")'),
                                     ('eqptEgrTotalHist5min', 'query-target-filter=wcard(eqptEgrTotalHist5min.dn,"sys/phys-.*/HDeqptEgrTotal5min-0")'),
                                     'l1PhysIf')
        
        for domain in ACI._order:
            ingr_donut = MorrisDonut(height=300, title='Input')
            egr_donut = MorrisDonut(height=300, title='Output')
            ingr_dcnt = 0
            egr_dcnt = 0
            total_ingr = 0.00
            total_egr = 0.00
            start = ingrs[domain][0].repIntvStart[11:-13]
            end = ingrs[domain][0].repIntvEnd[11:-13]
            table = Table('Interface', 'Type', 'Admin State', 'Speed', 'Input Rate(pps)', 'Input Util(%)', 'Output Rate(pps)', 'Output Util(%)')
            
            for phyi in phyis[domain]:
                raw_rns = phyi.dn.split('[')
                rns = raw_rns[0].split('/')
                iname = rns[1] + '/' + rns[2] + '/' + raw_rns[1][:-1]
                itype = phyi.portT
                istat = phyi.adminSt
                ispeed = phyi.speed
                irate = 0.00
                iutil = 0.0
                orate = 0.00
                outil = 0.0
                
                for ingr in ingrs[domain]:
                    if phyi.dn in ingr.dn:
                        irate = round(float(ingr.pktsRateAvg), 2)
                        iutil = round(float(ingr.utilAvg), 1)
                        break
                
                for egr in egrs[domain]:
                    if phyi.dn in egr.dn:
                        orate = round(float(egr.pktsRateAvg), 2)
                        outil = round(float(egr.utilAvg), 1)
                        break
                
                table.add(iname, itype, istat, ispeed, str(irate), str(iutil), str(orate), str(outil))
                if irate > 0.0: ingr_donut.add(iname, irate); ingr_dcnt += 1; total_ingr += irate
                if orate > 0.0: egr_donut.add(iname, orate); egr_dcnt += 1; total_egr += orate
                if ingr_dcnt == 0: ingr_donut.add('Non-Communicate', 0)
                if egr_dcnt == 0: egr_donut.add('Non-Communicate', 0)
                
            lo(
                Row(Panel(domain, Layout(
                    Row(
                        Col(InfoPanel('Start', start, panel=Panel.BLUE, icon='fa-hourglass-start'), (Col.SMALL, 6), (Col.MIDIUM, 6), (Col.LARGE, 6)),
                        Col(InfoPanel('End', end, panel=Panel.BLUE, icon='fa-hourglass-end'), (Col.SMALL, 6), (Col.MIDIUM, 6), (Col.LARGE, 6))
                    ),
                    Row(InfoPanel('Total Input', str(round(total_ingr, 2)) + ' pps', panel=Panel.BLUE, icon='fa-compress')),
                    Row(InfoPanel('Total Output', str(round(total_egr, 2)) + ' pps', panel=Panel.BLUE, icon='fa-expand')),
                    Row(
                        Col(ingr_donut, (Col.SMALL, 6), (Col.MIDIUM, 6), (Col.LARGE, 6)),
                        Col(egr_donut, (Col.SMALL, 6), (Col.MIDIUM, 6), (Col.LARGE, 6))
                    ),
                    Row(table)
                ), icon='fa-table'))
            )
        
        return lo
    

class EPG_Utilization(SubFeature):
    
    '''Statistics of EPG Utilization'''
    
    def __init__(self): SubFeature.__init__(self, 10, 'fa-object-group')
    
    def get(self, request, *cmd):
        if len(ACI._order) == 0: return InfoBlock('데이터 없음', '연결된 APIC이 없습니다. Setting 메뉴에서 APIC 연결을 추가하세요.')
        
        lo = Layout()
        
        bytes, pkts = ACI.get(('l2IngrBytesAgHist15min', 'query-target-filter=wcard(l2IngrBytesAg15min.dn,"uni/tn-.*/ap-.*/epg-.*/HDl2IngrBytesAg15min-0")'),
                              ('l2IngrPktsAgHist15min', 'query-target-filter=wcard(l2IngrPktsAg15min.dn,"uni/tn-.*/ap-.*/epg-.*/HDl2IngrPktsAg15min-0")'))
        
        for domain in ACI._order:
            donut = MorrisDonut(height=300)
            donut_cnt = 0
            table = Table('EPG', 'Unicast Bytes', 'Unicast Packets', 'Multicast Bytes', 'Multicast Packets')
            start = bytes[domain][0].repIntvStart[11:-13]
            end = bytes[domain][0].repIntvEnd[11:-13]
            tub = 0.00
            tmb = 0.00
            
            for byte in bytes[domain]:
                rns = byte.dn.split('/')
                tdn = byte.dn.split('/CDl2Ingr')[0]
                epg = rns[1][3:] + '/' + rns[2][3:] + '/' + rns[3][4:]
                ub = round(float(byte.unicastRate), 2)
                mb = round(float(byte.multicastRate), 2)
                up = 0.00
                mp = 0.00
                for pkt in pkts[domain]:
                    if tdn in pkt.dn:
                        up = round(float(pkt.unicastRate), 2)
                        mp = round(float(pkt.multicastRate), 2)
                        break
                if ub > 0.0: donut.add(epg + '/Unicast', ub); donut_cnt += 1
                if mb > 0.0: donut.add(epg + '/Multicast', mb); donut_cnt += 1
                tub += ub
                tmb += mb
                table.add(epg, str(ub), str(up), str(mb), str(mp))
            
            if donut_cnt == 0: donut.add('Non-Communicate', 0)
            
            lo(
                Row(Panel(domain, Layout(
                    Row(
                        Col(Layout(
                            Row(
                                Col(InfoPanel('Start', start, panel=Panel.BLUE, icon='fa-hourglass-start'), (Col.SMALL, 6), (Col.MIDIUM, 6), (Col.LARGE, 6)),
                                Col(InfoPanel('End', end, panel=Panel.BLUE, icon='fa-hourglass-end'), (Col.SMALL, 6), (Col.MIDIUM, 6), (Col.LARGE, 6))
                            ),
                            Row(InfoPanel('Total Unicast', str(round(tub, 2)) + ' Bytes', panel=Panel.BLUE, icon='fa-arrow-circle-o-right')),
                            Row(InfoPanel('Total Multicast', str(round(tmb, 2)) + ' Bytes', panel=Panel.BLUE, icon='fa-share-alt'))
                        ), (Col.SMALL, 6), (Col.MIDIUM, 6), (Col.LARGE, 6)),
                        Col(donut, (Col.SMALL, 6), (Col.MIDIUM, 6), (Col.LARGE, 6))
                    ),
                    Row(table)
                ), icon='fa-table'))
            )
        
        return lo