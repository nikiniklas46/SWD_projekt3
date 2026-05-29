# Projekt-3 Solar Energy Dashboard

Dieses Projekt ist ein Solar-Energy-Dashboard mit Streamlit, Flask, Pandas und Docker.

Das Dashboard kann Energiedaten aus einer CSV-Datei oder von einem lokalen Server laden. Danach werden Kennzahlen wie Gesamtverbrauch, Gesamterzeugung, Bilanz, Eigenversorgung und erspartes Geld berechnet.

## Funktionen

- Laden von Solarenergiedaten aus einer CSV-Datei
- Abrufen von simulierten Serverdaten über eine Flask-API
- Berechnung wichtiger Kennzahlen
- Darstellung der Daten in einem Streamlit-Dashboard
- Visualisierung von Verbrauch, Erzeugung und Bilanz
- Fehlerbehandlung und Logging
- Tests mit pytest
- Docker-Unterstützung mit Docker Compose

## Projektstruktur

```text
Projekt-3/
├── Source/
│   ├── app.py
│   ├── app_connector.py
│   ├── calculations.py
│   ├── data_loader.py
│   ├── data_storage.py
│   ├── server.py
│   └── utils/
│       └── logger.py
├── data/
│   └── input/
│       └── example_data.csv
├── tests/
├── documentation/
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md