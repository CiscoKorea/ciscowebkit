'''
Created on 2016. 7. 15.

@author: "comfact"
'''

from ciscowebkit.common.pygics import instof, SingleTon, M

class __Feature__(SingleTon, M):
    
    def __init__(self, tick, icon):
        M.__init__(self, _tick=tick*1000, _icon=icon)
        
    def get(self, request, *cmd):
        return __View__('none')
    
    def post(self, request, data, *cmd):
        return __View__('none')
    
    def update(self, request, data, *cmd):
        return __View__('none')
    
    def delete(self, request, data, *cmd):
        return __View__('none')
    

class __View__(M):
    
    def __init__(self, ux, **kargs):
        M.__init__(self, _ux=ux, **kargs)
        
    def __create_link__(self, link):
        if instof(link, tuple):
            flink, clink = link
            if flink != None or clink != None:
                return ''' onclick="show_feature('%s','%s');"''' % (flink['_code'] if flink else '', clink if clink else '')
        return ''
    
    def __create_del__(self, did):
        return '''<p class="close" style="float:left !important;padding:0px 5px 0px 0px;margin:0px;" onclick="del_data('%s');"> &times; </p>''' % did if did else ''
        
    def __render__(self):
        return ''
