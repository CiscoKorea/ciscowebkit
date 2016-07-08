'''
Created on 2016. 7. 5.

@author: "comfact"
'''

import os

from django.template import Template, Context, loader
from django.http import HttpResponse

from ciscowebkit.common.pygics import instof, classof, nameof, tagof, iterkv, iterval, inf
from ciscowebkit.common.pygics import SingleTon, L, M
from ciscowebkit.common.pygics import Module, NameSpace, Dir

from ciscowebkit.common import Feature, __Default_Feature__, Overview, Setting

from ciscowebkit.product import PRODUCT_ORDER


class Manager(SingleTon):
    
    def __init__(self):
        self.__load_templates__()
        self.__load_features__()
        
        print 'PRODUCTS      :', inf(self.products)
        print 'PRODUCT ORDER :', self.product_order
        
    def action(self, request):
        paths = filter(None, request.path.split('/'))
        pathlen = len(paths)
        p_name = paths[0]
        
#         try:
        if pathlen == 1:
            feature = self.products[p_name].overview
            try: view = feature.__obj__.action(request)
            except: HttpResponse(self.internal_error_tpl)
            return HttpResponse(self.render_feature(p_name, 'overview', feature.__view__, feature.__desc__, view, None))
        elif pathlen == 2:
            f_name = paths[1]
            feature = self.products[p_name][f_name]
            try: view = feature.__obj__.action(request)
            except: HttpResponse(self.internal_error_tpl)
            return HttpResponse(self.render_feature(p_name, f_name, feature.__view__, feature.__desc__, view, None))
        elif pathlen == 3:
            f_name = paths[1]
            s_name = paths[2]
            feature = self.products[p_name][f_name][s_name]
            try: view = feature.__obj__.action(request)
            except: HttpResponse(self.internal_error_tpl)
            return HttpResponse(self.render_feature(p_name, (f_name, s_name), feature.__view__, feature.__desc__, view, None))
        else:
            return HttpResponse(self.page_not_found_tpl)
#         except:
#             return HttpResponse(self.page_not_found_tpl)

    def render_feature(self, p_name, f_name, title, desc, view, status):
        
        products = ''
        for p in self.product_order:
            if p in self.products:
                if p == p_name: products += self.products[p].__link__ # ACTIVE
                else: products += self.products[p].__link__
        
        features = ''
        nowsub = None
        for f in self.products[p_name].__fo__:
            if instof(f, tuple):
                if nowsub == None:
                    if f == f_name: features += '<li class="active"><a href="javascript:;" data-toggle="collapse" data-target="#%s"><i class="fa fa-fw fa-arrows-v"></i> %s <i class="fa fa-fw fa-caret-down"></i></a><ul id="%s" class="collapse">' % (f[0], f[0], f[0])
                    else: features += '<li><a href="javascript:;" data-toggle="collapse" data-target="#%s"><i class="fa fa-fw fa-arrows-v"></i> %s <i class="fa fa-fw fa-caret-down"></i></a><ul id="%s" class="collapse">' % (f[0], f[0], f[0])
                    nowsub = f[0]
                elif nowsub != None and nowsub != f[0]:
                    features += '</ul></li>'
                    if f == f_name: features += '<li class="active"><a href="javascript:;" data-toggle="collapse" data-target="#%s"><i class="fa fa-fw fa-arrows-v"></i> %s <i class="fa fa-fw fa-caret-down"></i></a><ul id="%s" class="collapse">' % (f[0], f[0], f[0])
                    else: features += '<li><a href="javascript:;" data-toggle="collapse" data-target="#%s"><i class="fa fa-fw fa-arrows-v"></i> %s <i class="fa fa-fw fa-caret-down"></i></a><ul id="%s" class="collapse">' % (f[0], f[0], f[0])
                    nowsub = f[0]
                features += '<li>' + self.products[p_name][f[0]][f[1]].__link__ + '</li>'
            else:
                if nowsub != None:
                    features += '</ul></li>'
                    nowsub = None
                if f == f_name: features += '<li class="active">' + self.products[p_name][f].__link__ + '</li>'
                else: features += '<li>' + self.products[p_name][f].__link__ + '</li>'
        
        return self.feature_tpl.render({'products' : Template(products).render(Context()),
                                        'features' : Template(features).render(Context()),
                                        'status' : self.status_tpl.render(),
                                        'title' : title,
                                        'desc' : desc,
                                        'view' : view})
    
    def render_dashboard(self, widgets, status):
        products = ''
        for p in self.product_order:
            if p in self.products:
                products += self.products[p].__link__
        
        return self.dashboard_tpl.render({'products' : Template(products).render(Context()),
                                          'status' : self.status_tpl.render(),
                                          'widgets' : widgets})
        
    
    def __load_templates__(self):
        self.dashboard_tpl = loader.get_template('dashboard.html')
        self.feature_tpl = loader.get_template('feature.html')
        self.status_tpl = loader.get_template('status.html')
        self.page_not_found_tpl = Template('<h1>Page Not Found</h1>').render(Context())
        self.internal_error_tpl = Template('<h1>Internal Error</h1>').render(Context())
        
    def __load_features__(self):
        
        self.products = M()
        self.product_order = L()
        for po in PRODUCT_ORDER: self.product_order << po.lower()
        
        p_paths = Dir.showall('ciscowebkit/product/')
        for p_path in p_paths:
            if not Dir.isDir(p_path) or not Dir.isDir(p_path + '/feature'): continue
            if not Dir.isDir(p_path + '/feature'): continue
            p_r_name = os.path.split(p_path)[-1]
            p_name = p_r_name.lower()
            p_view = p_r_name.replace('_', ' ')
            p_url = '/' + p_name + '/'
            self.products[p_name] = M()
            self.products[p_name]['__view__'] = p_view
            self.products[p_name]['__url__'] = p_url
            self.products[p_name]['__link__'] = '<a class="navbar-brand" href="%s">%s</a>' % (p_url, p_view)
            
            # Add-on Feature
            features = NameSpace(p_path + '/feature', inherited=nameof(Feature), force=True)
            for f_r_name, f_mod in iterkv(features):
                f_name = f_r_name.lower()
                f_view = f_r_name.replace('_', ' ')
                f_url = p_url + f_name + '/'
                self.products[p_name][f_name] = M()
                self.products[p_name][f_name]['__view__'] = f_view
                self.products[p_name][f_name]['__url__'] = f_url
                
                if len(f_mod) > 1: # Sub Feature
                    self.products[p_name][f_name]['__type__'] = 'sub'
                    for s_r_name, s_cls in iterkv(f_mod):
                        s_name = s_r_name.lower()
                        s_view = s_r_name.replace('_', ' ')
                        s_url = f_url + s_name + '/'
                        self.products[p_name][f_name][s_name] = M()
                        self.products[p_name][f_name][s_name]['__view__'] = s_view
                        self.products[p_name][f_name][s_name]['__url__'] = s_url
                        self.products[p_name][f_name][s_name]['__obj__'] = s_cls.NEW()
                        self.products[p_name][f_name][s_name]['__icon__'] = s_cls.ICON
                        self.products[p_name][f_name][s_name]['__link__'] = '<a href="%s"><i class="%s"></i> %s</a>' % (s_url, s_cls.ICON, s_view)
                        if s_cls.__doc__ != None: self.products[p_name][f_name][s_name]['__desc__'] = ' : ' + s_cls.__doc__
                        if s_cls.__doc__ == None: self.products[p_name][f_name][s_name]['__desc__'] = ''
                else:
                    for s_cls in iterval(f_mod):
                        self.products[p_name][f_name]['__type__'] = 'single'
                        self.products[p_name][f_name]['__obj__'] = s_cls.NEW()
                        self.products[p_name][f_name]['__desc__'] = s_cls.__doc__
                        self.products[p_name][f_name]['__icon__'] = s_cls.ICON
                        self.products[p_name][f_name]['__link__'] = '<a href="%s"><i class="%s"></i> %s</a>' % (f_url, s_cls.ICON, f_view)
                        if s_cls.__doc__ != None: self.products[p_name][f_name]['__desc__'] = ' : ' + s_cls.__doc__
                        if s_cls.__doc__ == None: self.products[p_name][f_name]['__desc__'] = ''
            
            # Ordering
            def_mod = Module(p_path + '/feature/__init__.py', force=True)
            self.products[p_name]['__fo__'] = L()
            self.products[p_name].__fo__ << 'overview'
            for fo in def_mod.FEATURE_ORDER:
                if '.' in fo: self.products[p_name].__fo__ << (fo.lower().split('.')[0], fo.lower().split('.')[1])
                else: self.products[p_name].__fo__ << fo.lower()
            self.products[p_name].__fo__ << 'setting'
            
            # Add Overview & Setting
            def_mod = Module(p_path + '/feature/__init__.py', inherited=nameof(__Default_Feature__), force=True)
            for f_cls in iterval(def_mod):
                if classof(f_cls, Overview) and nameof(f_cls) != nameof(Overview):
                    self.products[p_name]['overview'] = M()
                    self.products[p_name]['overview']['__type__'] = 'single'
                    self.products[p_name]['overview']['__view__'] = 'Overview'
                    self.products[p_name]['overview']['__url__'] = p_url + 'overview/'
                    self.products[p_name]['overview']['__obj__'] = f_cls.NEW()
                    self.products[p_name]['overview']['__icon__'] = f_cls.ICON
                    self.products[p_name]['overview']['__link__'] = '<a href="%s"><i class="%s"></i> %s</a>' % (p_url + 'overview/', f_cls.ICON, 'Overview')
                    if f_cls.__doc__ != None: self.products[p_name]['overview']['__desc__'] = ' : ' + f_cls.__doc__
                    if f_cls.__doc__ == None: self.products[p_name]['overview']['__desc__'] = ''
                elif classof(f_cls, Setting) and nameof(f_cls) != nameof(Setting):
                    self.products[p_name]['setting'] = M()
                    self.products[p_name]['setting']['__type__'] = 'single'
                    self.products[p_name]['setting']['__view__'] = 'Setting'
                    self.products[p_name]['setting']['__url__'] = p_url + 'setting/'
                    self.products[p_name]['setting']['__obj__'] = f_cls.NEW()
                    self.products[p_name]['setting']['__icon__'] = f_cls.ICON
                    self.products[p_name]['setting']['__link__'] = '<a href="%s"><i class="%s"></i> %s</a>' % (p_url + 'setting/', f_cls.ICON, 'Setting')
                    if f_cls.__doc__ != None: self.products[p_name]['setting']['__desc__'] = ' : ' + f_cls.__doc__
                    if f_cls.__doc__ == None: self.products[p_name]['setting']['__desc__'] = ''
                