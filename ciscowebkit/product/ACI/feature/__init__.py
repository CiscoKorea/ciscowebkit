FEATURE_ORDER = ['Show.APIC',
                 'Show.Switch',
                 'Show.EPG',
                 'Show.EP',
                 'Stats.INTF_Util',
                 'Stats.EPG_Util']

from ciscowebkit.common import Overview, Setting

class Impl_Overview(Overview):
    
    def __init__(self): Overview.__init__(self)
    
    def action(self, request):
        return 'Over View Page'
    
class Impl_Setting(Setting):
    
    def __init__(self): Setting.__init__(self)
    
    def action(self, request):
        return 'Setting Page'