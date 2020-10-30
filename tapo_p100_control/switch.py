"""Tapo P100 Plug Home Assistant Intergration"""
import logging

from PyP100 import PyP100
import voluptuous as vol

import homeassistant.helpers.config_validation as cv

from homeassistant.components.switch import SwitchEntity
from homeassistant.const import CONF_IP_ADDRESS, CONF_EMAIL, CONF_PASSWORD

# Validation of the user's configuration
PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_IP_ADDRESS): cv.string,
    vol.Required(CONF_USERNAME): cv.string,
    vol.Required(CONF_PASSWORD): cv.string,
})

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
		self.is_on = False
		self.update()

	@property
    def name(self):
        """Name of the device."""
        return "Tapo P100"

    @property
    def is_on(self):
        """Name of the device."""
        return self.is_on

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
		data = self._p100.getDeviceInfo()
		self._is_on = data["device_on"]

