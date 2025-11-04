# Termo Bucuresti pentru Home Assistant

Monitorizează întreruperile la apă și căldură de la Termoenergetica București direct în Home Assistant.

## Instalare via HACS

1. Deschide HACS în Home Assistant
2. Click pe "Integrări Custom"
3. Click pe ⋮ (trei puncte) și selectează "Repository-uri custom"
4. Adaugă: `https://github.com/username/termo_bucuresti_homeassistant`
5. Selectează categoria "Integration"
6. Caută "Termo Bucuresti" și instalează

## Configurare

1. Restartează Home Assistant
2. Mergi la Setări → Dispozitive & Servicii
3. Click pe "+ Adaugă Integrare" 
4. Caută "Termo Bucuresti"
5. Introdu numele străzii tale

## Senzori

- `sensor.termo_apa_strada` - Starea apei
- `sensor.termo_caldura_strada` - Starea căldurii
