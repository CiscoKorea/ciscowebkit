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
        
        lo = Layout()
        
        cnt_tnt = APIC.getNoTenant()
        cnt_bd  = APIC.getNoBD()
        cnt_epg = APIC.getNoEPG()
        cnt_ep  = APIC.getNoEP()
        cnt_flt = APIC.getNoFilter()
        cnt_ctr = APIC.getNoContract()
        cnt_47d = APIC.getNoL47Device()
        cnt_47g = APIC.getNoL47Graph()
        cnt_nd  = APIC.getNoNode()
        cnt_ft  = APIC.getNoFault()
        cnt_size = [(Col.SMALL, 3), (Col.MIDIUM, 2), (Col.LARGE, 1)]
        
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
                Col(Panel('TotalHealth', APICSET.getTotalHealthHist(height=200)), (Col.SMALL, 4)),
                Col(Panel('NodeHealth', Layout(
                    Row(
                        Col(APICSET.getNodeHealthHist(height=200), (Col.SMALL, 7)),
                        Col(APICSET.getNodeHealthCurr(height=200), (Col.SMALL, 5))
                    )
                )), (Col.SMALL, 8))
            ),
            Row(Panel('EpgHealth', APICSET.getEpgHealthCurr(height=200)))
        )

        return lo
