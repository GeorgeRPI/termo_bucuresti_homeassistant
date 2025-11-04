"""Termo Bucuresti."""
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up from config entry."""
    await hass.config_entries.async_forward_entry_setups(entry, ["sensor"])
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload config entry."""
    await hass.config_entries.async_unload_platforms(entry, ["sensor"])
    return True

# În __init__.py - adaugă storage pentru istoric
from homeassistant.helpers.storage import Store

class TermoData:
    """Stochează istoricul întreruperilor."""
    
    def __init__(self, hass: HomeAssistant):
        self.hass = hass
        self.store = Store(hass, 1, "termo_bucuresti_history")
        self.history = []
    
    async def load(self):
        """Încarcă istoricul."""
        data = await self.store.async_load()
        self.history = data.get("interruptions", []) if data else []
    
    async def save_interruption(self, interruption_data: dict):
        """Salvează o întrerupere în istoric."""
        self.history.append({
            "timestamp": dt_util.now().isoformat(),
            **interruption_data
        })
        # Păstrează doar ultimele 10 de intrări
        self.history = self.history[-10:]
        await self.store.async_save({"interruptions": self.history})
