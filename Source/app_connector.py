import os
from typing import Any

import pandas as pd
import requests
import streamlit as st

from Source.utils.logger import setup_logger

logger = setup_logger()

SERVER_URL: str = os.getenv("SERVER_URL", "http://127.0.0.1:5000")


def hole_aktuelle_app_daten() -> dict[str, Any]:
    """
    Holt aktuelle Energiedaten vom lokalen Server.

    Returns:
        dict[str, Any]: Aktuelle Energiedaten mit Verbrauch und Erzeugung.
    """
    try:
        antwort: requests.Response = requests.get(
            f"{SERVER_URL}/api/energy/current",
            timeout=5,
        )
        antwort.raise_for_status()

        daten: dict[str, Any] = antwort.json()

    except requests.exceptions.ConnectionError:
        logger.error("Keine Verbindung zum Server möglich.")
        st.error("Keine Verbindung zum Server. Bitte starte zuerst server.py.")
        st.stop()

    except requests.exceptions.Timeout:
        logger.error("Zeitüberschreitung beim Abrufen der Serverdaten.")
        st.error("Der Server antwortet nicht rechtzeitig.")
        st.stop()

    except requests.exceptions.JSONDecodeError:
        logger.error("Serverantwort konnte nicht als JSON gelesen werden.")
        st.error("Die Serverantwort hat kein gültiges JSON-Format.")
        st.stop()

    except requests.exceptions.RequestException as fehler:
        logger.exception("Fehler beim Abrufen der aktuellen Energiedaten.")
        st.error(f"Fehler beim Abrufen der Serverdaten: {fehler}")
        st.stop()

    if "verbrauch" not in daten or "erzeugung" not in daten:
        logger.error("Serverantwort enthält nicht die erwarteten Werte.")
        st.error("Serverdaten sind unvollständig. Erwartet: verbrauch und erzeugung.")
        st.stop()

    try:
        daten["verbrauch"] = float(daten["verbrauch"])
        daten["erzeugung"] = float(daten["erzeugung"])

    except (TypeError, ValueError):
        logger.error("Serverdaten enthalten ungültige Zahlenwerte.")
        st.error("Serverdaten enthalten ungültige Zahlenwerte.")
        st.stop()

    if daten["verbrauch"] < 0 or daten["erzeugung"] < 0:
        logger.error("Serverdaten enthalten negative Werte.")
        st.error("Serverdaten enthalten negative Energiewerte.")
        st.stop()

    logger.info("Aktuelle Energiedaten wurden erfolgreich vom Server geladen.")

    return daten


def hole_historische_app_daten() -> pd.DataFrame:
    """
    Holt historische Energiedaten vom lokalen Server.

    Returns:
        pd.DataFrame: Historische Energiedaten mit Datum, Verbrauch und Erzeugung.
    """
    try:
        antwort: requests.Response = requests.get(
            f"{SERVER_URL}/api/energy/history",
            timeout=5,
        )
        antwort.raise_for_status()

        server_daten: Any = antwort.json()

    except requests.exceptions.ConnectionError:
        logger.error("Keine Verbindung zum Server möglich.")
        st.error("Keine Verbindung zum Server. Bitte starte zuerst server.py.")
        st.stop()

    except requests.exceptions.Timeout:
        logger.error("Zeitüberschreitung beim Abrufen der Serverdaten.")
        st.error("Der Server antwortet nicht rechtzeitig.")
        st.stop()

    except requests.exceptions.JSONDecodeError:
        logger.error("Serverantwort konnte nicht als JSON gelesen werden.")
        st.error("Die Serverantwort hat kein gültiges JSON-Format.")
        st.stop()

    except requests.exceptions.RequestException as fehler:
        logger.exception("Fehler beim Abrufen der historischen Energiedaten.")
        st.error(f"Fehler beim Abrufen der Serverdaten: {fehler}")
        st.stop()

    if not isinstance(server_daten, list):
        logger.error("Historische Serverdaten sind keine Liste.")
        st.error("Historische Serverdaten haben ein ungültiges Format.")
        st.stop()

    daten: pd.DataFrame = pd.DataFrame(server_daten)

    erwartete_spalten: list[str] = ["datum", "verbrauch", "erzeugung"]
    fehlende_spalten: list[str] = [
        spalte for spalte in erwartete_spalten if spalte not in daten.columns
    ]

    if fehlende_spalten:
        logger.error("Fehlende Spalten in Serverdaten: %s", fehlende_spalten)
        st.error(f"Diese Spalten fehlen in den Serverdaten: {fehlende_spalten}")
        st.stop()

    daten["datum"] = pd.to_datetime(
        daten["datum"],
        errors="coerce",
    )

    daten["verbrauch"] = pd.to_numeric(
        daten["verbrauch"],
        errors="coerce",
    )

    daten["erzeugung"] = pd.to_numeric(
        daten["erzeugung"],
        errors="coerce",
    )

    daten = daten.dropna(
        subset=["datum", "verbrauch", "erzeugung"],
    )

    if daten.empty:
        logger.error("Nach Bereinigung sind keine gültigen Serverdaten vorhanden.")
        st.error("Nach Bereinigung sind keine gültigen Serverdaten vorhanden.")
        st.stop()

    if (daten["verbrauch"] < 0).any() or (daten["erzeugung"] < 0).any():
        logger.error("Serverdaten enthalten negative Energiewerte.")
        st.error("Serverdaten enthalten negative Energiewerte.")
        st.stop()

    daten = daten.sort_values("datum")
    daten["bilanz"] = daten["erzeugung"] - daten["verbrauch"]

    logger.info("Historische Energiedaten wurden erfolgreich vom Server geladen.")

    return daten