'''
Created on 2016. 7. 20.

@author: "comfact"
'''

from ciscowebkit.common.pygics import L, M
from ciscowebkit.common.abstract import __View__


class __Morris__(__View__):
    
    def __init__(self, chart_name, *lines, **option):
        __View__.__init__(self, chart_name, lines=L(*lines), opts=M(), data=L())
        if len(self.lines) == 0: self.lines << 'Data'
        self._link = self.__create_link__(option['link']) if 'link' in option else ''
        self._title = '<h3 class="cw-css-elem-title">%s</h3>' % option['title'] if 'title' in option else ''
        self._height = ' style="height:%dpx"' % option['height'] if 'height' in option else ''
        
    def grid(self, ymin=None, ymax=None):
        if ymin != None: self.opts['ymin'] = ymin
        if ymax != None: self.opts['ymax'] = ymax
        return self
    
    def add(self, xdata, *ydata):
        record = M()
        record['tstamp'] = xdata
        idx = 0
        for line in self.lines:
            record[line] = ydata[idx]
            idx += 1
        self.data << record
        return self
    
    def __render__(self):
        return '<div>%s<div id="cw-view-%s"%s%s></div></div>' % (self._title, self._id, self._link, self._height)
    

class MorrisLine(__Morris__):
    
    def __init__(self, *lines, **option):
        __Morris__.__init__(self, 'morr_line', *lines, **option)
    
class MorrisArea(__Morris__):
    
    def __init__(self, *lines, **option):
        __Morris__.__init__(self, 'morr_area', *lines, **option)
    
class MorrisBar(__Morris__):
    
    def __init__(self, *bars, **option):
        __Morris__.__init__(self, 'morr_bar', *bars, **option)

class MorrisDonut(__View__):
    
    def __init__(self, **option):
        __View__.__init__(self, 'morr_donut', data=L())
        self._link = self.__create_link__(option['link']) if 'link' in option else ''
        self._title = '<h3 class="cw-css-elem-title">%s</h3>' % option['title'] if 'title' in option else ''
        self._height = ' style="height:%dpx"' % option['height'] if 'height' in option else ''
        
    def add(self, label, value):
        self.data << M(label=label, value=value)
        return self
    
    def __render__(self):
        return '<div>%s<div id="cw-view-%s"%s%s></div></div>' % (self._title, self._id, self._link, self._height)
    