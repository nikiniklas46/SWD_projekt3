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
Projekt-3-und-4/
├── .github/
│   └── workflows/
│       └── ci.yml
├── data/
│   ├── input/
│   │   └── example_data.csv
│   └── output/
│       └── README.md
├── documentation/
│   ├── Architecture.md
│   ├── Dashboard_specs.md
│   ├── project_description.md
│   └── task_distribution.md
├── Source/
│   ├── __init__.py
│   ├── app.py
│   ├── app_connector.py
│   ├── calculations.py
│   ├── data_loader.py
│   ├── data_storage.py
│   ├── server.py
│   └── utils/
│       ├── __init__.py
│       └── logger.py
├── tests/
│   ├── test_calculations.py
│   ├── test_data_loader.py
│   └── test_integration.py
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .gitignore
└── README.md