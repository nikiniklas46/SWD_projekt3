
---

## `documentation/dashboard_specification.md`

```markdown
# Dashboard-Spezifikation

Das Dashboard zeigt Solar- und Energiedaten übersichtlich an.

## Datenquellen

Das Dashboard unterstützt zwei Datenquellen:

- CSV-Datei
- Server-Daten über Flask-API

## Kennzahlen

Folgende Kennzahlen werden berechnet und angezeigt:

- Gesamtverbrauch
- Gesamterzeugung
- Gesamtbilanz
- Eigenversorgung in Prozent
- Erspartes Geld
- Durchschnittlicher Verbrauch pro Tag
- Durchschnittliche Erzeugung pro Tag
- Anzahl erfasster Tage
- Gesamtstatus, zum Beispiel Überschuss oder Netzbezug

## Visualisierungen

Das Dashboard enthält:

- Tabelle mit den geladenen Daten
- Liniendiagramm für Verbrauch und Erzeugung
- Balkendiagramm für die Bilanz

## Fehlerbehandlung

Ungültige CSV-Dateien, fehlende Spalten, negative Werte oder Serverprobleme werden erkannt und dem Benutzer angezeigt.