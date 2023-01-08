#      Copyright (C) 2019 Kodi Hue Service (script.service.hue)
#      This file is part of script.service.hue
#      SPDX-License-Identifier: MIT
#      See LICENSE.TXT for more information.

import datetime
import json
from json import JSONDecodeError

import xbmc
import xbmcgui

from resources.lib import ADDON
from resources.lib.language import get_string as _

win = xbmcgui.Window(10000)


def validate_settings():
    _validate_schedule()
    _validate_ambilight()


def _validate_ambilight():
    xbmc.log(f"[script.service.hue] Validate ambilight config. Enabled: {ADDON.getSettingBool('group3_enabled')}")
    if ADDON.getSettingBool("group3_enabled"):
        light_ids = ADDON.getSetting("group3_Lights")
        if light_ids == "-1":
            ADDON.setSettingBool("group3_enabled", False)
            xbmc.log("[script.service.hue] No ambilights selected")
            notification(_("Hue Service"), _("No lights selected for Ambilight."), icon=xbmcgui.NOTIFICATION_ERROR)


def _validate_schedule():
    xbmc.log(f"[script.service.hue] Validate schedule. Schedule Enabled: {ADDON.getSettingBool('enableSchedule')}")
    if ADDON.getSettingBool("enableSchedule"):
        try:
            convert_time(ADDON.getSettingString("startTime"))
            convert_time(ADDON.getSettingString("endTime"))
            # xbmc.log("[script.service.hue] Time looks valid")
        except ValueError as e:
            ADDON.setSettingBool("EnableSchedule", False)
            xbmc.log(f"[script.service.hue] Invalid time settings: {e}")
            notification(_("Hue Service"), _("Invalid start or end time, schedule disabled"), icon=xbmcgui.NOTIFICATION_ERROR)


def convert_time(time):
    hour = int(time.split(":")[0])
    minute = int(time.split(":")[1])
    return datetime.time(hour, minute)


def notification(header, message, time=5000, icon=ADDON.getAddonInfo('icon'), sound=False):
    xbmcgui.Dialog().notification(header, message, icon, time, sound)


def cache_get(key: str):
    data_str = win.getProperty(key)
    try:
        data = json.loads(data_str)
        # xbmc.log(f"[script.service.hue] Cache Get: {key}, {data}")
        return data
    except JSONDecodeError:
        # Occurs when Cache is empty or unreadable (Eg. Old SimpleCache data still in memory because Kodi hasn't restarted)
        return None


def cache_set(key, data):
    data_type = type(data)
    data_str = json.dumps(data)
    # xbmc.log(f"[script.service.hue] Cache Set: {key}, {data_str} - {data_type}")
    win.setProperty(key, data_str)
    return
