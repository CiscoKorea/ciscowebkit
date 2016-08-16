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
import sys
import time
import glob
import shutil
import hashlib
import datetime
import subprocess
from socket import gethostname

class Time:
    
    @classmethod
    def stamp(cls): return time.strftime("%Y-%m-%d,%H:%M:%S", time.localtime())
    
    @classmethod
    def numeric_stamp(cls): return int(time.time())
    
class Env:
    
    @classmethod
    def isWindows(cls):
        if sys.platform.startswith('win'): return True
        return False
    
    @classmethod
    def isLinux(cls):
        if sys.platform.startswith('linux'): return True
        return False
    
    @classmethod
    def getHostName(cls): return gethostname()
    
class Console:
     
    _SCREEN_ = sys.stdout
     
    @classmethod
    def waitkey(cls, show='BREAK!! press any key> '): raw_input(show)
     
    @classmethod
    def get(cls, show='INPUT> '): return raw_input(show)
     
    @classmethod
    def setScrOut(cls): sys.stdout = Console._SCREEN_
 
    @classmethod
    def setFileOut(cls, path): sys.stdout = open(path, 'a')
        
class Dir:
    
    @classmethod
    def create(cls, path):
        if not os.path.exists(path): os.mkdir(path)
        
    @classmethod
    def delete(cls, path):
        if os.path.exists(path): shutil.rmtree(path)
            
    @classmethod
    def move(cls, src, dst):
        if os.path.exists(src): shutil.move(src, dst)
    
    @classmethod
    def copy(cls, src, dst):
        if os.path.exists(src): shutil.copytree(src, dst)
        
    @classmethod
    def exist(cls, path): return os.path.exists(path)
    
    @classmethod
    def show(cls, path, ext='*'):
        if os.path.exists(path): return glob.glob(path + '/' + ext)
        return []
    
    @classmethod
    def showall(cls, path):
        if os.path.exists(path): return glob.glob(path + '/*')
        return []
    
    @classmethod
    def isDir(cls, path): return os.path.isdir(path)
    
    @classmethod
    def isFile(cls, path): return os.path.isfile(path)

class File:
    
    @classmethod
    def create(cls, path):
        if not os.path.exists(path): open(path, 'w').close()
    
    @classmethod
    def delete(cls, path):
        if os.path.exists(path): os.remove(path)
            
    @classmethod
    def move(cls, src, dst):
        if os.path.exists(src): shutil.move(src, dst)
    
    @classmethod
    def copy(cls, src, dst):
        if os.path.exists(src): shutil.copy2(src, dst)
    
    @classmethod
    def exist(cls, path): return os.path.exists(path)
    
    @classmethod
    def getDesc(cls, file_path):
        spath = os.path.split(file_path)
        path = spath[0]
        name, ext = os.path.splitext(spath[-1])
        return path, name, ext
    
    @classmethod
    def getTime(cls, file_path): return str(datetime.datetime.fromtimestamp(os.path.getmtime(file_path)))
    
    @classmethod
    def easyWrite(cls, path, data):
        with open(path, 'w') as fd: fd.write(str(data))
    
    @classmethod
    def easyRead(cls, path):
        with open(path, 'r') as fd: return fd.read()
        return None
    
    @classmethod
    def getMD5(cls, path, blocksize=65535):
        md5 = hashlib.md5()
        with open(path, 'rb') as fd:
            for block in iter(lambda: fd.read(blocksize), b''):
                md5.update(block)
        return md5.hexdigest()
    
    def __init__(self, path):
        self.path = path
        self.desc = open(path, 'wr')
        
    def read(self): return self.desc.read()
    def readline(self): return self.desc.readline()
    def write(self, data): self.desc.write(data)
    def writeline(self, data): self.desc.write(data + '\n')
        
class Command:
    
    @classmethod
    def execute(cls, cmd):
        if os.system(cmd) == 0: return True
        return False
    
    def __parse_cmd__(self, cmd):        
        len_cmd = len(cmd)
        word = ''
        const = False
        for i in range(0, len_cmd):
            if const == False:
                if cmd[i] == '\"': word += cmd[i]; const = True
                elif cmd[i] == '|': self.cmd.append([]); word = ''
                elif cmd[i] == ' ':
                    if word != '': self.cmd[-1].append(word); word = ''
                else: word += cmd[i]
            else:
                if cmd[i] == '\"': word += cmd[i]; const = False
                else: word += cmd[i]
        if word != '': self.cmd[-1].append(word)
            
    def __init__(self, cmd=None):
        self.pfd = None
        self.cmd = [[]]
        if cmd: self.__parse_cmd__(cmd)
            
    def add(self, cmd):
        self.__parse_cmd__(cmd)
        return self
        
    def do(self, cmd=None):
        if cmd: self.__parse_cmd__(cmd)
        if Env.isLinux():
            for c in self.cmd:
                if c == []: continue
                if self.pfd: self.pfd = subprocess.Popen(c, stdin=self.pfd.stdout, stdout=subprocess.PIPE)
                else: self.pfd = subprocess.Popen(c, stdout=subprocess.PIPE)
            ret = self.pfd.wait()
            out = self.pfd.stdout.readlines()
        elif Env.isWindows():
            for c in self.cmd:
                if c == []: continue
                if self.pfd: self.pfd = subprocess.Popen(c, shell=True, stdin=self.pfd.stdout, stdout=subprocess.PIPE)
                else: self.pfd = subprocess.Popen(c, shell=True, stdout=subprocess.PIPE)
            ret = self.pfd.wait()
            out = self.pfd.stdout.readlines()
        self.cmd = [[]]
        return (ret, out)
             
    def __str__(self): return str(self.cmd)

class Daemon:
    
    def __init__(self, cmd):
        self.cmd = cmd
        self.pid = 0
        self.pfd = None
        
    def start(self):
        if self.pid != 0: return False
        if Env.isLinux():
            cmd = self.cmd.split(' ')
            self.pfd = subprocess.Popen(cmd)
        elif Env.isWindows():
            cmd = 'start ' + self.cmd
            cmd = cmd.split(' ')
            self.pfd = subprocess.Popen(cmd, shell=True)
        self.pid = self.pfd.pid
        return True
    
    def stop(self):
        if self.pid == 0: return False
        try:
            if Env.isLinux():
                self.pfd.kill()
                os.system('kill -9 %d' % self.pid)
            elif Env.isWindows():
                self.pfd.kill()
        except: return False
        return True
    
    def restart(self):
        self.stop()
        self.start()

    def __del__(self): self.stop()
