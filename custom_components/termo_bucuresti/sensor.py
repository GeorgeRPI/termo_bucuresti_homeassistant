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
        TermoSensor(strada, "apă caldă"),
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
            
            _LOGGER.info("Încerc conectare la CMTEB pentru strada: %s", self._strada)
            
            # Headers pentru a evita blocarea
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            async with session.get(
                "https://www.cmteb.ro/functionare_sistem_termoficare.php",
                headers=headers,
                timeout=30
            ) as response:
                _LOGGER.info("Status response: %s", response.status)
                
                if response.status == 200:
                    text = await response.text()
                    _LOGGER.info("Conectare reușită, procesez conținutul")
                    await self._process_page_content(text)
                else:
                    _LOGGER.warning("Site-ul a returnat status: %s", response.status)
                    self._attr_native_value = f"Eroare HTTP {response.status}"
                    self._attr_available = False
                    
        except asyncio.TimeoutError:
            _LOGGER.warning("Timeout la conectare la CMTEB")
            self._attr_native_value = "Timeout"
            self._attr_available = False
        except Exception as e:
            _LOGGER.error("Eroare la conectare la CMTEB: %s", str(e))
            self._attr_native_value = "Eroare conexiune"
            self._attr_available = False

    async def _process_page_content(self, text: str):
        """Process the HTML content."""
        try:
            text_lower = text.lower()
            strada_lower = self._strada.lower()
            
            _LOGGER.debug("Text extras din pagină (primele 300 caractere): %s", text_lower[:300])
            
            # Verifică dacă strada apare pe pagină
            if strada_lower in text_lower:
                _LOGGER.info("Strada '%s' GĂSITĂ pe pagină", self._strada)
                
                if self._service_type == "apă":
                    service_keywords = ['apă', 'apa', 'apei', 'apă potabilă', 'serviciu apă']
                    service_found = any(keyword in text_lower for keyword in service_keywords)
                    
                    if service_found:
                        self._attr_native_value = "Oprită"
                        _LOGGER.info("✅ Întrerupere APĂ detectată pentru %s", self._strada)
                    else:
                        self._attr_native_value = "Normal"
                        _LOGGER.info("✅ Serviciu APĂ normal pentru %s", self._strada)
                else:
                    service_keywords = ['căldură', 'caldura', 'caldurii', 'încălzire', 'serviciu căldură']
                    service_found = any(keyword in text_lower for keyword in service_keywords)
                    
                    if service_found:
                        self._attr_native_value = "Oprită"
                        _LOGGER.info("✅ Întrerupere CĂLDURĂ detectată pentru %s", self._strada)
                    else:
                        self._attr_native_value = "Normal"
                        _LOGGER.info("✅ Serviciu CĂLDURĂ normal pentru %s", self._strada)
            else:
                _LOGGER.info("Strada '%s' NU a fost găsită pe pagină - servicii normale", self._strada)
                self._attr_native_value = "Normal"
            
            self._attr_available = True
            
        except Exception as e:
            _LOGGER.error("Eroare la procesarea conținutului: %s", e)
            self._attr_native_value = "Eroare procesare"
            self._attr_available = False