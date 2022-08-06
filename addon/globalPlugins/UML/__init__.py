from __future__ import unicode_literals
import os
import globalPluginHandler
import gui
import wx
import addonHandler
import globalVars
import config
import synthDriverHandler
from logHandler import log
from .constants import *
from .settings import SettingsDialog
from . import updater


try:
    addonHandler.initTranslation()
except BaseException:
    def _(x): return x


# Define conspec here too. Looks like it fails to access some values when UML is not set as speech synthesizer.
confspec = {
    "primaryLanguage": "string(default=ja)",
    "strategy": "string(default=word)",
    "japanese": "string(default=_)",
    "fallback": "string(default=_)",
    "checkForUpdatesOnStartup": "boolean(default=True)",
}
config.conf.spec["UML_global"] = confspec

class GlobalPlugin(globalPluginHandler.GlobalPlugin):
    scriptCategory = _("UML")

    def __init__(self, *args, **kwargs):
        super(GlobalPlugin, self).__init__(*args, **kwargs)
        if globalVars.appArgs.secure:
            return
        # end secure screen
        if self.getUpdateCheckSetting() is True:
            self.autoUpdateChecker = updater.AutoUpdateChecker()
            self.autoUpdateChecker.autoUpdateCheck(mode=updater.AUTO)
        # end update check
        self._setupMenu()

    def terminate(self):
        super(GlobalPlugin, self).terminate()
        try:
            gui.mainFrame.sysTrayIcon.menu.Remove(self.rootMenuItem)
        except BaseException:
            pass

    def _setupMenu(self):
        self.rootMenu = wx.Menu()

        self.settingsItem = self.rootMenu.Append(wx.ID_ANY, _("&Settings of Universal Multilingual"), _(
            "Change settings of Universal Multilingual"))
        gui.mainFrame.sysTrayIcon.Bind(
            wx.EVT_MENU, self.settings, self.settingsItem)

        self.updateCheckToggleItem = self.rootMenu.Append(
            wx.ID_ANY,
            self.updateCheckToggleString(),
            _("Toggles update checking on startup.")
        )
        gui.mainFrame.sysTrayIcon.Bind(
            wx.EVT_MENU, self.toggleUpdateCheck, self.updateCheckToggleItem)

        self.updateCheckPerformItem = self.rootMenu.Append(
            wx.ID_ANY,
            _("Check for updates"),
            _("Checks for new updates manually.")
        )
        gui.mainFrame.sysTrayIcon.Bind(
            wx.EVT_MENU, self.performUpdateCheck, self.updateCheckPerformItem)

        self.rootMenuItem = gui.mainFrame.sysTrayIcon.menu.Insert(
            2, wx.ID_ANY, _("Universal Multilingual"), self.rootMenu)

    def settings(self, evt):
        engineMap = {
            "ja": config.conf["UML_global"]["japanese"],
            "en": config.conf["UML_global"]["fallback"],
        }
        opts = {
            "primary_language": config.conf["UML_global"]["primaryLanguage"],
            "strategy": config.conf["UML_global"]["strategy"],
            "engineMap": engineMap,
        }
        print(opts)
        dlg = SettingsDialog(opts)
        ret = dlg.ShowModal()
        if ret == wx.ID_OK:
            self._saveSettings(dlg.GetData())
        dlg.Destroy()

    def _saveSettings(self, data):
        # If the new settings fail, revert to the previous one.
        backup = list(config.conf["UML_global"].items())
        config.conf["UML_global"]["primaryLanguage"] = data["primary_language"]
        config.conf["UML_global"]["strategy"] = data["strategy"]
        config.conf["UML_global"]["japanese"] = data["engineMap"]["ja"]
        config.conf["UML_global"]["fallback"] = data["engineMap"]["en"]
        if synthDriverHandler.getSynth().name == "UML":
            self._askHotReload(backup)

    def _askHotReload(self, backup):
        ret = gui.messageBox(_("You are currently using Universal Multilingual.\nDo you want to reload Universal Multilingual and apply the new settings now?"), caption=_(
            "Confirmation"), style=wx.YES_NO)
        if ret == wx.ID_NO:
            return

        synthDriverHandler.setSynth(None)

        # Try to create new synth
        try:
            newSynth = synthDriverHandler.getSynthInstance(
                "UML", asDefault=True)
        except BaseException as e:
            for elem in backup:
                config.conf["UML_global"][elem[0]] = elem[1]
            synthDriverHandler.setSynth("UML")
            gui.messageBox(_("Failed to reload Universal multilingual.\nreason: %s\nThe new settings will not be applied.") % (
                e), _("Error"))
            return
        # end exception
        synthDriverHandler._curSynth = newSynth

    def updateCheckToggleString(self):
        return _("Disable checking for updates on startup") if self.getUpdateCheckSetting() is True else _("Enable checking for updates on startup")

    def toggleUpdateCheck(self, evt):
        changed = not self.getUpdateCheckSetting()
        self.setUpdateCheckSetting(changed)
        msg = _("Updates will be checked automatically when launching NVDA.") if changed is True else _(
            "Updates will not be checked when launching NVDA.")
        self.updateCheckToggleItem.SetItemLabel(self.updateCheckToggleString())
        gui.messageBox(msg, _("Settings changed"))

    def performUpdateCheck(self, evt):
        updater.AutoUpdateChecker().autoUpdateCheck(mode=updater.MANUAL)

    def getUpdateCheckSetting(self):
        return config.conf["UML_global"]["checkForUpdatesOnStartup"]

    def setUpdateCheckSetting(self, val):
        config.conf["UML_global"]["checkForUpdatesOnStartup"] = val
