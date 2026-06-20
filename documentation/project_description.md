# Projektbeschreibung

Dieses Projekt ist ein Solar-Energy-Dashboard zur Analyse von PV- und Energiedaten.

Das Dashboard kann Daten aus zwei Quellen laden:

1. CSV-Datei mit Beispiel- oder Testdaten
2. Lokaler Flask-Server mit simulierten Energiedaten

Die Daten werden bereinigt, geprüft und anschließend im Streamlit-Dashboard angezeigt. Zusätzlich werden wichtige Kennzahlen berechnet, zum Beispiel Gesamtverbrauch, Gesamterzeugung, Energiebilanz, Eigenversorgung und erspartes Geld.

Ziel des Projekts ist der Aufbau einer professionellen Projektstruktur mit Backend, Frontend, Tests, Docker und Dokumentation.

Zusätzlich ist das Backend so vorbereitet, dass echte PV-Daten von einer Professor-API geladen werden können. Die URL und der API-Key werden über eine lokale `.env`-Datei verwaltet, damit keine Zugangsdaten in das Git-Repository gelangen.