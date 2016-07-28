'''
Created on 2016. 7. 20.

@author: "comfact"
'''

from ciscowebkit.common.pygics import L, M
from ciscowebkit.common.abstract import __View__

class ChartistLine(__View__):
    
    def __init__(self, *lines, **option):
        __View__.__init__(self, 'ctst_line', lines=L(*lines), opts=M(), labels=L(), series=L(), anima=False)
        for l in self.lines: self.series << L()
        self._link = self.__create_link__(option['link']) if 'link' in option else ''
        self._title = '<h3 class="cw-css-elem-title">%s</h3>' % option['title'] if 'title' in option else ''
        
    def grid(self, ymin=None, ymax=None):
        if ymin != None: self.opts['low'] = ymin
        if ymax != None: self.opts['high'] = ymax
        return self
    
    def ani(self):
        self['anima'] = True
        return self
        
    def add(self, xdata, *ydata):
        self.labels << xdata
        idx = 0
        for s in self.series:
            s << M(meta=self.lines[idx], value=ydata[idx])
            idx += 1
        return self
    
    def __render__(self):
        return '<div>%s<div id="cw-view-%s" class="ct-chart"%s></div></div>' % (self._title, self._id, self._link)

class ChartistArea(__View__):
    
    def __init__(self, *lines, **option):
        __View__.__init__(self, 'ctst_area', lines=L(*lines), opts=M(), labels=L(), series=L(), anima=False)
        for l in self.lines: self.series << L()
        self._link = self.__create_link__(option['link']) if 'link' in option else ''
        self._title = '<h3 class="cw-css-elem-title">%s</h3>' % option['title'] if 'title' in option else ''
        
    def grid(self, ymin=None, ymax=None):
        if ymin != None: self.opts['low'] = ymin
        if ymax != None: self.opts['high'] = ymax
        return self
    
    def ani(self):
        self['anima'] = True
        return self
        
    def add(self, xdata, *ydata):
        self.labels << xdata
        idx = 0
        for s in self.series:
            s << M(meta=self.lines[idx], value=ydata[idx])
            idx += 1
        return self
    
    def __render__(self):
        return '<div>%s<div id="cw-view-%s" class="ct-chart"%s></div></div>' % (self._title, self._id, self._link)


class ChartistVBar(__View__):
    
    def __init__(self, *lines, **option):
        __View__.__init__(self, 'ctst_vbar', lines=L(*lines), opts=M(seriesBarDistance=15), labels=L(), series=L(), size=15, anima=False)
        if len(self.lines) > 0:
            for l in self.lines: self.series << L()
            self.add = self.__addMapped__
        else:
            self.add = self.__addLinear__
            self.opts['distributeSeries'] = True
        self._link = self.__create_link__(option['link']) if 'link' in option else ''
        self._title = '<h3 class="cw-css-elem-title">%s</h3>' % option['title'] if 'title' in option else ''
        
    def grid(self, ymin=None, ymax=None):
        if ymin != None: self.opts['low'] = ymin
        if ymax != None: self.opts['high'] = ymax
        return self
    
    def stroke(self, size=None, dist=None):
        if size != None: self['size'] = size
        if dist != None: self.opts['seriesBarDistance'] = dist
        return self
    
    def stack(self):
        self.opts['stackBars'] = True
        return self
    
    def ani(self):
        self['anima'] = True
        return self
    
    def __addMapped__(self, xdata, *ydata):
        self.labels << xdata
        idx = 0
        for s in self.series:
            s << M(meta=self.lines[idx], value=ydata[idx])
            idx += 1
        return self
        
    def __addLinear__(self, label, value):
        self.labels << label
        self.series << M(meta=label, value=value)
        return self
        
    def __render__(self):
        return '<div>%s<div id="cw-view-%s" class="ct-chart"%s></div></div>' % (self._title, self._id, self._link)
    
class ChartistHBar(__View__):
    
    def __init__(self, *lines, **option):
        __View__.__init__(self, 'ctst_hbar', lines=L(*lines), opts=M(seriesBarDistance=5), labels=L(), series=L(), size=5, anima=False)
        if len(self.lines) > 0:
            for l in self.lines: self.series << L()
            self.add = self.__addMapped__
        else:
            self.add = self.__addLinear__
            self.opts['distributeSeries'] = True
        self._link = self.__create_link__(option['link']) if 'link' in option else ''
        self._title = '<h3 class="cw-css-elem-title">%s</h3>' % option['title'] if 'title' in option else ''
        
    def grid(self, ymin=None, ymax=None):
        if ymin != None: self.opts['low'] = ymin
        if ymax != None: self.opts['high'] = ymax
        return self
    
    def stroke(self, size=None, dist=None):
        if size != None: self['size'] = size
        if dist != None: self.opts['seriesBarDistance'] = dist
        return self
    
    def stack(self):
        self.opts['stackBars'] = True
        return self
    
    def ani(self):
        self['anima'] = True
        return self
    
    def __addMapped__(self, xdata, *ydata):
        self.labels << xdata
        idx = 0
        for s in self.series:
            s << M(meta=self.lines[idx], value=ydata[idx])
            idx += 1
        return self
        
    def __addLinear__(self, label, value):
        self.labels << label
        self.series << M(meta=label, value=value)
        return self
        
    def __render__(self):
        return '<div>%s<div id="cw-view-%s" class="ct-chart"%s></div></div>' % (self._title, self._id, self._link)
    
class ChartistPie(__View__):
    
    def __init__(self, title, **option):
        __View__.__init__(self, 'ctst_pie', title=title, opts=M(donutWidth='100%'), labels=L(), series=L())
        self._link = self.__create_link__(option['link']) if 'link' in option else ''
        self._title = '<h3 class="cw-css-elem-title">%s</h3>' % option['title'] if 'title' in option else ''
        
    def stroke(self, size):
        self.opts['donutWidth'] = str(size) + '%'
        return self
        
    def ani(self):
        self['anima'] = True
        return self
        
    def add(self, label, value):
        self.labels << label
        self.series << M(meta=label, value=value)
        return self
    
    def __render__(self):
        return '<div>%s<div id="cw-view-%s" class="ct-chart"%s></div></div>' % (self._title, self._id, self._link)
