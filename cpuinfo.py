# Small utility for Linux which shows CPU usage information.
# Requires wxPython
# 
# Copyright (c) 2014 Victor Kindhart
import time
import wx

# Constants
CONST_PROCFILE = "/proc/stat"
CONST_SIZE = (100, 120)
CONST_STYLE = wx.NO_BORDER|wx.CAPTION|wx.STAY_ON_TOP
CONST_WIDGET_CPUWIDGET_SIZE  = (60, 80)

def get_cpu_info(fn, cpunum):
    """
    Get information about specified CPU

    @param string fn - file to read data from
    @param string cpunum - CPU name/number (space for total cpu info)
    """
    with open(fn, "rb") as fp:
        data = fp.read()
    line = [ln for ln in data.splitlines()
                if ln.startswith("cpu%s" % cpunum)][0]
    cpu = line.split()
    return [int(i) for i in cpu[1:]]

class CPUWidget(wx.Panel):
    def __init__(self, parent, size=CONST_WIDGET_CPUWIDGET_SIZE):
        wx.Panel.__init__(self, parent, size=size)
        self.Load = 0

        psize = self.GetParent().GetSize()
        pos = [(psize[0] - size[0])/2, (psize[1] - size[1])/2]
        self.SetPosition(pos)

        self._brush_on  = wx.Brush('#36FF27')
        self._brush_off = wx.Brush('#075100')

        self.SetBackgroundColour("#000000")
        self.Bind(wx.EVT_PAINT, self.OnPaint)

    def SetLoad(self, load):
        self.Load = load

    def GetLoad(self):
        return self.Load

    def OnPaint(self, evt):

        dc = wx.PaintDC(self)
        load = self.GetLoad()/10

        size = self.GetSize()
        x = 5
        x2 = 30
        sx = 25
        sy = 8

        for i in xrange(1, 11):
            if 10 - i > load:
                dc.SetBrush(self._brush_off)
                dc.DrawRectangle(x, i*7 - 2, sx, sy)
                dc.DrawRectangle(x2, i*7 - 2, sx, sy)
            else:
                dc.SetBrush(self._brush_on)
                dc.DrawRectangle(x, i*7 - 2, sx, sy)
                dc.DrawRectangle(x2, i*7 - 2, sx, sy)

class CPUFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, -1, "CPU info",
                          size=CONST_SIZE,
                          style=CONST_STYLE)
        self._dragging = False
        self._mouse_pos = (0, 0)
        self.panel = wx.Panel(self)
        self.panel.SetSize(self.GetSize())

        self.panel.Bind(wx.EVT_LEFT_DOWN, self._OnLeftDown)
        self.panel.Bind(wx.EVT_MOTION, self._OnMouseMove)
        self.panel.Bind(wx.EVT_LEFT_UP, self._OnLeftUp)
        self.panel.Bind(wx.EVT_PAINT, self._FrameThemePaint)

        self.cpu = CPUWidget(self.panel)
        self.pcnt = wx.StaticText(self.panel)
        #self.MakeCloseButton()
        self.PREV_TOTAL = 0
        self.PREV_IDLE  = 0

        wx.CallLater(1, self.update)

    def update(self):
        cpu = get_cpu_info(CONST_PROCFILE, ' ')
        IDLE = cpu[3]
        TOTAL = sum(cpu[:7])

        DIFF_IDLE = IDLE - self.PREV_IDLE
        DIFF_TOTAL = TOTAL - self.PREV_TOTAL
        DIFF_USAGE = (1000.*(DIFF_TOTAL-DIFF_IDLE)/DIFF_TOTAL+5)/10.
        self.cpu.SetLoad(int(DIFF_USAGE))
        self.cpu.OnPaint(None)
        self.pcnt.SetLabel("%.2f%%" % DIFF_USAGE)
        self.pcnt.Centre()
        self.pcnt.SetPosition((self.pcnt.GetPosition()[0], 0))
            
        self.PREV_TOTAL = TOTAL
        self.PREV_IDLE = IDLE
        wx.CallLater(1000, self.update)

    def _FrameThemePaint(self, evt):
        sx, sy = self.GetSize()

        dc = wx.PaintDC(self.panel)
        dc.SetPen(wx.Pen("#898989"))
        dc.DrawRectangle(0, 0, sx, sy)

        dc.SetPen(wx.Pen("#ECECEC"))
        dc.SetBrush(wx.Brush("#E1E1E1"))
        dc.DrawRectangle(1, 1, sx - 2, sy - 2)

    def _OnLeftDown(self, evt):
        self._dragging  = True
        self._mouse_pos = self.ScreenToClient(wx.GetMousePosition())
    
    def _OnMouseMove(self, evt):
        if self._dragging:
            mx, my = wx.GetMousePosition()
            ox, oy = self._mouse_pos
            
            self.SetPosition((mx - ox, my - oy))
    
    def _OnLeftUp(self, evt):
        self._dragging = False

app = wx.App()
frame = CPUFrame()
frame.Show()
app.MainLoop()
