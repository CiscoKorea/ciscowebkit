'''
Created on 2016. 7. 5.

@author: "comfact"
'''

import os

from django.template import Template, Context, loader
from django.http import HttpResponse

from ciscowebkit.common.pygics import instof, classof, nameof, iterkv, iterval, inf
from ciscowebkit.common.pygics import SingleTon, L, M
from ciscowebkit.common.pygics import Module, NameSpace, Dir

from ciscowebkit.common import FeatureInterface, Feature, SubFeature, Overview, Setting

from ciscowebkit.product import PRODUCT_ORDER

class Manager(SingleTon):
    
    class ViewData(M):
        
        def __init__(self):
            M.__init__(self)
            self['title'] = ''
            self['icon'] = 'fa-database'
            
        def setTitle(self, title='', icon='fa-database'):
            self['title'] = title
            self['icon'] = icon
            
    class TableData(ViewData):

        def __init__(self):
            Manager.ViewData.__init__(self)
            self['head'] = L()
            self['datas'] = L()
        
        def setHead(self, *argv):
            self['head'] = L(*argv)
            
        def addData(self, *argv, **kargs):
            option = M(css='')
            if 'type' in kargs: option['css'] = kargs['type']
            self.datas << M(record=argv, option=option)
    
    @classmethod
    def render(cls, data):
        if instof(data, Manager.TableData):
            return cls.GET().table_tpl.render({'title':data.title,'icon':data.icon,'head':data.head, 'datas':data.datas})
        return cls.GET().internal_error_tpl
    
    def __init__(self):
        self.__load_templates__()
        self.__load_features__()
        
        print inf(M(products=self.products, order=self.product_order))
    
    def __load_templates__(self):
        self.dashboard_tpl = loader.get_template('dashboard.html')
        self.feature_tpl = loader.get_template('feature.html')
        self.status_tpl = loader.get_template('status.html')
        
        self.table_tpl = loader.get_template('elements/table.html')
        
        self.page_not_found_tpl = Template('<h1>Page Not Found</h1>').render(Context())
        self.internal_error_tpl = Template('<h1>Internal Error</h1>').render(Context())
    
    def __action_method__(self, request, obj):
        if request.method == 'GET': view = obj.get(request)
        elif request.method == 'POST': view = obj.post(request)
        elif request.method == 'UPDATE': view = obj.update(request)
        elif request.method == 'DELETE': view = obj.delete(request)
        else: view = self.internal_error_tpl
        return view
    
    def __action_default__(self, request):
        paths = filter(None, request.path.split('/'))
        pathlen = len(paths)
        p_name = paths[0]
        
        try:
            if pathlen == 1:
                feature = self.products[p_name].overview
                try: view = self.__action_method__(request, feature.__obj__)
                except: return HttpResponse(self.internal_error_tpl)
                return HttpResponse(self.__render_feature__(p_name, 'overview', feature.__view__, feature.__desc__, view, None))
            elif pathlen == 2:
                f_name = paths[1]
                feature = self.products[p_name][f_name]
                try: view = self.__action_method__(request, feature.__obj__)
                except: return HttpResponse(self.internal_error_tpl)
                return HttpResponse(self.__render_feature__(p_name, f_name, feature.__view__, feature.__desc__, view, None))
            elif pathlen == 3:
                f_name = paths[1]
                s_name = paths[2]
                feature = self.products[p_name][f_name][s_name]
                try: view = self.__action_method__(request, feature.__obj__)
                except: return HttpResponse(self.internal_error_tpl)
                return HttpResponse(self.__render_feature__(p_name, (f_name, s_name), feature.__view__, feature.__desc__, view, None))
            else:
                return HttpResponse(self.page_not_found_tpl)
        except:
            return HttpResponse(self.page_not_found_tpl)
    
    def __action_debug__(self, request):
        paths = filter(None, request.path.split('/'))
        pathlen = len(paths)
        p_name = paths[0]
        
        if pathlen == 1:
            feature = self.products[p_name].overview
            view = self.__action_method__(request, feature.__obj__)
            return HttpResponse(self.__render_feature__(p_name, 'overview', feature.__view__, feature.__desc__, view, None))
        elif pathlen == 2:
            f_name = paths[1]
            feature = self.products[p_name][f_name]
            view = self.__action_method__(request, feature.__obj__)
            return HttpResponse(self.__render_feature__(p_name, f_name, feature.__view__, feature.__desc__, view, None))
        elif pathlen == 3:
            f_name = paths[1]
            s_name = paths[2]
            feature = self.products[p_name][f_name][s_name]
            view = self.__action_method__(request, feature.__obj__)
            return HttpResponse(self.__render_feature__(p_name, (f_name, s_name), feature.__view__, feature.__desc__, view, None))
        else:
            return HttpResponse(self.page_not_found_tpl)

    def __render_feature__(self, p_name, f_name, title, desc, view, status):
        
        products = ''
        for p in self.product_order:
            if p in self.products:
                if p == p_name: products += '<a class="navbar-product-active" href="%s">%s</a>' % (self.products[p].__url__, self.products[p].__view__)
                else: products += '<a class="navbar-product" href="%s">%s</a>' % (self.products[p].__url__, self.products[p].__view__)
                
        if instof(f_name, tuple):
            s_name = f_name[1]
            m_name = f_name[0]
        else:
            s_name = None
            m_name = f_name
        
        features = ''
        nowsub = None
        for f in self.products[p_name].__fo__:
            if instof(f, tuple):
                if nowsub == None:
                    if f[0] == m_name: features += '<li class="active"><a href="javascript:;" data-toggle="collapse" data-target="#%s" class aria-expanded="true"><i class="fa fa-fw %s"></i> %s <i class="fa fa-fw fa-caret-down"></i></a><ul id="%s" class="collapse in" aria-expanded="true">' % (f[0], self.products[p_name][f[0]].__icon__, self.products[p_name][f[0]].__view__, f[0])
                    else: features += '<li><a href="javascript:;" data-toggle="collapse" data-target="#%s" class="collapsed" aria-expanded="false"><i class="fa fa-fw %s"></i> %s <i class="fa fa-fw fa-caret-down"></i></a><ul id="%s" class="collapse" aria-expanded="false">' % (f[0], self.products[p_name][f[0]].__icon__, self.products[p_name][f[0]].__view__, f[0])
                    nowsub = f[0]
                elif nowsub != None and nowsub != f[0]:
                    if f[0] == m_name: features += '</ul></li><li class="active"><a href="javascript:;" data-toggle="collapse" data-target="#%s" class aria-expanded="true"><i class="fa fa-fw %s"></i> %s <i class="fa fa-fw fa-caret-down"></i></a><ul id="%s" class="collapse in" aria-expanded="true">' % (f[0], self.products[p_name][f[0]].__icon__, self.products[p_name][f[0]].__view__, f[0])
                    else: features += '</ul></li><li><a href="javascript:;" data-toggle="collapse" data-target="#%s" class="collapsed" aria-expanded="false"><i class="fa fa-fw %s"></i> %s <i class="fa fa-fw fa-caret-down"></i></a><ul id="%s" class="collapse" aria-expanded="false">' % (f[0], self.products[p_name][f[0]].__icon__, self.products[p_name][f[0]].__view__, f[0])
                    nowsub = f[0]
                if f[1] == s_name: features += '<li class="active">' + self.products[p_name][f[0]][f[1]].__link__ + '</li>'
                else: features += '<li>' + self.products[p_name][f[0]][f[1]].__link__ + '</li>'
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
    
    def __render_dashboard__(self, widgets, status):
        products = ''
        for p in self.product_order:
            if p in self.products:
                products += self.products[p].__link__
        
        return self.dashboard_tpl.render({'products' : Template(products).render(Context()),
                                          'status' : self.status_tpl.render(),
                                          'widgets' : widgets})
        
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
                
                for cls_r_name, cls_obj in iterkv(f_mod):
                    
                    print cls_r_name,
                    
                    if classof(cls_obj, SubFeature):
                        print 'SubFeature'
                        cls_name = cls_r_name.lower()
                        cls_view = cls_r_name.replace('_', ' ')
                        cls_url = f_url + cls_name + '/'
                        self.products[p_name][f_name][cls_name] = M()
                        self.products[p_name][f_name][cls_name]['__view__'] = cls_view
                        self.products[p_name][f_name][cls_name]['__url__'] = cls_url
                        self.products[p_name][f_name][cls_name]['__obj__'] = cls_obj.NEW()
                        self.products[p_name][f_name][cls_name]['__icon__'] = cls_obj.GET()._icon_
                        self.products[p_name][f_name][cls_name]['__link__'] = '<a href="%s"><i class="fa fa-fw %s"></i> %s</a>' % (cls_url, cls_obj.GET()._icon_, cls_view)
                        if cls_obj.__doc__ != None: self.products[p_name][f_name][cls_name]['__desc__'] = ' ' + cls_obj.__doc__
                        if cls_obj.__doc__ == None: self.products[p_name][f_name][cls_name]['__desc__'] = ''
                    else:
                        print 'MainFeature'
                        self.products[p_name][f_name]['__obj__'] = cls_obj.NEW()
                        self.products[p_name][f_name]['__icon__'] = cls_obj.GET()._icon_
                        self.products[p_name][f_name]['__link__'] = '<a href="%s"><i class="fa fa-fw %s"></i> %s</a>' % (f_url, cls_obj.GET()._icon_, f_view)
                        if cls_obj.__doc__ != None: self.products[p_name][f_name]['__desc__'] = ' : ' + cls_obj.__doc__
                        if cls_obj.__doc__ == None: self.products[p_name][f_name]['__desc__'] = ''
            
            # Ordering
            def_mod = Module(p_path + '/feature/__init__.py', force=True)
            self.products[p_name]['__fo__'] = L()
            self.products[p_name].__fo__ << 'overview'
            for fo in def_mod.FEATURE_ORDER:
                if '.' in fo: self.products[p_name].__fo__ << (fo.lower().split('.')[0], fo.lower().split('.')[1])
                else: self.products[p_name].__fo__ << fo.lower()
            self.products[p_name].__fo__ << 'setting'
            
            # Add Overview & Setting
            def_mod = Module(p_path + '/feature/__init__.py', inherited=nameof(FeatureInterface), force=True)
            for f_cls in iterval(def_mod):
                if classof(f_cls, Overview) and nameof(f_cls) != nameof(Overview):
                    self.products[p_name]['overview'] = M()
                    self.products[p_name]['overview']['__view__'] = 'Overview'
                    self.products[p_name]['overview']['__url__'] = p_url + 'overview/'
                    self.products[p_name]['overview']['__obj__'] = f_cls.NEW()
                    self.products[p_name]['overview']['__icon__'] = f_cls.GET()._icon_
                    self.products[p_name]['overview']['__link__'] = '<a href="%s"><i class="fa fa-fw %s"></i> %s</a>' % (p_url + 'overview/', f_cls.GET()._icon_, 'Overview')
                    if f_cls.__doc__ != None: self.products[p_name]['overview']['__desc__'] = ' : ' + f_cls.__doc__
                    if f_cls.__doc__ == None: self.products[p_name]['overview']['__desc__'] = ''
                elif classof(f_cls, Setting) and nameof(f_cls) != nameof(Setting):
                    self.products[p_name]['setting'] = M()
                    self.products[p_name]['setting']['__view__'] = 'Setting'
                    self.products[p_name]['setting']['__url__'] = p_url + 'setting/'
                    self.products[p_name]['setting']['__obj__'] = f_cls.NEW()
                    self.products[p_name]['setting']['__icon__'] = f_cls.GET()._icon_
                    self.products[p_name]['setting']['__link__'] = '<a href="%s"><i class="fa fa-fw %s"></i> %s</a>' % (p_url + 'setting/', f_cls.GET()._icon_, 'Setting')
                    if f_cls.__doc__ != None: self.products[p_name]['setting']['__desc__'] = ' : ' + f_cls.__doc__
                    if f_cls.__doc__ == None: self.products[p_name]['setting']['__desc__'] = ''
