""""Tapo L1510 Bulb Home Assistant Intergration"""
import logging

from PyP100 import PyP100
import voluptuous as vol
import homeassistant.helpers.config_validation as cv

from homeassistant.components.light import (
    LightEntity,
    PLATFORM_SCHEMA,
    SUPPORT_BRIGHTNESS,
    ATTR_BRIGHTNESS,
    SUPPORT_FLASH,
    ATTR_FLASH,
    FLASH_LONG,
    FLASH_SHORT
    )
from homeassistant.const import CONF_IP_ADDRESS, CONF_EMAIL, CONF_PASSWORD

import json, time

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

    add_entities([L1510Bulb(p100)])

class L1510Bulb(LightEntity):
    """Representation of a P100 Plug"""

    def __init__(self, p100):
        self._p100 = p100
        self._is_on = False
        self._brightness = 255

        self.update()

    @property
    def name(self):
        """Name of the device."""
        return self._name

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
        return SUPPORT_BRIGHTNESS | SUPPORT_FLASH

    def turn_on(self, **kwargs) -> None:
        """Turn Light On"""
        self._p100.handshake()
        self._p100.login()
        
        """ See if we are going to flash the light """
        flash = kwargs.get(ATTR_FLASH)
        if flash == None:
            newBrightness = kwargs.get(ATTR_BRIGHTNESS, 255)

            newBrightness = (newBrightness / 255) * 100

            self._p100.setBrightness(newBrightness)
            self._p100.turnOn()

            self._is_on = True
            self._brightness = kwargs.get(ATTR_BRIGHTNESS, 255)
        
        elif flash == FLASH_SHORT:
            for i in range(2):
                newBrightness = kwargs.get(ATTR_BRIGHTNESS, 255)
                newBrightness = (newBrightness / 255) * 100
                self._p100.setBrightness(newBrightness)  
                self._p100.turnOn()
                self._is_on = True
                time.sleep(1)
                self._p100.turnOff()
                time.sleep(1)
                self._is_on = False
            self._is_on = False
            self._brightness = kwargs.get(ATTR_BRIGHTNESS, 255)

        elif flash == FLASH_LONG:
            for i in range(2):
                newBrightness = kwargs.get(ATTR_BRIGHTNESS, 255)
                newBrightness = (newBrightness / 255) * 100
                self._p100.setBrightness(newBrightness)  
                self._p100.turnOn()
                self._is_on = True
                time.sleep(1)
                self._p100.turnOff()
                self._is_on = False
                time.sleep(3)
            self._is_on = False
            self._brightness = kwargs.get(ATTR_BRIGHTNESS, 255)

        else:
            _LOGGER.error("Could not determine data for turnon")


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
        self._brightness = data["result"]["brightness"]
