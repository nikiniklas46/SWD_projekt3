# Dashboard-Spezifikation

## Ziel

Das Dashboard zeigt aktuelle PV-Daten und berechnete Kennzahlen zu Verbrauch und Erzeugung an.

Die Daten stammen von der Professor-API und werden über das eigene Flask-Backend bereitgestellt. Das Dashboard selbst greift nicht direkt auf die Professor-API zu.

## Datenquellen

Das Dashboard unterstützt zwei Datenquellen:

- Professor-Server-Daten
- CSV-Beispieldaten

Die Professor-Server-Daten sind die Hauptdatenquelle für das finale Dashboard.

Die CSV-Beispieldaten dienen als zusätzliche Demonstration des Data-Cleaning-Moduls.

## Aktualisierung

Das Dashboard kann automatisch aktualisiert werden.

Das Aktualisierungsintervall kann in der Sidebar eingestellt werden. Bei jeder Aktualisierung fragt das Dashboard den eigenen Flask-Server ab.

Der Flask-Server ruft anschließend die Professor-API ab und speichert die erhaltenen Werte als Snapshot.

## Geforderte Kennzahlen

Das Dashboard zeigt folgende geforderte Kennzahlen:

- Momentanverbrauch
- Momentanerzeugung
- Tagesverbrauch des aktuellen Tages
- Tageserzeugung des aktuellen Tages
- Monatsverbrauch
- Monatserzeugung
- Jahresverbrauch
- Jahreserzeugung
- Verhältnis Verbrauch aus PV zu Gesamtverbrauch für den Tag
- Verhältnis Verbrauch aus PV zu Gesamtverbrauch für den Monat
- Verhältnis Verbrauch aus PV zu Gesamtverbrauch für das Jahr

## Einheiten

Die Professor-API liefert momentane Leistungswerte in Watt.

Momentanwerte werden im Dashboard als Leistung angezeigt:

kW