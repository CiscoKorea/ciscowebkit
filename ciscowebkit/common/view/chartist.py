<<<<<<< HEAD
#!/usr/bin/env python
# -*- coding: utf-8 -*-
################################################################################
#        _____ _                  _____           _                            #
#       / ____(_)                / ____|         | |                           #
#      | |     _ ___  ___ ___   | (___  _   _ ___| |_ ___ _ __ ___  ___        #
#      | |    | / __|/ __/ _ \   \___ \| | | / __| __/ _ \ '_ ` _ \/ __|       #
#      | |____| \__ \ (_| (_) |  ____) | |_| \__ \ ||  __/ | | | | \__ \       #
#       \_____|_|___/\___\___/  |_____/ \__, |___/\__\___|_| |_| |_|___/       #
#                                        __/ |                                 #
#                                       |___/                                  #
#           _  __                       _____       _  _____ ______            #
#          | |/ /                      / ____|     | |/ ____|  ____|           #
#          | ' / ___  _ __ ___  __ _  | (___   ___ | | (___ | |__              #
#          |  < / _ \| '__/ _ \/ _` |  \___ \ / _ \| |\___ \|  __|             #
#          | . \ (_) | | |  __/ (_| |  ____) | (_) | |____) | |____            #
#          |_|\_\___/|_|  \___|\__,_| |_____/ \___/|_|_____/|______|           #
#                                                                              #
################################################################################
#                                                                              #
# Copyright (c) 2016 Cisco Systems                                             #
# All Rights Reserved.                                                         #
#                                                                              #
# Licensed under the Apache License, Version 2.0 (the "License"); you may      #
# not use this file except in compliance with the License. You may obtain      #
# a copy of the License at                                                     #
#                                                                              #
# http://www.apache.org/licenses/LICENSE-2.0                                   #
#                                                                              #
# Unless required by applicable law or agreed to in writing, software          #
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT #
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the  #
#    License for the specific language governing permissions and limitations   #
#    under the License.                                                        #
#                                                                              #
################################################################################

=======
#!/usr/bin/env python
# -*- coding: utf-8 -*-
################################################################################
#                                                                              #
################################################################################
#                                                                              #
# Copyright (c) 2016 Cisco Systems                                             #
# All Rights Reserved.                                                         #
#                                                                              #
# Licensed under the Apache License, Version 2.0 (the "License"); you may      #
# not use this file except in compliance with the License. You may obtain      #
# a copy of the License at                                                     #
#                                                                              #
# http://www.apache.org/licenses/LICENSE-2.0                                   #
#                                                                              #
# Unless required by applicable law or agreed to in writing, software          #
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT #
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the  #
#    License for the specific language governing permissions and limitations   #
#    under the License.                                                        #
#                                                                              #
################################################################################


>>>>>>> refs/remotes/origin/master
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
        if 'height' in option: self.opts['height'] = str(option['height']) + 'px'
        
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
        if 'height' in option: self.opts['height'] = str(option['height']) + 'px'
        
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


class ChartistBar(__View__):
    
    def __init__(self, *lines, **option):
        __View__.__init__(self, 'ctst_bar', lines=L(*lines), opts=M(seriesBarDistance=15), labels=L(), series=L(), size=15, anima=False)
        if len(self.lines) > 0:
            for l in self.lines: self.series << L()
            self.add = self.__addMapped__
        else:
            self.add = self.__addLinear__
            self.opts['distributeSeries'] = True
        self._link = self.__create_link__(option['link']) if 'link' in option else ''
        self._title = '<h3 class="cw-css-elem-title">%s</h3>' % option['title'] if 'title' in option else ''
        if 'height' in option: self.opts['height'] = str(option['height']) + 'px'
        
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
    
class ChartistSlide(__View__):
    
    def __init__(self, *lines, **option):
        __View__.__init__(self, 'ctst_slide', lines=L(*lines), opts=M(seriesBarDistance=5), labels=L(), series=L(), size=5, anima=False)
        if len(self.lines) > 0:
            for l in self.lines: self.series << L()
            self.add = self.__addMapped__
        else:
            self.add = self.__addLinear__
            self.opts['distributeSeries'] = True
        self._link = self.__create_link__(option['link']) if 'link' in option else ''
        self._title = '<h3 class="cw-css-elem-title">%s</h3>' % option['title'] if 'title' in option else ''
        if 'height' in option: self.opts['height'] = str(option['height']) + 'px'
        
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
    
class ChartistDonut(__View__):
    
    def __init__(self, **option):
        __View__.__init__(self, 'ctst_donut', opts=M(donutWidth='100%'), labels=L(), series=L())
        self._link = self.__create_link__(option['link']) if 'link' in option else ''
        self._title = '<h3 class="cw-css-elem-title">%s</h3>' % option['title'] if 'title' in option else ''
        if 'height' in option: self.opts['height'] = str(option['height']) + 'px'
        
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
