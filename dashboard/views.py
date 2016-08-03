from ciscowebkit.common import *

class Dashboard(Feature):
    
    def __init__(self):
        Feature.__init__(self)
        
    def get(self, request, *cmd):
        return Text("Dashboard")
    