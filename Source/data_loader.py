from typing import Any

import pandas as pd
import streamlit as st

from Source.utils.logger import setup_logger

logger = setup_logger()


def lade_daten(dateiquelle: Any = "data/input/example_data.csv") -> pd.DataFrame:  #
    """
    Lädt eine CSV-Datei mit Solarenergiedaten, überprüft sie auf Fehler
    und bereitet die Daten für die Analyse vor.

    Die Funktion führt folgende Schritte aus:
    - Einlesen der CSV-Datei
    - Überprüfung auf typische Fehler
    - Umbenennen und Bereinigen der Spalten
    - Konvertierung der Datentypen
    - Entfernen fehlerhafter oder unvollständiger Zeilen
    - Validierung der Daten, zum Beispiel keine negativen Werte
    - Hinzufügen der Bilanz und Kalenderwoche

    Parameters:
        dateiquelle (Any): Dateipfad als String oder hochgeladene Datei aus Streamlit.

    Returns:
        pd.DataFrame: Bereinigter und vorbereiteter Datensatz.
    """
    try:
        daten: pd.DataFrame = pd.read_csv(dateiquelle)

    except FileNotFoundError:
        logger.error("Datei wurde nicht gefunden.")
        st.error("Die CSV-Datei wurde nicht gefunden.")
        st.stop()

    except pd.errors.EmptyDataError:
        logger.error("CSV-Datei ist leer.")
        st.error("Die CSV-Datei ist leer.")
        st.stop()

    except pd.errors.ParserError:
        logger.error("CSV-Datei konnte nicht korrekt gelesen werden.")
        st.error("Die CSV-Datei hat ein ungültiges Format.")
        st.stop()

    except Exception as fehler:
        logger.exception("Unbekannter Fehler beim Laden der CSV-Datei.")
        st.error(f"Unbekannter Fehler beim Laden der Datei: {fehler}")
        st.stop()

    daten.columns = daten.columns.str.strip()

    daten = daten.rename(  # Spaltennamen vereinheitlichen, damit sie später leichter zu verwenden sind
        columns={
            "Datum": "datum",
            "datum": "datum",
            "Verbrauch(kWh)": "verbrauch",
            "Verbrauch_kWh": "verbrauch",
            "Verbrauch": "verbrauch",
            "verbrauch": "verbrauch",
            "Erzeugung(kWh)": "erzeugung",
            "Erzeugung_kWh": "erzeugung",
            "Erzeugung": "erzeugung",
            "erzeugung": "erzeugung",
        }
    )

    erwartete_spalten: list[str] = ["datum", "verbrauch", "erzeugung"]

    fehlende_spalten: list[str] = [
        spalte for spalte in erwartete_spalten if spalte not in daten.columns
    ]

    if fehlende_spalten:
        logger.error("Fehlende Spalten in CSV: %s", fehlende_spalten)
        st.error(f"Diese Spalten fehlen in deiner CSV: {fehlende_spalten}")
        st.write("Gefundene Spaltennamen:", list(daten.columns))
        st.stop()

    daten["datum"] = (
        pd.to_datetime(  # Datumsspalte werden konvertiert, Fehlerhafte Werte werden zu NaT
            daten["datum"],
            errors="coerce",
        )
    )

    daten["verbrauch"] = pd.to_numeric(
        daten["verbrauch"],
        errors="coerce",
    )

    daten["erzeugung"] = pd.to_numeric(
        daten["erzeugung"],
        errors="coerce",
    )

    fehlerhafte_zeilen: pd.DataFrame = daten[
        daten[["datum", "verbrauch", "erzeugung"]].isna().any(axis=1)
    ]

    if not fehlerhafte_zeilen.empty:
        logger.warning(
            "%s fehlerhafte oder unvollständige Zeilen wurden entfernt.",
            len(fehlerhafte_zeilen),
        )

    daten = daten.dropna(
        subset=["datum", "verbrauch", "erzeugung"],
    )

    if daten.empty:
        logger.error("Nach der Bereinigung sind keine gültigen Daten vorhanden.")
        st.error("Nach der Bereinigung sind keine gültigen Daten vorhanden.")
        st.stop()

    if (daten["verbrauch"] < 0).any() or (daten["erzeugung"] < 0).any():
        logger.error("Negative Energiewerte wurden gefunden.")
        st.error("Die CSV enthält negative Energiewerte. Bitte Datei prüfen.")
        st.stop()

    daten = daten.sort_values(
        "datum"
    )  # Daten nach Datum sortieren, damit sie in der Analyse chronologisch sind

    daten["bilanz"] = daten["erzeugung"] - daten["verbrauch"]  # Bilanzspalte hinzufügen
    daten["woche"] = (
        daten["datum"].dt.isocalendar().week.astype(int)
    )  # Kalenderwoche hinzufügen

    logger.info("Solarenergiedaten erfolgreich geladen und bereinigt.")

    return daten
