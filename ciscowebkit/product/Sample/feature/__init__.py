FEATURE_ORDER = [
                 'ChartTest',
                 'Feature1',
                 'Feature2.Object_1',
                 'Feature2.Object_2',
                 'Feature3',
                 'Feature4.Object_1',
                 'Feature4.Object_2',
                ]

from ciscowebkit.common import Overview, Setting

class Impl_Overview(Overview):
    
    def __init__(self): Overview.__init__(self)
    
    def get(self, request):
        return 'Over View Page'
    
class Impl_Setting(Setting):
    
    def __init__(self): Setting.__init__(self)
    
    def get(self, request):
        return 'Setting Page'