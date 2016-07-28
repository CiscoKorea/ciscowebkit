#-*- coding: utf-8 -*-
'''
Created on 2016. 7. 11.

@author: "comfact"
'''

from ciscowebkit.common import *

class Base(Feature):
    
    '''Base Elements'''
    
    def __init__(self, **kargs):
        Feature.__init__(self, 3, 'fa-archive', **kargs)
        self.inum = 0
        self.itable = Table('ID', 'Name', 'Data')
        self.ipanel = Panel("Input Data", self.itable)
        
    def get(self, requset, *cmd):
        lo = Layout()
        
        lo.addRow()
        lo.addCol(Panel("T1", Text("This is Text 1", link=(None, 't1'))), scr=Layout.SMALL, size=6)
        lo.addCol(Panel("T2", Text("This is Text 2", link=(None, 't2'))), scr=Layout.SMALL, size=6)
        
        lo.addRow()
        lo.addCol(InfoBlock('Test Info 1', 'This is Test Msg and active'))
        lo.addCol(InfoBlock('Test Info 2', 'This is Test Msg and deactive'))
        
        lo.addRow()
        lo.addCol(InfoPanel('Info Panel', 100, 'link to self', panel=Panel.INFO, link=(self, None)), scr=Layout.SMALL, size=6)
        lo.addCol(InfoDoc('''This is information document.
This page is chart samples

Let's start sample view models !!!
'''), scr=Layout.SMALL, size=6)
        
        lo.addRow()
        lo.addCol(VList().add('t1', 't1', 'fa-bus', 't1').add('t2', 't2', 'fa-plane', 't2'), scr=Layout.SMALL, size=6)
        lo.addCol(HList().add('t1', 't1', 'fa-bus', 't1').add('t2', 't2', 'fa-plane', 't2'), scr=Layout.SMALL, size=6)
        
        lo.addRow()
        t1 = Table('Col1', 'Col2', 'Col3', title='Table 1').add('1', '2', '3', link=(None, 't1')).add('a', 'b', 'c', link=(None, 't2')).add('A', 'B', 'C', link=(None, 't1')).add('가', '나', '다', link=(None, 't2'))
        t2 = Table('Col1', 'Col2', 'Col3', title='Table 2').add('1', '2', '3', did='t1').add('a', 'b', 'c', did='t2').add('A', 'B', 'C', did='t3').add('가', '나', '다', did='t4')
        lot = Layout().addRow().addCol(t1).addRow().addCol(t2)
        lo.addCol(Panel("Tables", lot))
        
        lo.addRow()
        form = Form('Submit').addText('test1', 'TextInput1').addText('test2', 'TextInput2')
        lo.addCol(Panel("Form", form))
        
        lo.addRow().addCol(self.ipanel)
        
        return lo
    
    def post(self, request, data, *cmd):
        print 'Call Post', data
        self.itable.add(str(self.inum), data.test1, data.test2)
        self.inum += 1
        return self.get(request, *cmd)

    def delete(self, request, data, *cmd):
        print 'Call Delete', data
        return self.get(request, *cmd)
