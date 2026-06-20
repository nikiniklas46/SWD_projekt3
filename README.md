# Solar Energy Dashboard

Dieses Projekt ist ein PV-Dashboard zur Anzeige und Auswertung aktueller Photovoltaik-Daten.

Das Dashboard besteht aus einem Flask-Backend, das aktuelle PV-Werte von einer externen Professor-API abruft, und einem Streamlit-Frontend, das die Daten visualisiert. Die Anwendung speichert regelmäßig Snapshots der Momentanwerte und berechnet daraus Tages-, Monats- und Jahreskennzahlen.

## Funktionen

- Abruf echter PV-Daten über die Professor-API
- Eigener Flask-Server als Backend
- Streamlit-Dashboard als Frontend
- Speicherung von Professor-API-Snapshots
- Berechnung von Momentan-, Tages-, Monats- und Jahreswerten
- Verhältnis Verbrauch aus PV zu Gesamtverbrauch für Tag, Monat und Jahr
- Zeitverlaufsdiagramm für Tageserzeugung und Tagesverbrauch
- Torten-/Donutdiagramme für den PV-Anteil
- Dark-Mode-Design
- Logging und Error Handling
- Unit- und Integrationstests
- Docker- und docker-compose-Unterstützung
- GitHub-Actions-CI mit pytest, Black und Ruff

## Projektstruktur

```text
SWD_projekt3/
├── .github/
│   └── workflows/
│       └── ci.yml
├── .streamlit/
│   └── config.toml
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
│   ├── test_app_connector.py
│   ├── test_calculations.py
│   ├── test_data_loader.py
│   ├── test_data_storage.py
│   ├── test_integration.py
│   ├── test_pv_calculation.py
│   └── test_server.py
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```