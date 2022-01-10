"""Tapo L1510 Bulb Home Assistant Intergration"""
import logging

from PyP100 import PyL530
import voluptuous as vol
from base64 import b64decode

import homeassistant.helpers.config_validation as cv

from homeassistant.components.light import (
    LightEntity,
    PLATFORM_SCHEMA,
    SUPPORT_BRIGHTNESS,
    ATTR_BRIGHTNESS
    )
from homeassistant.const import CONF_IP_ADDRESS, CONF_EMAIL, CONF_PASSWORD

import json

# Validation of the user's configuration
PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_IP_ADDRESS): cv.string,
    vol.Required(CONF_EMAIL): cv.string,
    vol.Required(CONF_PASSWORD): cv.string,
})

_LOGGER = logging.getLogger(__name__)

def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the Awesome Light platform."""
    # Assign configuration variables.
    # The configuration check takes care they are present.
    ipAddress = config[CONF_IP_ADDRESS]
    email = config[CONF_EMAIL]
    password = config.get(CONF_PASSWORD)

    # Setup connection with devices/cloud
    l530 = PyL530.L530(ipAddress, email, password)

    try:
    	l530.handshake()
    	l530.login()
    except:
    	_LOGGER.error("Could not connect to plug. Possibly invalid credentials")

    add_entities([L1510Bulb(l530)])

class L1510Bulb(LightEntity):
    """Representation of a P100 Plug"""

    def __init__(self, l530):
        self._l530 = l530
        self._is_on = False
        self._brightness = 255

        self.update()

    @property
    def name(self):
        """Name of the device."""
        return self._name

    @property
    def unique_id(self):
        """Unique id."""
        return self._unique_id

    @property
    def is_on(self):
        """Name of the device."""
        return self._is_on

    @property
    def brightness(self):
        return self._brightness

    @property
    def supported_features(self):
        """Flag supported features."""
        return SUPPORT_BRIGHTNESS

    def turn_on(self, **kwargs) -> None:
        """Turn Plug On"""

        newBrightness = kwargs.get(ATTR_BRIGHTNESS, 255)

        newBrightness = (newBrightness / 255) * 100

        self._l530.setBrightness(newBrightness)
        self._l530.turnOn()

        self._is_on = True
        self._brightness = kwargs.get(ATTR_BRIGHTNESS, 255)

    def turn_off(self, **kwargs):
        """Turn Plug Off"""
        self._l530.turnOff()

        self._is_on = False

    def update(self):
        self._l530.handshake()
        self._l530.login()

        data = self._l530.getDeviceInfo()

        encodedName = data["result"]["nickname"]
        name = b64decode(encodedName)
        self._name = name.decode("utf-8")

        self._is_on = data["result"]["device_on"]
        self._unique_id = data["result"]["device_id"]
        self._brightness = data["result"]["brightness"]
