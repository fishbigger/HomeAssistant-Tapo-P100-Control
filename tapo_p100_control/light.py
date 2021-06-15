"""Tapo L510 Bulb Home Assistant Integration"""
import logging

from PyP100 import PyP100
import voluptuous as vol

import homeassistant.helpers.config_validation as cv

from homeassistant.components.light import (
    LightEntity,
    PLATFORM_SCHEMA,
    SUPPORT_BRIGHTNESS,
    SUPPORT_COLOR,
    SUPPORT_COLOR_TEMP,
    ATTR_BRIGHTNESS,
    ATTR_COLOR_TEMP,
    ATTR_HS_COLOR,
    ATTR_KELVIN
    )
from homeassistant.const import CONF_IP_ADDRESS, CONF_EMAIL, CONF_PASSWORD

from homeassistant.util.color import (
    color_temperature_kelvin_to_mired as kelvin_to_mired,
    color_temperature_mired_to_kelvin as mired_to_kelvin,
)

import json

MODEL_L530 = "L530 Series"

SUPPORT_L510 = SUPPORT_BRIGHTNESS
SUPPORT_L530 = SUPPORT_BRIGHTNESS | SUPPORT_COLOR | SUPPORT_COLOR_TEMP

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
    	_LOGGER.error("Could not connect to bulb. Possibly invalid credentials")

    add_entities([L510Bulb(p100)])

class L510Bulb(LightEntity):
    """Representation of a L510/L530 bulb"""

    def __init__(self, p100):
        self._p100 = p100
        self._is_on = False
        self._brightness = 255
        self._color_temp = None
        self._hs_color = None
        self._model = "L510 Series"

        self._max_kelvin = 6500
        self._min_kelvin = 2500
        self._max_mireds = kelvin_to_mired(self._min_kelvin)
        self._min_mireds = kelvin_to_mired(self._max_kelvin)

        self.update()

    @property
    def name(self):
        """Name of the device."""
        return self._name

    @property
    def is_on(self):
        """Turn bulb on"""
        return self._is_on

    @property
    def brightness(self):
        """Return the brightness of this light between 1..255."""
        if self._brightness:
            brightness255 = 255 * self._brightness / 100
            return brightness255

    @property
    def color_temp(self):
        """Return current color temperature in mireds"""
        if self._color_temp:
            mired_color_temp = kelvin_to_mired(self._color_temp)
            return mired_color_temp

    @property
    def min_mireds(self):
        """Return minimum supported color temperature."""
        return self._min_mireds

    @property
    def max_mireds(self):
        """Return maximum supported color temperature."""
        return self._max_mireds

    @property
    def hs_color(self):
        """Return current color (hue and saturation)"""
        if self._hs_color:
            return self._hs_color

    @property
    def supported_features(self):
        """Flag supported features."""
        if self._model == MODEL_L530:
            return SUPPORT_L530
        else:
            return SUPPORT_L510

    def set_brightness(self, brightness):
        """Set bulb's brightness"""
        if brightness:
            _LOGGER.debug("Setting brightness: %s", brightness)
            brightness100 = round(100 * brightness / 255)
            _LOGGER.debug("Convert brightness to: %s", brightness100)
            self._p100.setBrightness( brightness100 )

    def set_color_temp(self, color_temp):
        """Set bulb's color temperature"""
        if color_temp and self.supported_features & SUPPORT_COLOR_TEMP:
            temp_in_k = mired_to_kelvin(color_temp)

            # Conversion can give value out of range at the extremes
            if temp_in_k > self._max_kelvin:
                temp_in_k = self._max_kelvin
            elif temp_in_k < self._min_kelvin:
                temp_in_k = self._min_kelvin

            _LOGGER.debug("Setting color temp: %s K", temp_in_k)
            self._p100.setColorTemp(temp_in_k)

    def set_hs_color(self, hs_color):
        """Set bulb's color"""
        if hs_color and self.supported_features & SUPPORT_COLOR:
            _LOGGER.debug("Setting hue sat color: %s", hs_color)
            self._p100.setColor(hs_color[0], hs_color[1])

    def turn_on(self, **kwargs) -> None:
        """Turn bulb on"""
        brightness = kwargs.get(ATTR_BRIGHTNESS)
        color_temp = kwargs.get(ATTR_COLOR_TEMP)
        hs_color = kwargs.get(ATTR_HS_COLOR)

        self._p100.handshake()
        self._p100.login()

        # Only turn on if effects aren't being set, as they turn the bulb on anyway
        if brightness or color_temp or hs_color:
            _LOGGER.debug("Trying brightness: %s, color temp: %s, hue-sat: %s", brightness, color_temp, hs_color)
            try:
                # values checked for none in methods
                self.set_brightness(brightness)
                self.set_color_temp(color_temp)
                self.set_hs_color(hs_color)
            except:
                _LOGGER.error("Unable to set bulb properties")
        else:
            _LOGGER.debug("Turning bulb on")
            self._p100.turnOn()

        self._is_on = True
        self._brightness = brightness
        # Need to check, as function gives error if color_temp is None
        if color_temp:
            self._color_temp = mired_to_kelvin(color_temp)
        self._hs_color = hs_color

    def turn_off(self, **kwargs):
        """Turn bulb off"""
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
        self._model = data["result"]["model"]
        self._brightness = data["result"]["brightness"]
        try:
            self._color_temp = data["result"]["color_temp"]
            if self._color_temp == 0:
                self._color_temp = None
        except KeyError:
            self._color_temp = None
        try:
            self._hs_color = ( data["result"]["hue"], data["result"]["saturation"] )
        except KeyError:
            self._hs_color = None
