# Architektur

## Überblick

Das Projekt besteht aus einem Backend, einem Frontend und mehreren unterstützenden Modulen.

Das Backend ruft aktuelle PV-Daten von der Professor-API ab. Die Daten werden normalisiert, als Snapshots gespeichert und anschließend vom Dashboard verwendet.


Professor-API
→ Flask-Backend
→ Data Storage
→ Calculation Module
→ Streamlit-Dashboard