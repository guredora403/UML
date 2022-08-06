import wx
import addonHandler
import synthDriverHandler

try:
    addonHandler.initTranslation()
except BaseException:
    def _(x): return x


class EngineSelectionDialog(wx.Dialog):
    def __init__(self, synths, language, focusedEngineIdentifier=None):
        wx.Dialog.__init__(
            self, None, -1, _("Select synthesizer for %s language") % (language))
        self.synths = synths
        synth = _("Synthesizer")
        synthLabel = wx.StaticText(self, wx.ID_ANY, label=synth, name=synth)
        self.synthList = wx.ListBox(self, wx.ID_ANY, name=synth)
        self.synthList.InsertItems([x[1] for x in self.synths], 0)

        ok = wx.Button(self, wx.ID_OK, _("OK"))
        ok.SetDefault()
        cancel = wx.Button(self, wx.ID_CANCEL, _("Cancel"))

        msz = wx.BoxSizer(wx.VERTICAL)
        msz.Add(synthLabel, 0, wx.EXPAND)
        msz.Add(self.synthList, 0, wx.EXPAND)
        msz.AddSpacer(40)

        bsz = wx.BoxSizer(wx.HORIZONTAL)
        bsz.Add(ok, 1)
        bsz.Add(cancel, 1)

        msz.Add(bsz, 0, wx.ALIGN_RIGHT)
        self.SetSizer(msz)
        msz.Fit(self)

    def GetData(self):
        s = self.synthList.GetSelection()
        return self.synths[s][0] if s >= 0 else ""
