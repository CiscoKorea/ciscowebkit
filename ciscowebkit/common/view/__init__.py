
from ciscowebkit.common.view.basic import Layout, Row, Col, Empty, Error, Panel, Plain, Text, VList, HList, InfoBlock, InfoNoti, InfoPanel, InfoDoc, Table, Form

from ciscowebkit.common.view.chartist import ChartistLine, ChartistArea, ChartistBar, ChartistSlide, ChartistDonut

from ciscowebkit.common.view.morris import MorrisLine, MorrisArea, MorrisBar, MorrisDonut

from ciscowebkit.common.view.collection import JustGage

def rotateCols(cols, lists):
    ret = []
    for i in range(0, len(lists)):
        col = [cols[i]]
        for j in range(0, len(lists[i])):
            col.append(lists[i][j])
        ret.append(col)
    return ret