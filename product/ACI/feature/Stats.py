#-*- coding: utf-8 -*-
'''
Created on 2016. 8. 12.

@author: "comfact"
'''

from ciscowebkit.common import *

class Stats(Feature):
    
    def __init__(self): Feature.__init__(self, 0, 'fa-heartbeat')

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