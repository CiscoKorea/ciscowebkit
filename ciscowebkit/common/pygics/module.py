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

'''
Created on 2016. 7. 5.

@author: "comfact"
'''

import os
import re
import imp
import inspect

from ciscowebkit.common.pygics.lang import nameof, typeof, instof, L, M
from ciscowebkit.common.pygics.system import Dir

class Module(M):
    
    _PYGICS_RESERVED_KEY_ = ['__builtins__', '__file__', '__package__', '__name__', '__doc__',
                             'pygics_patch', 'testof', 'typeof', 'nameof', 'tagof', 'argof', 'instof', 'classof', 'isinst', 'isclass', 'iscode',
                             'catch', 'retch', 'raising', 'clone', 'C', 'I', 'Inf', 'inf',
                             'iterkey', 'iterval', 'iterkv', 'sleep', 'greg', 'isgreg', 'ungreg', 'exist']
    
    _PYGICS_MODULE_GLOVAL_MAP_ = {}
    
    def __init__(self, file_path, ident=None, inherited=None, force=False, **kargs):
        M.__init__(self, **kargs)
        self._module_desc_ = M()
        self._module_desc_['path'] = file_path
        self._module_desc_['ident'] = ident
        self._module_desc_['inherited'] = inherited
        
        if os.path.exists(file_path):
            self._module_desc_['name'], self._module_desc_['ext'] = os.path.splitext(os.path.split(file_path)[-1])
            if force == False and file_path in Module._PYGICS_MODULE_GLOVAL_MAP_: data = Module._PYGICS_MODULE_GLOVAL_MAP_[file_path]
            else:
                if self._module_desc_['ext'].lower() == '.py':
                    Module._PYGICS_MODULE_GLOVAL_MAP_[file_path] = imp.load_source(self._module_desc_['name'], file_path)
                    data =  Module._PYGICS_MODULE_GLOVAL_MAP_[file_path]
                elif self._module_desc_['ext'].lower() == '.pyc':
                    Module._PYGICS_MODULE_GLOVAL_MAP_[file_path] = imp.load_compiled(self._module_desc_['name'], file_path)
                    data =  Module._PYGICS_MODULE_GLOVAL_MAP_[file_path]
                else: data = None
            if data:
                if self._module_desc_.ident:
                    if not instof(self._module_desc_.ident, list): self._module_desc_['ident'] = L(self._module_desc_.ident)
                if self._module_desc_.inherited:
                    if not instof(self._module_desc_.inherited, list): self._module_desc_['inherited'] = L(self._module_desc_.inherited)
                if self._module_desc_.ident != None or self._module_desc_.inherited != None:
                    for name in data.__dict__:
                        element = data.__dict__[name]
                        elem_name = nameof(element)
                        if hasattr(element, '__bases__'):
                            elem_match = True
                            if self._module_desc_.ident != None:
                                if elem_name not in self._module_desc_.ident: elem_match = False
                            if self._module_desc_.inherited != None:
                                mro = inspect.getmro(element)
                                for obj in mro:
                                    if nameof(obj) in self._module_desc_.inherited and elem_name not in self._module_desc_.inherited: break
                                else: elem_match = False
                            if elem_match:
                                if name not in self: self[name] = element
                        elif self._module_desc_.inherited == None:
                            if elem_name in self._module_desc_.ident:
                                if name not in self: self[name] = element
                else:
                    for name in data.__dict__:
                        element = data.__dict__[name]
                        if hasattr(element, '__bases__'):
                            if re.search('^%s[\.w+]+' % self._module_desc_.name, nameof(element)):
                                if name not in self: self[name] = element
                        elif typeof(element) != 'module' and name not in Module._PYGICS_RESERVED_KEY_:
                            if name not in self: self[name] = element
                            
class NameSpace(M):
    
    def __init__(self, ns_path, ident=None, inherited=None, force=False, **kargs):
        M.__init__(self, **kargs)
        self._namespace_desc_ = M()
        self._namespace_desc_['name'] = os.path.split(ns_path)[-1]
        self._namespace_desc_['path'] = ns_path
        self._namespace_desc_['ident'] = ident
        self._namespace_desc_['inherited'] = inherited
        if os.path.exists(ns_path):
            flist = Dir.show(ns_path, '*.py')
            for fname in flist:
                module = Module(fname, ident, inherited, force)
                if len(module) > 0: self[module._module_desc_.name] = module

class WorkSpace(M):
    
    def __init__(self, work_path, ident=None, inherited=None, force=False, **kargs):
        M.__init__(self, **kargs)
        self._workspace_desc_ = M()
        self._workspace_desc_['path'] = work_path
        self._workspace_desc_['ident'] = ident
        self._workspace_desc_['inherited'] = inherited
        if os.path.exists(work_path):
            dlist = Dir.showall(work_path)
            for dname in dlist:
                ns_path = work_path + '/' + dname
                if Dir.isDir(ns_path):
                    ns = NameSpace(ns_path, ident, inherited, force, **kargs)
                    if len(ns) > 0: self[ns._namespace_desc_.name] = ns
