'''
Created on 2016. 7. 20.

@author: "comfact"
'''

from ciscowebkit.common.pygics import L, M
from ciscowebkit.common.abstract import __View__

class View:
    
    class NumLine(__View__):
        
        def __init__(self, title, icon='fa-line-chart', panel='default'):
            __View__.__init__(self, title, icon, panel)
            
        def optGrid(self, xmin=None, xmax=None, xtick=None, ymin=None, ymax=None, ytick=None):
            if xmin != None: self['xmin'] = xmin
            if xmax != None: self['xmax'] = xmax
            if xtick != None: self['xtick'] = xtick
            if ymin != None: self['ymin'] = ymin
            if ymax != None: self['ymax'] = ymax
            if ytick != None: self['ytick'] = ytick
            return self 
        
        def __html__(self, feature, scr='lg', size=12):
            return '''
<div class="col-%s-%d feature ft-%s">
    <div class="panel panel-%s">
        <div class="panel-heading">
            <h3 class="panel-title"><i class="fa %s"></i> %s</h3>
        </div>
        <div class="panel-body">
            <div class="flot-chart">
                <div id="data-%s" class="flot-chart-content"></div>
            </div>
        </div>
    </div>
</div>''' % (scr, size, feature._id, self.panel, self.icon, self.title, self.view_id)

        def __js__(self, feature):
            xaxis = ''
            yaxis = ''
            if 'xmin' in self: xaxis += 'min:%d,' % self.xmin
            if 'xmax' in self: xaxis += 'max:%d,' % self.xmax
            if 'xtick' in self: xaxis += 'tickSize:%d,tickFormatter:function(val,axis){return val|0;}' % self.xtick
            if 'ymin' in self: yaxis += 'min:%d,' % self.ymin
            if 'ymax' in self: yaxis += 'max:%d,' % self.ymax
            if 'ytick' in self: yaxis += 'tickSize:%d,tickFormatter:function(val,axis){return val|0;}' % self.ytick
            if xaxis != '': xaxis = 'xaxis:{' + xaxis + '},'
            if yaxis != '': yaxis = 'yaxis:{' + yaxis + '},'
            return '''
function (cmd, data) {
    var options = {
        series:{lines:{show:true},points:{show:true}},
        grid:{hoverable:true,
            markings: function(axes) {
                var markings = [];
                var xaxis = axes.xaxis;
                for (var x = Math.floor(xaxis.min); x < xaxis.max; x += xaxis.tickSize * 2) {
                    markings.push({ xaxis: { from: x, to: x + xaxis.tickSize }, color: "#f9f9f9" });
                }
                return markings;
            }
        },
        %s
        %s
        tooltip:true,
        tooltipOpts:{content:"'%%s' of %%x is %%y",shifts:{x:-60,y:25}}
    };
    $.plot("#data-%s", data["data"], options);
}
''' % (xaxis, yaxis, self.view_id)

    class Pie(__View__):
        
        def __init__(self, title, icon='fa-pie-chart', panel='default'):
            __View__.__init__(self, title, icon, panel)
        
        def __html__(self, feature, scr='lg', size=12):
            return '''
<div class="col-%s-%d feature ft-%s">
    <div class="panel panel-%s">
        <div class="panel-heading">
            <h3 class="panel-title"><i class="fa %s"></i> %s</h3>
        </div>
        <div class="panel-body">
            <div class="flot-chart">
                <div id="data-%s" class="flot-chart-content"></div>
            </div>
        </div>
    </div>
</div>''' % (scr, size, feature._id, self.panel, self.icon, self.title, self.view_id)

        def __js__(self, feature):
            return '''
function (cmd, data) {
    function labelFormatter(label, series) {
        return "<div style='font-size:8pt; text-align:center; padding:2px; color:white;'>" + label + "<br/>" + Math.round(series.percent) + "%%</div>";
    };
    var options = {
        series:{pie:{show:true,resize:true,radius:3/4,label:{show:true,radius:3/4,formatter:labelFormatter,background:{opacity:0.5,color:'#000'}}}},
        grid:{hoverable:true},
        tooltip:true,
        tooltipOpts:{content:"%%p.0%%, %%s",shifts:{x:20,y:0},defaultTheme:false}
    }
    
    $.plot("#data-%s", data, options);
}
''' % self.view_id

class Data:
    
    class NumLine(M):
        def __init__(self, xlabel, *ylabel):
            M.__init__(self, xlabel=xlabel, ylabel=L(*ylabel), data=L())
            for y in ylabel: self.data << M(label=y, data=L())
            
        def add(self, xdata, *ydata):
            idx = 0
            for data in self.data:
                data.data << L(xdata, ydata[idx])
                idx += 1
            return self
    
    class Pie(L):
        def __init__(self): L.__init__(self)
        
        def add(self, label, data):
            self << M(label=label, data=data)
            return self
