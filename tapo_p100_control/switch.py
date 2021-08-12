"""Tapo L1510 Bulb Home Assistant Intergration"""
import logging

from PyP100 import PyP100
import voluptuous as vol

import homeassistant.helpers.config_validation as cv

from homeassistant.components.switch import (
    SwitchEntity,
    PLATFORM_SCHEMA,
    )
from homeassistant.const import CONF_IP_ADDRESS, CONF_EMAIL, CONF_PASSWORD
from homeassistant.helpers.device_registry import format_mac

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
    p100 = PyP100.P100(ipAddress, email, password)

    try:
        p100.handshake()
        p100.login()
    except:
        _LOGGER.error("Could not connect to plug. Possibly invalid credentials")

    add_entities([P100Plug(p100)])

class P100Plug(SwitchEntity):
    """Representation of a P100 Plug"""

    def __init__(self, p100):
        self._p100 = p100
        self._is_on = False

        self.update()

    @property
    def name(self):
        """Name of the device."""
        return self._name

    @property
    def unique_id(self):
        """Unique ID of the device. Uses device MAC."""
        return self._mac

    @property
    def is_on(self):
        """Name of the device."""
        return self._is_on

    def turn_on(self, **kwargs) -> None:
        """Turn Plug On"""
        self._p100.handshake()
        self._p100.login()

        self._p100.turnOn()

        self._is_on = True

    def turn_off(self, **kwargs):
        """Turn Plug Off"""
        self._p100.handshake()
        self._p100.login()
        self._p100.turnOff()

        self._is_on = False

    def update(self):
        self._p100.handshake()
        self._p100.login()

        self._name = self._p100.getDeviceName()

        data = json.loads(self._p100.getDeviceInfo())

        self._is_on = data["result"]["device_on"]
        self._mac = format_mac(data["result"]["mac"])
