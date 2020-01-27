import threading

import cv2
import wx

from old_code_snippets.Camera import analyze_camera

ID_COUNT = wx.NewId()
myEVT_COUNT = wx.NewEventType()
EVT_COUNT = wx.PyEventBinder(myEVT_COUNT, 1)


class CountingThread(threading.Thread):
    def __init__(self, parent, value):
        """
        @param parent: The gui object that should recieve the value
        @param value: value to 'calculate' to
        """
        threading.Thread.__init__(self)
        self._parent = parent
        self._value = value

    def run(self):
        """Overrides Thread.run. Don't call this directly its called internally
        when you call Thread.start().
        """
        # time.sleep(2)  # our simulated calculation time
        ret = analyze_camera(cap)
        evt = CountEvent(myEVT_COUNT, -1, self.ret)
        wx.PostEvent(self._parent, evt)


class CountEvent(wx.PyCommandEvent):
    """Event to signal that a count value is ready"""

    def __init__(self, etype, eid, value=None):
        """Creates the event object"""
        wx.PyCommandEvent.__init__(self, etype, eid)
        self._value = value

    def GetValue(self):
        """Returns the value from the event.
        @return: the value of this event

        """
        return self._value


class CountingFrame(wx.Frame):
    def __init__(self, parent):
        wx.Frame.__init__(self, parent, title="Lets Count", size=(300, 300))

        # Attributes

        # Layout
        self.__DoLayout()
        self.CreateStatusBar()

        # Event Handlers

    def __DoLayout(self):
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(CountingPanel(self), 1, wx.ALIGN_CENTER)
        self.SetSizer(sizer)
        self.SetMinSize((300, 300))


class CountingPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        # Attributes
        self._counter = wx.StaticText(self, label="0")
        self._counter.SetFont(wx.Font(16, wx.MODERN, wx.NORMAL, wx.NORMAL))

        # Layout
        self.__DoLayout()

        # Event Handlers
        self.Bind(wx.EVT_BUTTON, self.OnButton)
        self.Bind(EVT_COUNT, self.OnCount)

    def __DoLayout(self):
        sizer = wx.BoxSizer(wx.VERTICAL)
        button = wx.Button(self, ID_COUNT, "Increment Counter")
        sizer.AddMany([(button, 0, wx.ALIGN_CENTER),
                       ((15, 15), 0),
                       (self._counter, 0, wx.ALIGN_CENTER)])
        self.SetSizer(sizer)

    def OnButton(self, evt):
        worker = CountingThread(self, 1)
        worker.start()

    def OnCount(self, evt):
        val = int(self._counter.GetLabel()) + evt.GetValue()
        self._counter.SetLabel(unicode(val))




# -----------------------------------------------------------------------------#

if __name__ == '__main__':
    cap = cv2.VideoCapture(0)
    APP = wx.App(False)
    FRAME = CountingFrame(None)
    FRAME.Show()
    APP.MainLoop()
