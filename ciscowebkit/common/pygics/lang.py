'''
Created on 2016. 7. 4.

@author: "comfact"
'''

import re
import sys
import copy
import json
import time
#import gevent
import inspect

# def pygics_patch():
#     from gevent.monkey import patch_all
#     if 'threading' in sys.modules: del sys.modules['threading']
#     patch_all(socket=True,
#               dns=True,
#               time=True,
#               select=True,
#               thread=True,
#               os=True,
#               ssl=True,
#               subprocess=True,
#               sys=True,
#               aggressive=True,
#               Event=True)

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
    elif 'classobj' in t: return 'class'
    elif 'class' in t: return 'class'
    elif 'module' in t: return 'module'
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
    
    def __init__(self, *argv):
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
    
    def __lshift__(self, data):
        self.append(data)
        return self
    
    def __rshift__(self, data):
        if data in self: list.remove(self, data)
        return self
    
    def __add__(self, data):
        if instof(data, list):
            for val in data: self << val
        return self
    
    def __xor__(self, data):
        if data in self: return True
        return False

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