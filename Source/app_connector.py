import os
from typing import Any

import requests

from Source.utils.logger import setup_logger

logger = setup_logger()

SERVER_URL: str = os.getenv("SERVER_URL", "http://localhost:5000")


def hole_aktuelle_app_daten() -> dict[str, Any]:
    """
    Holt aktuelle Energiedaten vom eigenen Flask-Server.
    """
    try:
        antwort: requests.Response = requests.get(
            f"{SERVER_URL}/api/energy/current",
            timeout=10,
        )
        daten: dict[str, Any] = antwort.json()

        if antwort.status_code != 200:
            raise RuntimeError(daten.get("error", "Unbekannter Serverfehler."))

        logger.info("Aktuelle App-Daten wurden vom Server geladen.")

        return daten

    except requests.exceptions.RequestException as fehler:
        logger.error("App konnte den Flask-Server nicht erreichen: %s", fehler)
        raise RuntimeError(
            f"Flask-Server konnte nicht erreicht werden: {fehler}"
        ) from fehler


def hole_historische_app_daten() -> list[dict[str, Any]]:
    """
    Holt gespeicherte historische Professor-Snapshots vom Flask-Server.
    """
    try:
        antwort: requests.Response = requests.get(
            f"{SERVER_URL}/api/energy/history",
            timeout=10,
        )

        daten: Any = antwort.json()

        if antwort.status_code != 200:
            if isinstance(daten, dict):
                raise RuntimeError(daten.get("error", "Unbekannter Serverfehler."))

            raise RuntimeError("Unbekannter Serverfehler.")

        if not isinstance(daten, list):
            raise RuntimeError("Historische Daten haben kein Listenformat.")

        logger.info("Historische App-Daten wurden vom Server geladen.")

        return daten

    except requests.exceptions.RequestException as fehler:
        logger.error("Historische Daten konnten nicht geladen werden: %s", fehler)
        raise RuntimeError(
            f"Historische Daten konnten nicht geladen werden: {fehler}"
        ) from fehler
