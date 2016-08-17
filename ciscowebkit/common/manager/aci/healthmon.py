'''
Created on 2016. 8. 17.

@author: "comfact"
'''

from ciscowebkit.common.pygics import *
from ciscowebkit.common.manager.aci import acitoolkit as acitool

class HealthMon:
    
    class APIC_CONNECTION_FAILED(E):
        def __init__(self, apic): E.__init__(self, 'Connection Failed %s@%s:%s' % (apic.user, str(apic.ips), apic.pwd))
            
    def __init__(self, apic):
        self._apic = apic
        self._session = acitool.Session('https://%s' % apic.connected, apic.user, apic.pwd)
        resp = self._session.login()
        if not resp.ok:
            self._session.close()
            raise HealthMon.APIC.APIC_CONNECTION_FAILED(apic)
        
    def __del__(self):
        self._session.close()
        
    def __call__(self):
        topology = acitool.HealthScore.get_topology_health(self._session)
        tenant = acitool.HealthScore.get_tenant_health(self._session)
        return M(topology=topology, tenant=tenant)