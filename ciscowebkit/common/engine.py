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
Created on 2016. 7. 5.

@author: "comfact"
'''

import os
import hashlib

from django.template import Template, Context, loader
from django.http import HttpResponse

from ciscowebkit.common.pygics import instof, classof, nameof, iterkv, inf, greg, SingleTon, Struct, L, M, Module, NameSpace, Dir
from ciscowebkit.common.feature import Feature, SubFeature

from product import PRODUCT_ORDER

from dashboard import Dashboard

from ciscowebkit.common.manager.aci import ACIManager

class Engine(SingleTon):
            
    def __init__(self):
        self.__load_product_managers__()
        self.__load_templates__()
        self.__load_features__()
        self.__build_template__()

    def __load_product_managers__(self):
        self.acimng = ACIManager(mon_sec=60, mon_cnt=10)
        #uncomment for testing 
#         self.acimng.addDomain('DCLab1', '10.72.86.21/10.72.86.22/10.72.86.23', 'admin', '1234Qwer')
        greg('ACI', self.acimng)
    
    def __load_templates__(self):
        self.ciscowebkit_tpl = loader.get_template('ciscowebkit.html')
        self.ciscowebkit_js_tpl = loader.get_template('ciscowebkit.js')
        self.page_not_found_tpl = Template('Page Not Found').render(Context())
        self.internal_error_tpl = Template('Internal Error').render(Context())
    
    def __load_features__(self):
        self.products = M()
        self.products['_porder'] = L()
        greg('PRODUCTS', self.products)
        for p in PRODUCT_ORDER: self.products._porder << p.lower()
        
        p_paths = Dir.showall('product/')
        for p_path in p_paths:
            if not Dir.isDir(p_path) or not Dir.isDir(p_path): continue
            p_raw = os.path.split(p_path)[-1]
            p_name = p_raw.lower()
            p_code = p_name
            p_url = '/' + p_name + '/'
            p_title = p_raw.replace('_', ' ')
            self.products[p_name] = M()
            self.products[p_name]['_name'] = p_name
            self.products[p_name]['_code'] = p_code
            self.products[p_name]['_url'] = p_url
            self.products[p_name]['_title'] = p_title
            
            # Add-on Feature
            features = NameSpace(p_path, inherited=nameof(Feature))
            for f_raw, f_mod in iterkv(features):
                f_name = f_raw.lower()
                f_code = p_code + '_' + f_name
                f_url = p_url + f_name + '/'
                f_title = f_raw.replace('_', ' ')
                
                for cls_code, cls_obj in iterkv(f_mod):
                    if classof(cls_obj, Feature) and not classof(cls_obj, SubFeature) and nameof(cls_obj) != nameof(Feature):
                        self.products[p_name][f_name] = cls_obj.NEW()
                        self.products[p_name][f_name]['_term'] = True
                        self.products[p_name][f_name]['_name'] = f_name
                        self.products[p_name][f_name]['_code'] = f_code
                        self.products[p_name][f_name]['_url'] = f_url
                        self.products[p_name][f_name]['_title'] = f_title
                        if cls_obj.__doc__ != None: self.products[p_name][f_name]['_desc'] = ' ' + cls_obj.__doc__
                        if cls_obj.__doc__ == None: self.products[p_name][f_name]['_desc'] = ''
                        break
                
                for cls_raw, cls_obj in iterkv(f_mod):
                    if classof(cls_obj, SubFeature) and nameof(cls_obj) != nameof(SubFeature):
                        cls_name = cls_raw.lower()
                        cls_code = f_code + '_' + cls_name
                        cls_url = f_url + cls_name + '/'
                        cls_title = cls_raw.replace('_', ' ')
                        self.products[p_name][f_name]['_term'] = False
                        self.products[p_name][f_name][cls_name] = cls_obj.NEW()
                        self.products[p_name][f_name][cls_name]['_term'] = True
                        self.products[p_name][f_name][cls_name]['_name'] = cls_name
                        self.products[p_name][f_name][cls_name]['_code'] = cls_code
                        self.products[p_name][f_name][cls_name]['_url'] = cls_url
                        self.products[p_name][f_name][cls_name]['_title'] = cls_title
                        if cls_obj.__doc__ != None: self.products[p_name][f_name][cls_name]['_desc'] = ' ' + cls_obj.__doc__
                        if cls_obj.__doc__ == None: self.products[p_name][f_name][cls_name]['_desc'] = ''
            
            # Ordering
            order = Module(p_path + '/__init__.py')
            self.products[p_name]['_forder'] = L()
            for f in order.FEATURE_ORDER:
                if '.' in f: self.products[p_name]._forder << (f.lower().split('.')[0], f.lower().split('.')[1])
                else: self.products[p_name]._forder << f.lower()
                
        # Dashboard
        self.products['dashboard'] = Dashboard()
        self.products.dashboard['_term'] = True
        self.products.dashboard['_name'] = 'dashboard'
        self.products.dashboard['_code'] = 'dashboard'
        self.products.dashboard['_url'] = '/dashboard/'
        self.products.dashboard['_title'] = 'Dashboard'
        self.products.dashboard['_desc'] = 'Cisco Webkit'
            
    def __build_template__(self):
        self.pfm = M()
        greg('PFM', self.pfm)
        pnav = ''
        fnav = ''
        page = ''
        
        for p_name in self.products._porder:
            if p_name in self.products:
                self.pfm[p_name] = None
                pnav += '''                <a id="cw-pnav-%s" class="cw-pnav" onclick="show_product(\'%s\');">%s</a>\n''' % (p_name, p_name, self.products[p_name]._title)
                fnav += '            <ul id="cw-fnav-%s" class="nav navbar-nav side-nav cw-fnav">\n' % p_name
                now_sub = None
                for f_name in self.products[p_name]._forder:
                    if instof(f_name, tuple):
                        m_name, s_name = f_name
                        feature = self.products[p_name][m_name][s_name]
                        if now_sub != None and now_sub != m_name:
                            fnav += '''            </ul></li>
            <li id="cw-fnav-%s_%s" class="ftbar cw-fnavitem"><a href="javascript:;" data-toggle="collapse" data-target="#cw-fsnav-%s-%s" class="collapsed" aria-expanded="false"><i class="fa fa-fw %s"></i> %s <i class="fa fa-fw fa-caret-down"></i></a><ul id="cw-fsnav-%s-%s" class="collapse" aria-expanded="false">
''' % (p_name, m_name, p_name, m_name, self.products[p_name][m_name]._icon, self.products[p_name][m_name]._title, p_name, m_name)
                        if now_sub == None:
                            fnav += '''            <li id="cw-fnav-%s_%s" class="ftbar cw-fnavitem"><a href="javascript:;" data-toggle="collapse" data-target="#cw-fsnav-%s-%s" class="collapsed" aria-expanded="false"><i class="fa fa-fw %s"></i> %s <i class="fa fa-fw fa-caret-down"></i></a><ul id="cw-fsnav-%s-%s" class="collapse" aria-expanded="false">
''' % (p_name, m_name, p_name, m_name, self.products[p_name][m_name]._icon, self.products[p_name][m_name]._title, p_name, m_name)
                        now_sub = m_name
                        fnav += '            <li id="cw-fnav-%s_%s_%s" class="ftbar cw-fnavitem" onclick="show_feature(\'%s\',\'\');"><a><i class="fa fa-fw %s"></i> %s</a></li>' % (p_name, m_name, s_name, feature._code, feature._icon, feature._title)
                        page += '<div id="cw-page-%s_%s_%s" class="cw-page"></div>\n' % (p_name, m_name, s_name)
                        if self.pfm[p_name] == None: self.pfm[p_name] = feature
                        self.pfm[feature._code] = feature
                    else:
                        if now_sub != None:
                            fnav += '            </ul></li>\n'
                            now_sub = None
                        feature = self.products[p_name][f_name]
                        fnav += '            <li id="cw-fnav-%s_%s" class="ftbar cw-fnavitem" onclick="show_feature(\'%s\',\'\');"><a><i class="fa fa-fw %s"></i> %s</a></li>\n' % (p_name, f_name, feature._code, feature._icon, feature._title)
                        page += '<div id="cw-page-%s_%s" class="cw-page"></div>\n' % (p_name, f_name)
                        if self.pfm[p_name] == None: self.pfm[p_name] = feature
                        self.pfm[feature._code] = feature
                if now_sub != None:
                    fnav += '</ul></li>\n'
                fnav += '</ul>\n'
        self.pfm['dashboard'] = self.products.dashboard
            
        self.product_nav_tpl = Template(pnav).render(Context())
        self.feature_nav_tpl = Template(fnav).render(Context())
        self.page_html_tpl = Template(page).render(Context())
        
        self.page_js_products_tpl = Template('var pfm = %s;' % Struct.CODE2JSON(self.pfm)).render(Context())
        self.page_js_tpl = self.ciscowebkit_js_tpl.render({'pfm' : Template('var pfm = %s;' % Struct.CODE2JSON(self.pfm)).render(Context())})
        self.ciscowebkit_build = self.ciscowebkit_tpl.render({'cw_pnav' : self.product_nav_tpl,
                                                              'cw_fnav' : self.feature_nav_tpl,
                                                              'cw_page_html' : self.page_html_tpl,
                                                              'cw_page_js' : self.page_js_tpl})
    
    def __action_method__(self, request, feature, *argv):
        if request.method == 'GET': data = feature.get(request, *argv)
        elif request.method == 'POST': data = feature.post(request, Struct.JSON2DATA(request.body), *argv)
        elif request.method == 'UPDATE': data = feature.update(request, Struct.JSON2DATA(request.body), *argv)
        elif request.method == 'DELETE': data = feature.delete(request, request.body, *argv)
        else: data = self.internal_error_tpl
        data['_id'] = feature._code
        data['_html'] = data.__render__()
        data['_md5'] = str(hashlib.md5(data._html).hexdigest())
        return data
    
    def __action__(self, request):
        paths = filter(None, request.path.split('/'))
        pathlen = len(paths)
        if pathlen > 0:
            if paths[0] == 'dashboard': data = self.__action_method__(request, self.products.dashboard, *paths[1:])
            else:
                feature = self.products[paths[0]]
                if pathlen > 1:
                    feature = feature[paths[1]]
                    if feature._term:
                        if pathlen > 2: data = self.__action_method__(request, feature, *paths[2:])
                        else: data = self.__action_method__(request, feature)
                    elif pathlen > 2:
                        feature = feature[paths[2]]
                        if pathlen > 3: data = self.__action_method__(request, feature, *paths[3:])
                        else: data = self.__action_method__(request, feature)
                    else: data = self.page_not_found_tpl
                else: data = self.page_not_found_tpl
            return HttpResponse(Struct.CODE2JSON(data), content_type="application/json")
        return HttpResponse(self.ciscowebkit_build)
