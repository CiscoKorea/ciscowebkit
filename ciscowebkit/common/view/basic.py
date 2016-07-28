'''
Created on 2016. 7. 18.

@author: "comfact"
'''

from ciscowebkit.common.pygics import L, M
from ciscowebkit.common.abstract import __View__

class Layout(__View__):
    
    LARGE = 'lg'
    MIDIUM = 'md'
    SMALL = 'sm'
    
    def __init__(self):
        __View__.__init__(self, 'layout', row=L())
    
    def addRow(self):
        self.row << L()
        return self
    
    def addCol(self, view, scr='lg', size=12):
        self.row[-1] << M(view=view, scr=scr, size=size)
        return self
    
    def __render__(self):
        html = ''
        idx = 1;
        for row in self.row:
            html += '<div class="row">\n'
            for col in row:
                col.view['_id'] = self._id + '_L' + str(idx); idx += 1
                html += '<div class="col-%s-%d">\n' % (col.scr, col.size) + col.view.__render__() + '</div>\n'
            html += '</div>\n'
        return html

class Panel(__View__):
    
    DEFAULT = 'default'
    RED = 'red'
    GREEN = 'green'
    YELLOW = 'yellow'
    BLUE = 'primary'
    PRIME = 'primary'
    ACTIVE = 'active'
    SUCCESS = 'success'
    INFO = 'info'
    WARNING = 'warning'
    DANGER = 'danger'
    
    def __init__(self, title, view, panel='default', icon='fa-sticky-note-o', link=None):
        __View__.__init__(self, 'panel', view=view)
        self._title = title
        self._panel = panel
        self._icon = icon
        self._link = self.__create_link__(link)
        
    def __render__(self):
        self.view['_id'] = self._id + '_P'
        return '''<div id="cw-view-%s" class="panel panel-%s">
<div class="panel-heading"><h3 class="panel-title"><i class="fa %s"></i> %s</h3></div>
<div class="panel-body"%s>%s</div>
</div>
''' % (self._id, self._panel, self._icon, self._title, self._link, self.view.__render__())

class Text(__View__):
    
    def __init__(self, text, link=None):
        __View__.__init__(self, 'text', text=text)
        self._link = self.__create_link__(link)
        
    def __render__(self):
        return '<p id="cw-view-%s"%s></p>\n' % (self._id, self._link)
    
class VList(__View__):
    
    def __init__(self):
        __View__.__init__(self, 'vlist', item=L())
    
    def add(self, title, badge=None, icon=None, cmd=None):
        self.item << M(title=title, link=self.__create_link__((None,cmd)), cmd=cmd, icon=icon, badge=badge)
        return self
    
    def __render__(self):
        return '<div id="cw-view-%s" class="list-group"></div>\n' % self._id
    
class HList(__View__):
    
    def __init__(self):
        __View__.__init__(self, 'hlist', item=L())
    
    def add(self, title, badge=None, icon=None, cmd=None):
        self.item << M(title=title, link=self.__create_link__((None,cmd)), cmd=cmd, icon=icon, badge=badge)
        return self
    
    def __render__(self):
        return '<div id="cw-view-%s" class="btn-group" role="group"></div>\n' % self._id
    
class InfoBlock(__View__):
    
    def __init__(self, title, msg='', icon='fa-info-circle', link=None):
        __View__.__init__(self, 'infoblock', title=title, msg=msg, icon=icon)
        self._link = self.__create_link__(link)
        
    def __render__(self):
        return '<div id="cw-view-%s"%s></div>' % (self._id, self._link)
    
class InfoPanel(__View__):
    
    def __init__(self, title, count, desc='', panel='default', icon='fa-info-circle', link=None):
        __View__.__init__(self, 'infopanel', title=title, count=count, desc=desc, panel=panel, icon=icon, link=self.__create_link__(link))
        
    def __render__(self):
        return '<div id="cw-view-%s"></div>' % self._id
    
class InfoDoc(__View__):
    
    def __init__(self, doc, link=None):
        __View__.__init__(self, 'infodoc', doc=doc)
        self._link = self.__create_link__(link)
        
    def __render__(self):
        return '<pre id="cw-view-%s" class="well"%s></pre>' % (self._id, self._link)
    
class Table(__View__):
    
    ACTIVE = 'active'
    SUCCESS = 'success'
    WARNING = 'warning'
    DANGER = 'danger'
    
    def __init__(self, *heads, **option):
        __View__.__init__(self,
                          'table',
                          heads=L(*heads),
                          recs=L(),
                          _stripe=option['stripe'] if 'stripe' in option else False,
                          _link=self.__create_link__(option['link']) if 'link' in option else ''
                          )
        self._title = '<h3 class="cw-css-elem-title">%s</h3>' % option['title'] if 'title' in option else ''
        
    def add(self, *cols, **option):
        rec = M(cols=L(*cols))
        rec['type'] = ''' class="%s"''' % option['type'] if 'type' in option else ''
        rec['link'] = self.__create_link__(option['link']) if 'link' in option else ''
        rec['did'] = self.__create_del__(option['did']) if 'did' in option else ''
        self.recs << rec
        return self
    
    def __render__(self):
        return '<div>%s<div id="cw-view-%s"></div></div>' % (self._title, self._id)

class Form(__View__):
    
    def __init__(self, submit, **kargs):
        __View__.__init__(self, 'form', **kargs)
        self._submit = submit
        self._order = L()
    
    def addText(self, name, title, placeholder=''):
        self[name] = M(_type='text', name=name, title=title, placeholder=placeholder)
        self._order << name
        return self
    
    def addTextArea(self, name, title, placeholder=''):
        self[name] = M(_type='textarea', name=name, title=title, placeholder=placeholder)
        self._order << name
        return self
    
    def __render__(self):
        data = '{'
        form = ''
        idx = 1
        for name in self._order:
            _id = self._id + '_I' + str(idx)
            elem = self[name]
            idx += 1
            data += '''%s: $('#%s').val(),''' % (name, _id)
            if elem._type == 'text': form += '''<div class="form-group"><label>%s</label><input id="%s" class="form-control" placeholder="%s"></div>''' % (elem.title, _id, elem.placeholder)
            elif elem._type == 'textarea': form += '''<div class="form-group"><label>%s</label><textarea id="%s" class="form-control" row="3" placeholder="%s"></div>''' % (elem.title, _id, elem.placeholder)
        data += '}'
        html = '''<form id="%s" roll="form">%s<div><span class="pull-right"><p class="btn btn-default" onclick="send_form(%s);">%s</p></span></div></form>''' % (self._id, form, data, self._submit)
        return html
        