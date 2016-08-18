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
Created on 2016. 7. 4.

@author: "comfact"
'''

import re
import sys
import copy
import json
import time
import inspect
import threading

#===============================================================================
# target of source 
#===============================================================================

def testof(result, predict, label=None):
    if label:
        if result == predict: print 'True  : %s : %s' % (label, str(result)); return True
        else: print 'False : %s : %s' % (label, str(result)); return True
    else:
        if result == predict: return True
        return False

def typeof(obj):
    t = str(type(obj))
    if 'str' in t: return 'string'
    elif 'int' in t: return 'integer'
    elif 'float' in t: return 'float'
    elif 'dict' in t: return 'dict'
    elif 'list' in t: return 'list'
    elif 'tuple' in t: return 'tuple'
    elif 'function' in t: return 'function'
    elif 'instancemethod' in t: return 'method'
    elif 'instance' in t: return 'instance'
    elif 'classmethod' in t: return 'classmethod'
    elif 'classobj' in t: return 'class'
    elif 'class' in t: return 'class'
    elif 'module' in t: return 'module'
    elif 'static' in t: return 'static'
    return 'unknown'

def nameof(obj):
    t = str(type(obj))
    if 'function' in t: return str(obj).split(' ')[1]
    elif 'instancemethod' in t: return str(obj)[:-1].split(' ')[2]
    elif 'instance' in t: return str(obj.__class__)
    elif 'classobj' in t: return str(obj)
    elif 'class' in t: return t[8:-2]
    elif 'module' in t: return str(obj)
    s = str(obj)
    if '<class' in s: return s[8:-2]
    return 'unknown'

def tagof(obj):
    t = str(type(obj))
    if 'function' in t: return str(obj).split(' ')[1]
    elif 'instancemethod' in t: return str(obj)[:-1].split(' ')[2].split('.')[-1]
    elif 'instance' in t: return obj.__class__.__name__
    elif 'classobj' in t: return obj.__name__
    elif 'class' in t: return obj.__class__.__name__
    return 'unknown'

def argof(obj): return inspect.getargspec(obj)[0]

def instof(inst, cls):
    if isinstance(inst, cls): return True
    return False

def classof(cls1, cls2):
    mro = inspect.getmro(cls1)
    for obj in mro:
        if obj == cls2: return True
    return False

#===============================================================================
# source is target
#===============================================================================

def isinst(obj):
    if 'instance' in str(type(obj)): return True
    return False

def isclass(obj):
    if 'classobj' in str(type(obj)): return True
    return False

def iscode(string):
    if re.search('^\w+$', string): return True
    return False

#===============================================================================
# exception handling
#===============================================================================

def catch(__func__, __return__=True, *argv, **kargs):
    try: __func__(*argv, **kargs)
    except: return __return__
    return not __return__

def retch(__func__, __return__=None, *argv, **kargs):
    try: ret = __func__(*argv, **kargs)
    except: return __return__
    return ret

def raising(__catch_ret__, __exception__, *argv, **kargs):
    if not __catch_ret__: raise __exception__(*argv, **kargs)
    
class E(Exception):
    
    def __init__(self, msg):
        Exception.__init__(self)
        self.log_title = nameof(self)
        self.log_time = time.strftime("%Y-%m-%d,%H:%M:%S", time.localtime())
        self.log_msg = msg
        
    def __str__(self):
        return '[%19s|%-7s] %s : %s\n' % (self.log_time, 'EXCEPT', self.log_title, self.log_msg)

#===============================================================================
# global register    
#===============================================================================

def greg(key, obj): __builtins__[key] = obj

def isgreg(key):
    if __builtins__.has_key(key): return True
    return False

def ungreg(key):
    if __builtins__.has_key(key): __builtins__.pop(key)

#===============================================================================
# iteration
#===============================================================================

def iterkey(obj): return obj.iterkeys()

def iterval(obj): return obj.itervalues()

def iterkv(obj): return obj.iteritems()

#===============================================================================
# processing utils
#===============================================================================
        
def clone(src):
    return copy.deepcopy(src)

def exist(obj):
    if len(obj) != 0: return True
    return False

#def sleep(sec): gevent.sleep(sec)

#===============================================================================
# information
#===============================================================================

class Inf(object):
    def __inf__(self): return self.__str__()

def inf(obj):
    if instof(obj, Inf): return obj.__inf__()
    return str(obj)

#===============================================================================
# object handling
#===============================================================================

def C(__class_name__):
    name_path = __class_name__.split('.')
    ref = sys.modules
    for path in name_path:
        if instof(ref, dict): ref = ref[path]
        else: ref = getattr(ref, path)
    return ref

def I(__class_name__, **kargs):
    return C(__class_name__)(**kargs)

class SingleTon:
    
    _SINGLETON_INSTANCE_ = None
    
    @classmethod
    def GET(cls, *argv, **kargs):
        if cls._SINGLETON_INSTANCE_ != None: return cls._SINGLETON_INSTANCE_
        cls._SINGLETON_INSTANCE_ = cls(*argv, **kargs)
        return cls._SINGLETON_INSTANCE_
    
    @classmethod
    def NEW(cls, *argv, **kargs):
        cls._SINGLETON_INSTANCE_ = cls(*argv, **kargs)
        return cls._SINGLETON_INSTANCE_

#===============================================================================
# Data Model
#===============================================================================

class Struct(Inf):
    
    @classmethod
    def __dump_to_list__(cls, l, model_stamp):
        ret = []
        for val in l:
            if instof(val, M):
                d = Struct.__dump_to_dict__(val, model_stamp)
                if model_stamp: d['__m__'] = val.__m__
                ret.append(d)
            elif instof(val, L): ret.append(Struct.__dump_to_list__(val, model_stamp))
            else: ret.append(val)
        return ret
    
    @classmethod
    def __dump_to_dict__(cls, d, model_stamp):
        ret = {}
        for key, val in d.iteritems():
            if instof(val, M):
                ret[key] = Struct.__dump_to_dict__(val, model_stamp)
                if model_stamp: ret[key]['__m__'] = val.__m__
            elif instof(val, L): ret[key] = Struct.__dump_to_list__(val, model_stamp)
            else: ret[key] = val
        if model_stamp: ret['__m__'] = d.__m__
        return ret
    
    @classmethod
    def __build_list_inf__(cls, l, c=0):
        try:
            return json.dumps(l, sort_keys=True, indent=4, separators=(',', ' : '))
        except:
            tstr = ''
            for i in range(0, c): tstr += '  '
            ret = '[\n'
            for val in l:
                if instof(val, dict): val = Struct.__build_dict_inf__(val, c + 1)
                elif instof(val, list): val = Struct.__build_list_inf__(val, c + 1)
                elif instof(val, str) or instof(val, unicode): val = '\"' + val + '\"'
                else: val = str(val)
                ret += '%s  %s,\n' % (tstr, val)
            ret += '%s]' % tstr
            return ret
    
    @classmethod
    def __build_dict_inf__(cls, d, c=0):
        try:
            return json.dumps(d, sort_keys=True, indent=4, separators=(',', ' : '))
        except:
            tstr = ''
            for i in range(0, c): tstr += '  '
            ret = '{\n'
            for key, val in d.iteritems():
                if instof(val, dict): ret += '%s  \"%s\" : %s,\n' % (tstr, key, Struct.__build_dict_inf__(val, c + 1))
                elif instof(val, list): ret += '%s  \"%s\" : %s,\n' % (tstr, key, Struct.__build_list_inf__(val, c + 1))
                elif instof(val, str) or instof(val, unicode): ret += '%s  \"%s\" : \"%s\",\n' % (tstr, key, val)
                else:
                    try: ret += '%s  \"%s\" : %s,\n' % (tstr, key, str(val))
                    except: pass
            ret += '%s}' % tstr
            return ret
    
    @classmethod
    def LOAD(cls, data):
        if instof(data, M) or instof(data, L): return data
        elif instof(data, dict):
            if '__m__' in data: return I(data['__m__'], **data)
            else: return M(**data)
        elif instof(data, list): return L(*data)
        elif instof(data, str) or instof(data, unicode):
            try: code = json.loads(data)
            except Exception as e: print str(e); return None
            return Struct.LOAD(code)
        return None
    
    @classmethod
    def DATA2JSON(cls, data, model_stamp=False):
        if instof(data, M) or instof(data, L): return data.DUMPJSON(model_stamp)
        return Struct.CODE2JSON(data)
    
    @classmethod
    def CODE2JSON(cls, code):
        if instof(code, dict) or instof(code, list):
            try: return json.dumps(code)
            except Exception as e: print str(e)
        return None
    
    @classmethod
    def JSON2DATA(cls, jdata):
        code = Struct.JSON2CODE(jdata)
        if instof(code, dict):
            if '__m__' in code: return I(code['__m__'], **code)
            else: return M(**code)
        elif instof(code, list): return L(*code)
        return None
    
    @classmethod
    def JSON2CODE(cls, jdata):
        try: return json.loads(jdata);
        except Exception as e: print str(e); return None
        
class L(Struct, list):
    
    def __init__(self, *argv, **kargs):
        list.__init__(self)
        for val in argv:
            if instof(val, M) or instof(val, L): self << val
            elif instof(val, dict):
                if '__m__' in val: self << I(val['__m__'], **val)
                else: self << M(**val)
            elif instof(val, list): self << L(*val)
            else: self << val
    
    def DUMP(self, model_stamp=False):
        return Struct.__dump_to_list__(self, model_stamp)
    
    def DUMPJSON(self, model_stamp=False):
        return json.dumps(self.DUMP(model_stamp))
    
    def __inf__(self): return Struct.__build_list_inf__(self)
    
    def __getitem__(self, index):
        try: return list.__getitem__(self, index)
        except: return None
    
    def append(self, data):
        list.append(self, data)
        return self
    
    def __lshift__(self, data):
        list.append(self, data)
        return self
    
    def remove(self, data):
        if data in self: list.remove(self, data)
        return self
    
    def __rshift__(self, data):
        if data in self: list.remove(self, data)
        return self
    
    def merge(self, data):
        if instof(data, list):
            for val in data: self << val
        return self
    
    def __add__(self, data):
        if instof(data, list):
            for val in data: self << val
        return self
    
    def __sub__(self, idx=0):
        self.pop(idx)
        return self
    
class M(Struct, dict):
    
    def __init__(self, **kargs):
        dict.__init__(self)
        self.__m__ = nameof(self)
        for key in kargs:
            if key == '__m__': continue
            val = kargs[key]
            if instof(val, M) or instof(val, L): self[key] = val
            elif instof(val, dict):
                if '__m__' in val: self[key] = I(val['__m__'], **val)
                else: self[key] = M(**val)
            elif instof(val, list): self[key] = L(*val)
            else: self[key] = val
            
    def DUMP(self, model_stamp=False):
        return Struct.__dump_to_dict__(self, model_stamp)
    
    def DUMPJSON(self, model_stamp=False):
        return json.dumps(self.DUMP(model_stamp))
    
    def __inf__(self): return Struct.__build_dict_inf__(self)
    
    def __setitem__(self, key, val):
        dict.__setitem__(self, key, val)
        self.__dict__[key] = val
    
    def __lshift__(self, data):
        if instof(data, dict):
            for k, v in data.iteritems(): self[k] = v
        return self
    
    def __rshift__(self, key):
        if self.has_key(key): self.pop(key); self.__dict__.pop(key)
        return self
    
    def __xor__(self, key):
        if self.has_key(key): return True
        return False
    
class Map(Struct, list):
    
    class X(L):
        
        def __init__(self, x, *data):
            L.__init__(self, *data)
            self.x = x
            self.ye = len(data) - 1
            
    class x(L):
        
        def __init__(self, *data):
            L.__init__(self, *data)
            self.ye = len(data) - 1
            
    class Y(L):
        
        def __init__(self, y, *data):
            L.__init__(self, *data)
            self.y = y
            self.xe = len(data) - 1
            
    class y(L):
        
        def __init__(self, *data):
            L.__init__(self, *data)
            self.xe = len(data) - 1
    
    class XY:
        
        def __init__(self, x, y, data):
            self.x = x
            self.y = y
            self.data = data
    
    def __init__(self):
        list.__init__(self)
        self._x_xaxis_ = -1
        self._x_yaxis_ = -1
        
    def DUMP(self, model_stamp=False):
        return Struct.__dump_to_list__(self, model_stamp)
    
    def DUMPJSON(self, model_stamp=False):
        return json.dumps(self.DUMP(model_stamp))
    
    def rotate(self):
        xy = Map()
        
        xy.__addEmpty__(self._x_yaxis_, self._x_xaxis_)
        for i in range(self._x_xaxis_ + 1):
            for j in range(self._x_yaxis_ + 1):
                xy[j][i] = self[i][j]
        return xy
    
    def __inf__(self):
        bstr = '-'
        for i in range(0, self._x_xaxis_ + 1): bstr += '---------'
        bstr += '\n'
        pstr = bstr
        for y in range(0, self._x_yaxis_ + 1):
            pstr += '|'
            for x in range(0, self._x_xaxis_ + 1):
                d = self[x][y]
                if d == None: pstr += '        |'
                else: pstr += '%-8s|' % str(d)
            else:
                pstr += '\n' + bstr
        return pstr
    
    def __addEmpty__(self, x, y):
        if x > self._x_xaxis_:
            for i in range(self._x_xaxis_, x):
                self.append(list())
                for j in range(0, self._x_yaxis_ + 1):
                    self[-1].append(None)
            self._x_xaxis_ = x
        if y > self._x_yaxis_:
            for d in self:
                for i in range(self._x_yaxis_, y):
                    d.append(None)
            self._x_yaxis_ = y
            
    def __addy__(self, data):
        if self._x_xaxis_ == data.xe:
            for i in range(0, self._x_xaxis_ + 1):
                self[i].append(data[i])
        if self._x_xaxis_ > data.xe:
            for i in range(0, self._x_xaxis_ + 1):
                if i > data.xe: d = None
                else: d = data[i]
                self[i].append(d)
        elif self._x_xaxis_ < data.xe:
            self.__addEmpty__(data.xe, self._x_yaxis_)
            for i in range(0, self._x_xaxis_ + 1):
                self[i].append(data[i])
        self._x_yaxis_ += 1
        
    def __addx__(self, data):
        if self._x_yaxis_ == data.ye:
            self.append(data)
        elif self._x_yaxis_ > data.ye:
            self.append(data)
            for i in range(data.ye, self._x_yaxis_): self[-1].append(None)
        elif self._x_yaxis_ < data.ye:
            self.__addEmpty__(self._x_xaxis_, data.ye)
            self.append(data)
        self._x_xaxis_ += 1
    
    def __addY__(self, data):
        self.__addEmpty__(data.xe, data.y)
        for i in range(data.xe + 1):
            self[i][data.y] = data[i]
            
    def __addX__(self, data):
        self.__addEmpty__(data.x, data.ye)
        for i in range(data.ye + 1):
            self[data.x][i] = data[i]
            
    def __addXY__(self, x, y, data):
        self.__addEmpty__(x, y)
        self[x][y] = data
        
    def __lshift__(self, data):
        if instof(data, Map.y): self.__addy__(data)
        elif instof(data, Map.x): self.__addx__(data)
        elif instof(data, Map.Y): self.__addY__(data)
        elif instof(data, Map.X): self.__addX__(data)
        elif instof(data, tuple): self.__addXY__(*data)
        elif instof(data, Map.XY): self.__addXY__(data.x, data.y, data.data)
        return self
    
class Meta(L):
    
    def __init__(self, *argv):
        L.__init__(self, *argv)
    
    def __encode__(self, data):
        return data
    
    def __decode__(self, data):
        return data
    
    def __call__(self, index):
        try: return list.__getitem__(self, index)
        except: return None
    
    def __getitem__(self, index):
        try: return self.__decode__(list.__getitem__(self, index))
        except: return None
    
    def __iter__(self, *args, **kwargs):

        class Liter:
            
            def __init__(self, ldata):
                self.ldata = ldata
                self.idx = 0
                self.llen = len(ldata)
                
            def __iter__(self, *args, **kwargs):
                return self
            
            def next(self):
                if self.idx < self.llen:
                    ret = self.ldata[self.idx]
                    self.idx += 1
                    return ret
                else: raise StopIteration()
                
        return Liter(self)
    
    def append(self, data):
        list.append(self, self.__encode__(data))
        return self
    
    def __lshift__(self, data):
        list.append(self, self.__encode__(data))
        return self
    
    def remove(self, data):
        f = None
        for i in range(len(self)):
            if data == self.__decode__(self(i)):
                f = self(i); break
        if f: list.remove(self, f)
        return self
    
    def __rshift__(self, data):
        f = None
        for i in range(len(self)):
            if data == self.__decode__(self(i)):
                f = self(i); break
        if f: list.remove(self, f)
        return self

class Table(M):
    
    class R(Map.y):
        
        def __init__(self, *col):
            Map.y.__init__(self, *col)
            
        def __meta__(self, data):
            return data
        
        def append(self, data):
            Map.y.append(self, self.__meta__(data))
            return self
        
        def __lshift__(self, data):
            Map.y.append(self, self.__meta__(data))
            return self
    
    def __init__(self, *head):
        M.__init__(self, head=L(*head), records=Map())
        
    def __lshift__(self, record):
        self.records << record
        return self

#===============================================================================
# Task
#===============================================================================

class Task:
    
    class Worker(threading.Thread):
        
        def __init__(self, task):
            threading.Thread.__init__(self)
            self.task = task
            
        def run(self):
            if self.task._task_delay > 0: time.sleep(self.task._task_delay)
            while self.task._task_active == True:
                if self.task._task_tick > 0: start_time = time.time()
                try:
                    self.task.task()
                except Exception as e:
                    self.task._task_active = False
                    print str(e)
                    break
                if self.task._task_tick > 0:
                    end_time = time.time()
                    sleep_time = self.task._task_tick - (end_time - start_time)
                    if sleep_time > 0: time.sleep(sleep_time)
    
    def __init__(self, tick=0, delay=0):
        self._task_tick = tick
        self._task_delay = delay
        self._task_active = False
        self._task_worker = Task.Worker(self)
        
    def task(self):
        pass
        
    def start(self):
        if self._task_active == False:
            self._task_active = True
            self._task_worker.start()
    
    def stop(self):
        if self._task_active == True:
            self._task_active = False
            self._task_worker._Thread__stop()
            self._task_worker.join()

class Mutex:
    
    def __init__(self):
        self._lock = threading.Lock()
    
    def lock(self): self._lock.acquire()
    
    def unlock(self): self._lock.release()
        
