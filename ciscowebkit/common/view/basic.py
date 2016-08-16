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

'''
Created on 2016. 7. 18.

@author: "comfact"
'''

from ciscowebkit.common.pygics import instof, L, M
from ciscowebkit.common.abstract import __View__

class Layout(__View__):
    
    BLUE = '#4169e1'
    GREEN = '#008000'
    YELLOW = '#ffd700'
    RED = '#ff0000'
    
    def __init__(self, *rows, **option):
        __View__.__init__(self, 'layout', rows=L(*rows))
        self._border = ' style="border: %dpx solid %s;"' % (option['border'][0], option['border'][1]) if 'border' in option else ''
        
    def __call__(self, *rows):
        for row in rows: self.rows << row
        return self
        
    def __render__(self):
        html = '<div%s>' % self._border
        idx = 0
        for row in self.rows:
            row['_id'] = self._id + 'R%d' % idx; idx += 1
            html += row.__render__()
        return html + '</div>'

class Row(__View__):
    
    DEFAULT = 200
    DOUBLE = 400
    HALF = 100
    
    def __init__(self, *cols, **option):
        __View__.__init__(self, 'layout_row', cols=L())
        for col in cols:
            if instof(col, Col): self.cols << col
            else: self.cols << Col(col)
            
    def __call__(self, *cols):
        for col in cols:
            if instof(col, Col): self.cols << col
            else: self.cols << Col(col)
        return self
        
    def __render__(self):
        html = '<div class="row">'
        idx = 0
        for col in self.cols:
            col['_id'] = self._id + 'C%d' % idx; idx += 1
            html += col.__render__()
        html += '</div>'
        return html

class Col(__View__):
    
    LARGE = 'lg'
    MIDIUM = 'md'
    SMALL = 'sm'
    
    def __init__(self, view, *widths):
        __View__.__init__(self, 'layout_col', view=view)
        self._widths = L()
        if len(widths) > 0:
            for width in widths:
                if instof(width, tuple): self._widths << width
        else: self._widths << ('lg', 12)
        
    def __render__(self):
        html = '<div class="'
        for width in self._widths: html += 'col-%s-%d ' % width
        self.view['_id'] = self._id + 'V'
        html += '">' + self.view.__render__() + '</div>\n'
        return html
    
class Empty(__View__):
    
    def __init__(self):
        __View__.__init__(self, 'empty')
        
class Error(__View__):
    
    def __init__(self, msg):
        __View__.__init__(self, 'error', doc=msg)
        
    def __render__(self):
        return '<pre id="cw-view-%s" class="well"></pre>' % self._id

class Panel(__View__):
    
    DEFAULT = 'default'
    
    ACTIVE = 'active'
    SUCCESS = 'success'
    WARNING = 'warning'
    INFO = 'info'
    DANGER = 'danger'
    
    BLUE = 'primary'
    GREEN = 'green'
    YELLOW = 'yellow'
    RED = 'red'
    
    LIGHT_BLUE = 'info'
    LIGHT_GREEN = 'success'
    LIGHT_YELLOW = 'warning'
    LIGHT_RED = 'danger'
    
    
    def __init__(self, title, view, panel='default', icon='fa-archive', link=None):
        __View__.__init__(self, 'panel', view=view)
        self._title = title
        self._panel = panel
        self._icon = icon
        self._link = self.__create_link__(link)
        
    def __render__(self):
        self.view['_id'] = self._id + 'P'
        return '''<div id="cw-view-%s" class="panel panel-%s">
<div class="panel-heading"><h3 class="panel-title"><i class="fa %s"></i> %s</h3></div>
<div class="panel-body"%s>%s</div>
</div>
''' % (self._id, self._panel, self._icon, self._title, self._link, self.view.__render__())

class Plain(__View__):
    
    def __init__(self, view, link=None):
        __View__.__init__(self, 'plain', view=view)
        self._link = self.__create_link__(link)
        
    def __render__(self):
        self.view['_id'] = self._id + 'P'
        return '''<div id="cw-view-%s" class="panel panel-default">
<div class="panel-body"%s>%s</div>
</div>
''' % (self._id, self._link, self.view.__render__())

class Text(__View__):
    
    def __init__(self, text, link=None, height=None):
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
    
class InfoNoti(__View__):
    
    def __init__(self, title, msg='', panel='default', icon='fa-info-circle', link=None):
        __View__.__init__(self, 'infonoti', title=title, msg=msg, panel=panel, icon=icon, link=self.__create_link__(link))
        
    def __render__(self):
        return '<div id="cw-view-%s"></div>' % self._id
    
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
    
    def addText(self, name, title='', placeholder=''):
        self[name] = M(_type='text', name=name, title=title, placeholder=placeholder)
        self._order << name
        return self
    
    def addTextArea(self, name, title, placeholder=''):
        self[name] = M(_type='textarea', name=name, title=title, placeholder=placeholder)
        self._order << name
        return self
    
    def addPassword(self, name, title, placeholder=''):
        self[name] = M(_type='password', name=name, title=title, placeholder=placeholder)
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
            if elem._type == 'text':
                if elem.title == '': form += '''<div class="form-group"><input id="%s" class="form-control" placeholder="%s"></div>''' % (_id, elem.placeholder)
                else: form += '''<div class="form-group"><label>%s</label><input id="%s" class="form-control" placeholder="%s"></div>''' % (elem.title, _id, elem.placeholder)
            elif elem._type == 'password':
                if elem.title == '': form += '''<div class="form-group"><input id="%s" type="password" class="form-control" placeholder="%s"></div>''' % (_id, elem.placeholder)
                else: form += '''<div class="form-group"><label>%s</label><input id="%s" type="password" class="form-control" placeholder="%s"></div>''' % (elem.title, _id, elem.placeholder)                
            elif elem._type == 'textarea': form += '''<div class="form-group"><label>%s</label><textarea id="%s" class="form-control" row="3" placeholder="%s"></div>''' % (elem.title, _id, elem.placeholder)
        data += '}'
        html = '''<form id="%s" roll="form">%s<div><span class="pull-right"><p class="btn btn-default" onclick="send_form(%s);">%s</p></span></div></form>''' % (self._id, form, data, self._submit)
        return html

class Terminal(__View__):
    
    def __init__(self, init_scr='', init_loc='', line_cnt=200):
        __View__.__init__(self, 'terminal')
        self.setScreen(init_scr)
        self.setLocation(init_loc)
        self.line_cnt = line_cnt
        
    def addScreen(self, scr):
        self.screen += scr
        lcnt = self.screen.count('\n')
        if lcnt > self.line_cnt:
            lines = self.screen.split('\n')
            self.screen = '\n'.join(lines[-self.line_cnt:])
        return self
    
    def setScreen(self, scr):
        self.screen = scr
        return self
    
    def setLocation(self, loc):
        if loc != '': self.location = loc + ' '
        else: self.location = ''
        return self
        
    def __render__(self):
        html = '''
<div class="panel panel-default">
    <div class="panel-heading"><h3 class="panel-title"><i class="fa fa-terminal"></i></h3></div>
    <div class="panel-body">
        <div class="cw-term-background" onclick="$('#cw-view-%s').focus();">
            <pre class="cw-term-screen">%s</pre>
            <div class="cw-term-input>
                <form roll="form">
                    <label class="cw-term-location">%s$&nbsp;</label>
                    <span class="cw-term-command">
                        <input type="text" id="cw-view-%s" class="cw-term-command-text" onkeydown="if (event.keyCode == 13) { send_form_imidiate({cmd:$('#cw-view-%s').val()}); }" />
                    </span>
                </form>
            </div>
        </div>
    </div>
</div>
''' % (self._id, self.screen, self.location, self._id, self._id)
        return html
        
        
        
        
        
        
