from ciscowebkit.common.pygics import SingleTon

# http://fontawesome.io/icons/

class FeatureInterface(SingleTon):
    
    def __init__(self, icon=None, **kargs):
        if icon: self._icon_ = icon
        else: self._icon_ = 'fa-file'
    
    def get(self, request):
        return 'Not Implemented'
    
    def post(self, request):
        return 'Not Implemented'
    
    def update(self, request):
        return 'Not Implemented'
    
    def delete(self, request):
        return 'Not Implemented'

class Feature(FeatureInterface):
    
    def __init__(self, icon=None, **kargs):
        FeatureInterface.__init__(self, icon, **kargs)
        
class SubFeature(Feature):
    
    def __init__(self, icon=None, **kargs):
        Feature.__init__(self, icon, **kargs)

class Overview(FeatureInterface):
    
    def __init__(self, **kargs):
        FeatureInterface.__init__(self, 'fa-newspaper-o', **kargs)
    
class Setting(FeatureInterface):
    
    def __init__(self, **kargs):
        FeatureInterface.__init__(self, 'fa-wrench', **kargs)
    
