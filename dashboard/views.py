from ciscowebkit.common import *

class Dashboard(Feature):
    
    def __init__(self): Feature.__init__(self, 10)
        
    def get(self, request, *cmd):
        lo = Layout()
        for pn in PRODUCTS._porder:
            if pn in PRODUCTS:
                prd = PRODUCTS[pn]
                fn = prd._forder[0]
                if instof(fn, tuple):
                    lo(Row(prd[fn[0]][fn[1]].get(request, *cmd)))
                else:
                    lo(Row(prd[fn].get(request, *cmd)))
        return lo
    