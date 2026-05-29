import os
from random import uniform
from typing import Any

import requests
from flask import Flask, jsonify

from Source.utils.logger import setup_logger

logger = setup_logger()

app: Flask = Flask(__name__)

PROFESSOR_URL: str = os.getenv("PROFESSOR_URL", "")


def simuliere_aktuelle_energiedaten() -> dict[str, float]:
    """
    Erstellt simulierte aktuelle Energiedaten.

    Returns:
        dict[str, float]: Simulierte Werte für Verbrauch und Erzeugung.
    """
    verbrauch: float = round(uniform(8.0, 25.0), 2)
    erzeugung: float = round(uniform(5.0, 30.0), 2)

    return {
        "verbrauch": verbrauch,
        "erzeugung": erzeugung,
    }


def hole_professor_daten() -> dict[str, float]:
    """
    Holt aktuelle PV-Daten von einer externen Professor-URL.

    Wenn keine Professor-URL gesetzt ist oder ein Fehler passiert,
    werden simulierte Daten verwendet.

    Returns:
        dict[str, float]: Aktuelle Energiedaten.
    """
    if not PROFESSOR_URL:
        logger.info("Keine Professor-URL gesetzt. Mock-Daten werden verwendet.")
        return simuliere_aktuelle_energiedaten()

    try:
        antwort: requests.Response = requests.get(
            PROFESSOR_URL,
            timeout=5,
        )
        antwort.raise_for_status()

        daten: dict[str, Any] = antwort.json()

        return {
            "verbrauch": float(daten["verbrauch"]),
            "erzeugung": float(daten["erzeugung"]),
        }

    except (
        requests.exceptions.RequestException,
        KeyError,
        TypeError,
        ValueError,
    ) as fehler:
        logger.warning(
            "Professor-Daten konnten nicht geladen werden. Mock-Daten werden verwendet: %s",
            fehler,
        )
        return simuliere_aktuelle_energiedaten()


@app.route("/")
def startseite() -> dict[str, str]:
    """
    Gibt eine einfache Startnachricht zurück.

    Returns:
        dict[str, str]: Nachricht, dass der Server läuft.
    """
    logger.info("Startseite des Servers wurde aufgerufen.")

    return {
        "message": "Solar Energy Server läuft."
    }


@app.route("/api/energy/current")
def aktuelle_energiedaten() -> Any:
    """
    Gibt aktuelle Energiedaten zurück.

    Die Daten kommen entweder von einer externen Professor-URL
    oder aus simulierten Mock-Daten.

    Returns:
        Any: JSON-Antwort mit Verbrauch und Erzeugung.
    """
    daten: dict[str, float] = hole_professor_daten()

    logger.info("Aktuelle Energiedaten wurden bereitgestellt.")

    return jsonify(daten)


@app.route("/api/energy/history")
def historische_energiedaten() -> Any:
    """
    Simuliert historische Energiedaten für mehrere Tage.

    Returns:
        Any: JSON-Antwort mit mehreren Energiedaten.
    """
    daten: list[dict[str, float | str]] = []

    for tag in range(1, 15):
        verbrauch: float = round(uniform(8.0, 25.0), 2)
        erzeugung: float = round(uniform(5.0, 30.0), 2)

        daten.append(
            {
                "datum": f"2025-01-{tag:02d}",
                "verbrauch": verbrauch,
                "erzeugung": erzeugung,
            }
        )

    logger.info("Historische Energiedaten wurden bereitgestellt.")

    return jsonify(daten)


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True,
    )