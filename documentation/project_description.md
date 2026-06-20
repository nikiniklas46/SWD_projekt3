# Projektbeschreibung

## Projekttitel

Solar Energy Dashboard für PV-Daten

## Ziel des Projekts

Ziel des Projekts ist die Entwicklung eines Dashboards zur Anzeige und Auswertung von PV-Daten.

Die Anwendung ruft aktuelle Photovoltaik-Werte über eine externe Professor-API ab, verarbeitet diese Daten in einem eigenen Backend und stellt sie anschließend in einem Streamlit-Dashboard dar.

## Aufgabenstellung

Das Projekt erfüllt folgende zentrale Anforderungen:

- Backend-Server zum Abruf aktueller PV-Werte aus einer URL
- Data-Cleaning-Modul
- Data-Storage-Modul
- Berechnungsmodul
- Streamlit-Frontend-Dashboard
- Logging und Error Handling
- Modularisierte Python-Struktur
- Unit- und Integrationstests
- Docker- und docker-compose-Unterstützung
- GitHub-Actions-CI
- Dokumentation und Installationsanleitung
- Sicherer Umgang mit URL und Credentials über `.env` und `.gitignore`

## Datenquelle

Die Daten werden über die Professor-API abgerufen:


https://jupyterhub-wi.rz.fh-ingolstadt.de:8443/data