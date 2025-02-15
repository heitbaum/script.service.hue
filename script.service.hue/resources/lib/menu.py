#      Copyright (C) 2019 Kodi Hue Service (script.service.hue)
#      This file is part of script.service.hue
#      SPDX-License-Identifier: MIT
#      See LICENSE.TXT for more information.

import sys
from urllib.parse import parse_qs

import xbmc
import xbmcplugin
import xbmcvfs
from xbmcgui import ListItem

from . import ADDON, ADDONID, ADDONPATH
from .kodiutils import cache_set, cache_get
from .language import get_string as _


def menu():
    route = sys.argv[0]
    addon_handle = int(sys.argv[1])
    base_url = sys.argv[0]
    command = sys.argv[2][1:]
    parsed = parse_qs(command)

    if route == f"plugin://{ADDONID}/":
        if not command:
            build_menu(base_url, addon_handle)

        elif command == "settings":
            ADDON.openSettings()
            xbmc.executebuiltin('Container.Refresh')

        elif command == "toggle":
            if cache_get("service_enabled") and _get_status() != "Disabled by daylight":
                xbmc.log("[script.service.hue] Disable service")
                cache_set("service_enabled", False)

            elif _get_status() != "Disabled by daylight":
                xbmc.log("[script.service.hue] Enable service")
                cache_set("service_enabled", True)
            else:
                xbmc.log("[script.service.hue] Disabled by daylight, ignoring")

            xbmc.executebuiltin('Container.Refresh')

    elif route == f"plugin://{ADDONID}/actions":
        action = parsed['action'][0]
        light_group_id = parsed['light_group_id'][0]
        xbmc.log(f"[script.service.hue] Actions: {action}, light_group_id: {light_group_id}")
        if action == "menu":

            xbmcplugin.addDirectoryItem(addon_handle, base_url + "?action=play&light_group_id=" + light_group_id, ListItem(_("Play")))
            xbmcplugin.addDirectoryItem(addon_handle, base_url + "?action=pause&light_group_id=" + light_group_id, ListItem(_("Pause")))
            xbmcplugin.addDirectoryItem(addon_handle, base_url + "?action=stop&light_group_id=" + light_group_id, ListItem(_("Stop")))

            xbmcplugin.endOfDirectory(handle=addon_handle, cacheToDisc=True)
        else:
            cache_set("action", (action, light_group_id))
    else:
        xbmc.log(f"[script.service.hue] Unknown command. Handle: {addon_handle}, route: {route}, Arguments: {sys.argv}")


def build_menu(base_url, addon_handle):
    xbmc.log(f"[script.service.hue] build_menu: status: {_get_status()}")
    status_item = ListItem(_("Hue Status: ") + _get_status())
    status_icon = _get_status_icon()
    if status_icon:
        status_item.setArt({"icon": status_icon})
        xbmc.log(f"[script.service.hue] status_icon: {status_icon}")

    settings_item = ListItem(_("Settings"))
    settings_item.setArt({"icon": xbmcvfs.makeLegalFilename(ADDONPATH + "resources/icons/settings.png")})

    xbmcplugin.addDirectoryItem(addon_handle, base_url + "/actions?light_group_id=1&action=menu", ListItem(_("Video Actions")), True)
    xbmcplugin.addDirectoryItem(addon_handle, base_url + "/actions?light_group_id=2&action=menu", ListItem(_("Audio Actions")), True)
    xbmcplugin.addDirectoryItem(addon_handle, base_url + "?toggle", status_item)
    xbmcplugin.addDirectoryItem(addon_handle, base_url + "?settings", settings_item)

    xbmcplugin.endOfDirectory(handle=addon_handle, cacheToDisc=False)


def _get_status():
    enabled = cache_get("service_enabled")
    daylight = cache_get("daylight")
    daylight_disable = ADDON.getSettingBool("daylightDisable")
    xbmc.log(f"[script.service.hue] _get_status enabled: {enabled}   -  {type(enabled)}, daylight: {daylight}, daylight_disable: {daylight_disable}")

    # xbmc.log("[script.service.hue] Current status: {}".format(daylight_disable))
    if daylight and daylight_disable:
        return _("Disabled by daylight")
    if enabled:
        return _("Enabled")
    elif not enabled:
        return _("Disabled")
    else:
        return "NoneType"


def _get_status_icon():
    enabled = cache_get("service_enabled")
    daylight = cache_get("daylight")
    daylight_disable = ADDON.getSettingBool("daylightDisable")
    # xbmc.log("[script.service.hue] Current status: {}".format(daylight_disable))
    if daylight and daylight_disable:
        return xbmcvfs.makeLegalFilename(ADDONPATH + "resources/icons/daylight.png")  # Disabled by Daylight
    elif enabled:
        return xbmcvfs.makeLegalFilename(ADDONPATH + "resources/icons/enabled.png")  # Enabled
    return xbmcvfs.makeLegalFilename(ADDONPATH + "resources/icons/disabled.png")  # Disabled
