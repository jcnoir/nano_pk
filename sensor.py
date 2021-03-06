"""Platform for sensor integration."""
from homeassistant.const import TEMP_CELSIUS
from homeassistant.helpers.entity import Entity
from datetime import timedelta

from apscheduler.schedulers.background import BackgroundScheduler
from telnetlib import Telnet
import xml.etree.ElementTree as xml
from custom_components.nano_pk.hargassner import HargassnerBridge



SCAN_INTERVAL = timedelta(seconds=5)

def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the sensor platform."""
    bridge = HargassnerBridge("192.168.0.161", updateInterval=SCAN_INTERVAL.total_seconds())
#    entities = []
#    for p in bridge.getSupportedParameters(): entities.append(HargassnerSensor(bridge, p, p))
#    add_entities(entities)
    add_entities([
        HargassnerStateSensor(bridge),
        HargassnerSensor(bridge, "boiler temperature", "TK"),
        HargassnerSensor(bridge, "smoke gas temperature", "TRG"),
        HargassnerSensor(bridge, "output", "Leistung", "mdi:fire"),
        HargassnerSensor(bridge, "outside temperature", "Taus"),
        HargassnerSensor(bridge, "buffer temperature 0", "TB1", "mdi:coolant-temperature"),
        HargassnerSensor(bridge, "buffer temperature 1", "TPo", "mdi:coolant-temperature"),
        HargassnerSensor(bridge, "buffer temperature 2", "TPm", "mdi:coolant-temperature"),
        HargassnerSensor(bridge, "buffer temperature 3", "TPu", "mdi:coolant-temperature"),
        HargassnerSensor(bridge, "return temperature", "TRL"),
        HargassnerSensor(bridge, "buffer level", "Puff Füllgrad", "mdi:gauge"),
        HargassnerSensor(bridge, "pellet consumption", "Verbrauchszähler", "mdi:basket-unfill"), # "mdi:arrow-down-box", "mdi:pail-minus", "mdi:transfer-down", "mdi:tranding-down"
        HargassnerSensor(bridge, "flow temperature", "TVL_1"),
        HargassnerSensor(bridge, "error", "Störung", "mdi:alert")
    ])


class HargassnerSensor(Entity):
    """Representation of a Sensor."""

    def __init__(self, bridge, description, paramName, icon=None):
        """Initialize the sensor."""
        self._state = None
        self._bridge = bridge
        self._description = description
        self._paramName = paramName
        self._icon = icon
        self._unit = bridge.getUnit(paramName)

    @property
    def name(self):
        """Return the name of the sensor."""
        return "Nano-PK " + self._description

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return self._unit

    @property
    def icon(self):
        """Return an icon for the sensor in the GUI."""
        return self._icon

    def update(self):
        """Fetch new state data for the sensor.
        This is the only method that should fetch new data for Home Assistant.
        """
        self._state = self._bridge.getValue(self._paramName)


class HargassnerStateSensor(HargassnerSensor):

    STATES = {"1":"Aus", "3":"Kessel Start", "4":"Zündüberwachung", "5":"Zündung", "6":"Übergang LB", "7":"Leistungsbrand", "10":"Entaschung", "12":"Putzen"}

    def __init__(self, bridge):
        super().__init__(bridge, "state", "ZK")

    def update(self):
        """Fetch new state data for the sensor.
        This is the only method that should fetch new data for Home Assistant.
        """
        rawState = self._bridge.getValue(self._paramName)
        self._state = self.STATES.get(rawState)
        if self._state==None: self._state = "Unbekannt (" + (str)(rawState) + ")"
        if rawState=="6" or rawState=="7": self._icon = "mdi:fireplace"
        else: self._icon = "mdi:fireplace-off"
