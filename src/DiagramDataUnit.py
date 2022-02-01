import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import matplotlib.patches as patches
from matplotlib.text import Text

import math


class LineDataUnits(Line2D):
    def __init__(self, *args, **kwargs):
        _lw_data = kwargs.pop("linewidth", 1)
        super().__init__(*args, **kwargs)
        self._lw_data = _lw_data

    def _get_lw(self):
        if self.axes is not None:
            ppd = 72./self.axes.figure.dpi
            trans = self.axes.transData.transform
            return ((trans((1, self._lw_data))-trans((0, 0)))*ppd)[1]
        else:
            return 1

    def _set_lw(self, lw):
        self._lw_data = lw

    _linewidth = property(_get_lw, _set_lw)


class CircleDataUnit(patches.Circle):
    def __init__(self, *args, **kwargs):
        _lw_data = kwargs.pop("linewidth", 1)
        super().__init__(*args, **kwargs)
        self._lw_data = _lw_data

    def _get_lw(self):
        if self.axes is not None:
            ppd = 72./self.axes.figure.dpi
            trans = self.axes.transData.transform
            return ((trans((1, self._lw_data))-trans((0, 0)))*ppd)[1]
        else:
            return 1

    def _set_lw(self, lw):
        self._lw_data = lw

    _linewidth = property(_get_lw, _set_lw)


class TextDataUnit(Text):
    def __init__(self, *args, **kwargs):
        _fontsize_data = kwargs.pop("fontsize", 1)
        super().__init__(*args, **kwargs)
        self._fontsize_data = _fontsize_data

    def _get_fontsize(self):
        if self.axes is not None:
            ppd = 72./self.axes.figure.dpi
            trans = self.axes.transData.transform
            return ((trans((1, self._fontsize_data))-trans((0, 0)))*ppd)[1]
        else:
            return 1

    def _set_fontsize(self, fontsize):
        self._fontsize_data = fontsize

    _linewidth = property(_get_fontsize, _set_fontsize)


def get_arc_param(x1, y1, x2, y2, phi, curve: float = 180.0):
    u = -curve/360.0
    n = [-(y2-y1), (x2-x1)]
    m = [0.5*(x1+x2), 0.5*(y1+y2)]
    x3 = m[0] - u*n[0]
    y3 = m[1] - u*n[1]

    x0 = (x1**2*y2 - x1**2*y3 - x2**2*y1 + x2**2*y3 + x3**2*y1 - x3**2*y2 + y1**2*y2 - y1**2*y3 -
          y1*y2**2 + y1*y3**2 + y2**2*y3 - y2*y3**2)/(2*(x1*y2 - x1*y3 - x2*y1 + x2*y3 + x3*y1 - x3*y2)+1e-6)
    y0 = -(x1**2*x2 - x1**2*x3 - x1*x2**2 + x1*x3**2 - x1*y2**2 + x1*y3**2 + x2**2*x3 - x2*x3**2 +
           x2*y1**2 - x2*y3**2 - x3*y1**2 + x3*y2**2)/(2*(x1*y2 - x1*y3 - x2*y1 + x2*y3 + x3*y1 - x3*y2)+1e-6)
    r = -math.sqrt((x1**2 - 2*x1*x2 + x2**2 + y1**2 - 2*y1*y2 + y2**2)*(x1**2 - 2*x1*x3 + x3**2 + y1**2 - 2*y1*y3 + y3**2)
                   * (x2**2 - 2*x2*x3 + x3**2 + y2**2 - 2*y2*y3 + y3**2))/(2*(x1*y2 - x1*y3 - x2*y1 + x2*y3 + x3*y1 - x3*y2)+1e-6)

    theta1 = math.atan2((y1-y0), (x1-x0))
    theta2 = math.atan2((y2-y0), (x2-x0))

    return x0, y0, r, theta1, theta2, x3, y3


class ArcDataUnit(patches.Arc):
    def __init__(self, *args, **kwargs):
        _lw_data = kwargs.pop("linewidth", 1)
        super().__init__(*args, **kwargs)
        self._lw_data = _lw_data

    def _get_lw(self):
        if self.axes is not None:
            ppd = 72./self.axes.figure.dpi
            trans = self.axes.transData.transform
            return ((trans((1, self._lw_data))-trans((0, 0)))*ppd)[1]
        else:
            return 1

    def _set_lw(self, lw):
        self._lw_data = lw

    _linewidth = property(_get_lw, _set_lw)
