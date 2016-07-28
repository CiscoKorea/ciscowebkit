'''
Created on 2016. 7. 20.

@author: "comfact"
'''

from ciscowebkit.common.pygics import L, M
from ciscowebkit.common.abstract import __View__

class MorrisLine:
    
    HTML = '''
                <div class="col-%s-%d feature ft-%s">
                    <div class="panel panel-%s">
                        <div class="panel-heading">
                            <h3 class="panel-title"><i class="fa %s"></i> %s</h3>
                        </div>
                        <div class="panel-body">
                            <div id="data-%s">
                            </div>
                        </div>
                    </div>
                </div>
'''
    JS = '''
function (cmd, data) {
    document.getElementById("data-%s").innerHTML = ''
    Morris.%s({
        element: 'data-%s',
        data: data["data"],
        xkey: data["xlabel"],
        ykeys: data["ylabel"],
        labels: data["ylabel"],
        %s
        resize: true
    });
}
'''
        
    class View(__View__):
        
        def __init__(self, title, icon='fa-line-chart', panel='default'):
            __View__.__init__(self, title, icon, panel)
            self['type'] = 'Line'
            
        def optGrid(self, ymin=None, ymax=None):
            if min != None: self['ymin'] = ymin
            if max != None: self['ymax'] = ymax
            return self
        
        def optArea(self):
            self['type'] = 'Area';
            return self
        
        def optSmooth(self):
            self['smooth'] = True;
            return self
        
        def __html__(self, feature, scr='lg', size=12):
            return MorrisLine.HTML % (scr, size, feature._id, self.panel, self.icon, self.title, self.view_id)

        def __js__(self, feature):
            options = ''
            if 'ymin' in self: options += 'ymin:%s,' % self.ymin
            if 'ymax' in self: options += 'ymax:%s,' % self.ymax
            if 'smooth' in self: options += 'smooth:true,'
            return MorrisLine.JS % (self.view_id, self.type, self.view_id, options)
    
    class Data(M):
        def __init__(self, xlabel, *ylabel):
            M.__init__(self, xlabel=xlabel, ylabel=L(*ylabel), data=L())
            
        def add(self, xdata, *ydata):
            record = M()
            record[self.xlabel] = xdata
            idx = 0
            for ylabel in self.ylabel:
                record[ylabel] = ydata[idx]
                idx += 1
            self.data << record
            return self

class MorrisBar:
    
    HTML = '''
                <div class="col-%s-%d feature ft-%s">
                    <div class="panel panel-%s">
                        <div class="panel-heading">
                            <h3 class="panel-title"><i class="fa %s"></i> %s</h3>
                        </div>
                        <div class="panel-body">
                            <div id="data-%s">
                            </div>
                        </div>
                    </div>
                </div>
'''
    JS = '''
function (cmd, data) {
    document.getElementById("data-%s").innerHTML = ''
    Morris.Bar({
        element: 'data-%s',
        data: data["data"],
        xkey: data["xlabel"],
        ykeys: data["ylabel"],
        labels: data["ylabel"],
        %s
        barRatio: 0.4,
        xLabelAngle: 35,
        hideHover: 'auto',
        resize: true
    });
}
'''

    class View(__View__):
        
        def __init__(self, title, icon='fa-bar-chart', panel='default'):
            __View__.__init__(self, title, icon, panel)
            
        def optGrid(self, ymin=None, ymax=None):
            if min != None: self['ymin'] = ymin
            if max != None: self['ymax'] = ymax
            return self
        
        def __html__(self, feature, scr='lg', size=12):
            return MorrisBar.HTML % (scr, size, feature._id, self.panel, self.icon, self.title, self.view_id)

        def __js__(self, feature):
            options = ''
            if 'ymin' in self: options += 'ymin:%s,' % self.ymin
            if 'ymax' in self: options += 'ymax:%s,' % self.ymax
            return MorrisBar.JS % (self.view_id, self.view_id, options)
        
    class Data(M):
        def __init__(self, xlabel, *ylabel):
            M.__init__(self, xlabel=xlabel, ylabel=L(*ylabel), data=L())
            
        def add(self, xdata, *ydata):
            record = M()
            record[self.xlabel] = xdata
            idx = 0
            for ylabel in self.ylabel:
                record[ylabel] = ydata[idx]
                idx += 1
            self.data << record
            return self

class MorrisDonut:
    
    HTML = '''
                <div class="col-%s-%d feature ft-%s">
                    <div class="panel panel-%s">
                        <div class="panel-heading">
                            <h3 class="panel-title"><i class="fa %s"></i> %s</h3>
                        </div>
                        <div class="panel-body">
                            <div id="data-%s">
                            </div>
                        </div>
                    </div>
                </div>
'''
    JS = '''
function (cmd, data) {
    document.getElementById("data-%s").innerHTML = ''
    Morris.Donut({
        element: 'data-%s',
        data : data,
        resize: true
    });
}
'''

    class View(__View__):
        
        def __init__(self, title, icon='fa-pie-chart', panel='default'):
            __View__.__init__(self, title, icon, panel)
            
        def __html__(self, feature, scr='lg', size=12):
            return MorrisDonut.HTML % (scr, size, feature._id, self.panel, self.icon, self.title, self.view_id)

        def __js__(self, feature):
            return MorrisDonut.JS % (self.view_id, self.view_id)
        
    class Data(L):
        def __init__(self): L.__init__(self)
        
        def add(self, label, data):
            self << M(label=label, value=data)
            return self
