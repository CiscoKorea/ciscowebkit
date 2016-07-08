from ciscowebkit.common.pygics import SingleTon

ICON_DASHBOARD = 'fa fa-fw fa-dashboard'
ICON_CHART = 'fa fa-fw fa-bar-chart-o'
ICON_TABLE = 'fa fa-fw fa-table'
ICON_EDIT = 'fa fa-fw fa-edit'
ICON_DESKTOP = 'fa fa-fw fa-desktop'
ICON_SETTING = 'fa fa-fw fa-wrench'
ICON_UPDOWN = 'fa fa-fw fa-arrows-v'
ICON_DROPDOWN = 'fa fa-fw fa-caret-down'
ICON_FILE = 'fa fa-fw fa-file'
ICON_MAIL = 'fa fa-envelope'
ICON_BELL = 'fa fa-bell'
ICON_USER = 'fa fa-user'

class Feature(SingleTon):
    
    ICON = ICON_FILE
    
    def __init__(self, **kargs): pass
    
    def action(self, request):
        return 'Not Implemented'

class __Default_Feature__(SingleTon):
    
    def __init__(self, **kargs): pass

    def action(self, request):
        return 'Not Implemented'

class Overview(__Default_Feature__):
    
    ICON = ICON_DASHBOARD
    
    def __init__(self, **kargs): __Default_Feature__.__init__(self, **kargs)
    
class Setting(__Default_Feature__):
    
    ICON = ICON_SETTING
    
    def __init__(self, **kargs): __Default_Feature__.__init__(self, **kargs)
    
