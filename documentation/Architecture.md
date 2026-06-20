# Architektur

Das Projekt ist in mehrere Bereiche aufgeteilt.

## Backend

Der Backend-Server befindet sich in:

Source/server.py

## Professor-Server und API-Anbindung

Der Backend-Server in `Source/server.py` ist so vorbereitet, dass er PV-Daten von einer externen Professor-URL abrufen kann.

Die Zugangsdaten werden nicht direkt im Code gespeichert. Stattdessen werden sie über eine lokale `.env`-Datei geladen:

```text
PROFESSOR_API_URL=...
PROFESSOR_API_KEY=...
USE_MOCK_DATA=false