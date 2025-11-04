"""Sensor for Termo Bucuresti."""
from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.aiohttp_client import async_get_clientsession

import asyncio
import logging

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up sensor."""
    strada = entry.data["strada"]
    async_add_entities([
        TermoSensor(strada, "apă"),
        TermoSensor(strada, "căldură")
    ])

class TermoSensor(SensorEntity):
    """Termo Sensor."""
    
    def __init__(self, strada: str, service_type: str):
        self._strada = strada
        self._service_type = service_type
        self._attr_name = f"Termo {service_type} - {strada}"
        self._attr_unique_id = f"termo_{service_type}_{strada.replace(' ', '_').replace(',', '').lower()}"
        self._attr_native_value = "Necunoscut"
        self._attr_available = True
        
        if service_type == "apă":
            self._attr_icon = "mdi:water-pump"
        else:
            self._attr_icon = "mdi:radiator"

    async def async_update(self):
        """Update sensor."""
        try:
            session = async_get_clientsession(self.hass)
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            async with session.get(
                "https://www.cmteb.ro/functionare_sistem_termoficare.php",
                headers=headers,
                timeout=30
            ) as response:
                
                if response.status == 200:
                    text = await response.text()
                    await self._process_page_content(text)
                else:
                    self._attr_native_value = f"Eroare HTTP {response.status}"
                    self._attr_available = False
                    
        except asyncio.TimeoutError:
            self._attr_native_value = "Timeout"
            self._attr_available = False
        except Exception as e:
            self._attr_native_value = "Eroare conexiune"
            self._attr_available = False

    async def _process_page_content(self, text: str):
        """Process the HTML content."""
        try:
            text_lower = text.lower()
            strada_lower = self._strada.lower()
            
            if strada_lower in text_lower:
                if self._service_type == "apă":
                    service_keywords = ['apă', 'apa', 'apei', 'apă potabilă']
                    if any(keyword in text_lower for keyword in service_keywords):
                        self._attr_native_value = "Oprită"
                    else:
                        self._attr_native_value = "Normal"
                else:
                    service_keywords = ['căldură', 'caldura', 'caldurii', 'încălzire']
                    if any(keyword in text_lower for keyword in service_keywords):
                        self._attr_native_value = "Oprită"
                    else:
                        self._attr_native_value = "Normal"
            else:
                self._attr_native_value = "Normal"
            
            self._attr_available = True
            
        except Exception:
            self._attr_native_value = "Eroare procesare"

   # În sensor.py - adaugă mai multe atribute
   self._attr_extra_state_attributes = {
       "strada": strada,
       "zona": entry.data.get("zona", "toate"),
       "stare_serviciu": "Necunoscută",
       "ultima_actualizare": None,
       "detaliu_intrerupere": "",
       "ora_estimare_final": "",
       "zona_afectata": "",
       "tip_intrerupere": "",
       "link_informatii": "https://www.cmteb.ro/functionare_sistem_termoficare.php"
   }

# Adaugă în async_setup_entry
async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up sensor."""
    strada = entry.data["strada"]
    
    sensors = [
        TermoSensor(strada, "apă"),
        TermoSensor(strada, "căldură"),
        TermoStatisticsSensor(),  # <-- Senzor nou pentru statistici
    ]
    
    async_add_entities(sensors, True)

class TermoStatisticsSensor(SensorEntity):
    """Senzor pentru statistici Termo."""
    
    def __init__(self):
        self._attr_name = "Termo Statistici"
        self._attr_unique_id = "termo_statistici_global"
        self._attr_icon = "mdi:chart-line"
        self._attr_native_value = 0
        
        self._interruption_history = []
        self._attr_extra_state_attributes = {
            "total_intreruperi": 0,
            "ultimele_24h": 0,
            "ultimele_7_zile": 0,
            "ultima_intrerupere": None,
            "durata_medie": "0h",
            "strada_cea_afectata": ""
        }

    async def async_update(self):
        """Update statistics."""
        # Aici vin datele din istoricul întreruperilor
        # Momentant exemplu cu date statice
        self._attr_native_value = len(self._interruption_history)
        self._attr_extra_state_attributes.update({
            "total_intreruperi": len(self._interruption_history),
            "ultimele_24h": 2,  # Exemplu
            "ultimele_7_zile": 5,  # Exemplu
            "ultima_intrerupere": "2024-01-15 14:30:00",
            "durata_medie": "3h",
            "strada_cea_afectata": "Victoriei"
        })
