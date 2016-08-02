'''
Created on 2016. 8. 2.

@author: "comfact"
'''

from ciscowebkit.common.pygics import L, M
from ciscowebkit.common.abstract import __View__

class JustGage(__View__):
    
    def __init__(self, value, min=0, max=100, **option):
        __View__.__init__(self, 'justgage', value=value, min=min, max=max, opts=M())
        if 'desc' in option: self.opts['title'] = option['desc']
        self._link = self.__create_link__(option['link']) if 'link' in option else ''
        self._title = '<h3 class="cw-css-elem-title">%s</h3>' % option['title'] if 'title' in option else ''
        self._height = ' style="height:%dpx;"' % option['height'] if 'height' in option else ''
        
    def __render__(self):
        return '<div>%s<div id="cw-view-%s" class="cw-resizable"%s%s></div></div>' % (self._title, self._id, self._link, self._height)
