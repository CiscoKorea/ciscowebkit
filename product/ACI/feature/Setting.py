#-*- coding: utf-8 -*-
'''
Created on 2016. 7. 27.

@author: "comfact"
'''

from ciscowebkit.common import *
 
class Setting(Feature):
    
    def __init__(self):
        Feature.__init__(self)
        
        form = Form('Connect')
        form.addText('domain', 'Domain', 'input unique domain name')
        form.addText('ips', 'IPs', 'x.x.x.x/y.y.y.y/z.z.z.z')
        form.addText('user', 'User', 'input admin name')
        form.addText('pwd', 'Password', 'input admin password')
        self.form_panel = Panel('Add Connection', form)
        
        self.info = None;
        
    def get(self, request, *cmd):
        lo = Layout()
        
        if self.info:
            lo.addRow().addCol(self.info)
            self.info = None;
        
        apic_table = Table('Domain', 'Address', 'User', 'Password', 'Connected')
        for apic in APIC:
            apic_table.add(apic.domain, apic.ip, apic.name, apic.pwd, apic.connected, did=apic.domain)
        
        lo.addRow().addCol(self.form_panel)
        lo.addRow().addCol(Panel('Connection List', apic_table))
        
        return lo
    
    def post(self, request, data, *cmd):
        apic = APIC.addDomain(data.domain, data.ips, data.user, data.pwd)
        if apic: self.info = InfoBlock('연결성공', '%s의 APIC과 %s로 연결되었습니다.' % (apic.domain, apic.connected)) 
        else: self.info = InfoBlock('연결실패', 'APIC 연결이 실패하였습니다. 연결정보를 확인하세요.')
        return self.get(request, *cmd)
    
    def delete(self, request, data, *cmd):
        APIC.delDomain(data)
        self.info = InfoBlock('연결삭제', '%s의 연결을 제거하였습니다/' % data)
        return self.get(request, *cmd)