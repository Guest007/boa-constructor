# Boa:WizardPage:wxWizardPage2

import wx
from wx.adv import WizardPage

[wxID_WXWIZARDPAGE2] = [wx.NewId() for _init_ctrls in range(1)]


class wxWizardPage2(WizardPage):
    def _init_ctrls(self, prnt):
        # generated method, don't edit
        WizardPage.__init__(self, bitmap=wx.NullBitmap, parent=prnt)
        self.SetSize(wx.Size(960, 692))
        self.SetClientSize(wx.Size(952, 665))
        self.SetPosition(wx.Point(110, 110))

    def __init__(self, parent):
        self._init_ctrls(parent)
