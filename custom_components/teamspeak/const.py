"""Constants for the Teamspeak 3 Server integration."""

from homeassistant.const import Platform

DOMAIN = "teamspeak"
MANUFACTURER = "TeamSpeak Systems, Inc."
ATTRIBUTION = f"Data provided by a TeamSpeak 3 Server by {MANUFACTURER}."
ICON = "mdi:headset"

PLATFORMS: list[Platform] = [Platform.SENSOR]
