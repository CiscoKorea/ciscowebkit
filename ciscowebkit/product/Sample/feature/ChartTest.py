#-*- coding: utf-8 -*-
'''
Created on 2016. 7. 11.

@author: "comfact"
'''

from ciscowebkit.common import Feature
from ciscowebkit.common.platform import Manager, View

class ChartTest(Feature):
    
    '''Single Feature 1'''
    
    def __init__(self, **kargs):
        Feature.__init__(self, 'fa-archive', **kargs)
        
    def get(self, request):
        
        iblock1 = View.InfoBlock('New Information 1')
        iblock2 = View.InfoBlock('Title', 'Message', 'fa-question-circle')
        
        ipanel1 = View.InfoPanel('Info Panel 1 to Self', 99, '/sample/charttest/', panel=View.PANEL.DANGER)
        ipanel2 = View.InfoPanel('Info Panel 2 to Dashboard', 20, '/dashboard', icon='fa-question-circle', panel=View.PANEL.SUCCESS)
        
        idoc = View.InfoDoc('Document', '''This is information document.
This page is chart samples

Let's start sample view models !!!''', panel=View.PANEL.SUCCESS)
        
        vlist = View.VListData('Vertical List', panel=View.PANEL.INFO)
        vlist.addList('Test 1')
        vlist.addList('Self Link', '/sample/charttest/', 'fa-link', 'to here')
        vlist.addList('Dashboard', '/dashboard', 'fa-dashboard', 'to dashboard', True)
        vlist.addList('Dummy', None, 'fa-trash', 'nothing')
        
        hlist = View.HListData('Horizonal List', panel=View.PANEL.INFO)
        hlist.addList('Test 1')
        hlist.addList('Self Link', '/sample/charttest/', 'fa-link', 'to here')
        hlist.addList('Dashboard', '/dashboard', 'fa-dashboard', 'to dashboard', True)
        hlist.addList('Dummy', None, 'fa-trash', 'nothing')
        
        data1 = View.TableData('Feature 1-1', panel=View.PANEL.INFO)
        data1.setHead('Col1', 'Col2', 'Col3')
        data1.addData('1', '2', '3')
        data1.addData('A', 'B', 'C', type=View.TableData.DANGER)
        data1.addData('a', 'b', 'c', type=View.TableData.ACTIVE)
        data1.addData('가', '나', '다')
        
        data2 = View.TableData('Feature 1-2', panel=View.PANEL.DANGER)
        data2.optStripe()
        data2.setHead('Col1', 'Col2', 'Col3')
        data2.addData('1', '2', '3')
        data2.addData('A', 'B', 'C', type=View.TableData.WARNING)
        data2.addData('a', 'b', 'c', type=View.TableData.SUCCESS)
        data2.addData('가', '나', '다')
        
        numline1 = View.NumLineData('NumLineData1', panel=View.PANEL.SUCCESS)
        numline1.addLine('Line1')
        numline1.addData('Line1', 1, '10')
        numline1.addData('Line1', 2, '20')
        numline1.addData('Line1', 3, 30)
        numline1.addLine('Line2')
        numline1.addData('Line2', 1, 50)
        numline1.addData('Line2', '2', 70)
        numline1.addData('Line2', 3, 90)
        
        numline2 = View.NumLineData('NumLineData2', panel=View.PANEL.SUCCESS)
        numline2.optGrid(0, None, 1, None, 100, 10)
        numline2.addLine('Line1')
        numline2.addData('Line1', 1, '10')
        numline2.addData('Line1', 2, '20')
        numline2.addData('Line1', 3, 30)
        numline2.addLine('Line2')
        numline2.addData('Line2', 1, 50)
        numline2.addData('Line2', '2', 70)
        numline2.addData('Line2', 3, 90)
        
        timeline1 = View.TimeLineData('TimeLineData1', panel=View.PANEL.BLUE)
        timeline1.setLabel('Quater', 'CheolSoo', 'YoungHee')
        timeline1.addData('2015 Q1', 10, 20)
        timeline1.addData('2015 Q2', 20, 30)
        timeline1.addData('2015 Q3', 30, 40)
        timeline1.addData('2015 Q4', 40, 10)
        timeline1.addData('2016 Q1', 50, 20)
        timeline1.addData('2016 Q2', 60, 30)
        timeline1.addData('2016 Q3', 30, 50)
        timeline1.addData('2016 Q4', 20, 60)
        
        timeline2 = View.TimeLineData('TimeLineData2', panel=View.PANEL.BLUE)
        timeline2.optArea()
        timeline2.optSmooth()
        timeline2.optGrid(0, 100)
        timeline2.setLabel('Quater', 'CheolSoo', 'YoungHee')
        timeline2.addData('2015 Q1', 10, 20)
        timeline2.addData('2015 Q2', 20, 30)
        timeline2.addData('2015 Q3', 30, 40)
        timeline2.addData('2015 Q4', 40, 10)
        timeline2.addData('2016 Q1', 50, 20)
        timeline2.addData('2016 Q2', 60, 30)
        timeline2.addData('2016 Q3', 30, 50)
        timeline2.addData('2016 Q4', 20, 60)
        
        bar1 = View.BarData('BarData1', panel=View.PANEL.GREEN)
        bar1.setLabel('IceCream', 'Tasty', 'Visual')
        bar1.addData('Jaws', -5, 20)
        bar1.addData('Screw', 10, 15)
        bar1.addData('Candy', 12, -10)
        bar1.addData('Dwaeji', 15, 10)
        bar1.addData('Left', 20, 0)
        bar1.addData('Right', 0, 20)
        
        bar2 = View.BarData('BarData2', panel=View.PANEL.GREEN)
        bar2.optGrid(-10, 30)
        bar2.setLabel('IceCream', 'Tasty', 'Visual')
        bar2.addData('Jaws', -5, 20)
        bar2.addData('Screw', 10, 15)
        bar2.addData('Candy', 12, -10)
        bar2.addData('Dwaeji', 15, 10)
        bar2.addData('Left', 20, 0)
        bar2.addData('Right', 0, 20)
        
        donut1 = View.DonutData('DonutData1', panel=View.PANEL.WARN)
        donut1.addData('Dunkin', '30')
        donut1.addData('Crispy', '40')
        donut1.addData('Sijang', '10')
        
        donut2 = View.DonutData('DonutData2', panel=View.PANEL.WARN)
        donut2.addData('Dunkin', '30')
        donut2.addData('Crispy', '40')
        donut2.addData('Sijang', '10')
        
        pie1 = View.PieData('PieData1', panel=View.PANEL.YELLOW)
        pie1.addData('apple', 10)
        pie1.addData('peanut', 25)
        pie1.addData('cream', 12)
        pie1.addData('pizza', 34)
        
        pie2 = View.PieData('PieData2', panel=View.PANEL.YELLOW)
        pie2.addData('apple', 10)
        pie2.addData('peanut', 25)
        pie2.addData('cream', 12)
        pie2.addData('pizza', 34)
        
        mv = View.MultiView()
        mv.addView(iblock1).addView(iblock2)
        mv.addRow().addView(ipanel1, present='midium', size=6).addView(ipanel2, present='midium', size=6)
        mv.addRow().addView(idoc)
        mv.addRow().addView(vlist, size=6).addView(hlist, size=6)
        mv.addRow().addView(data1, size=6).addView(data2, size=6)
        mv.addRow().addView(numline1, size=6).addView(numline2, size=6)
        mv.addRow().addView(timeline1, size=6).addView(timeline2, size=6)
        mv.addRow().addView(bar1, size=6).addView(bar2, size=6)
        mv.addRow().addView(donut1, size=6).addView(donut2, size=6)
        mv.addRow().addView(pie1, size=6).addView(pie2, size=6)
        
        return Manager.render(mv)
