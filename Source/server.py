import os
from datetime import datetime
from random import uniform
from typing import Any

import requests
import urllib3
from dotenv import load_dotenv
from flask import Flask, jsonify

from Source.data_storage import speichere_snapshot, snapshots_als_liste
from Source.utils.logger import setup_logger

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

load_dotenv()

logger = setup_logger()

app: Flask = Flask(__name__)

PROFESSOR_API_URL: str = (
    os.getenv("PROFESSOR_API_URL", "").strip().strip('"').strip("'")
)
PROFESSOR_API_KEY: str = (
    os.getenv("PROFESSOR_API_KEY", "").strip().strip('"').strip("'")
)
USE_MOCK_DATA: bool = os.getenv("USE_MOCK_DATA", "true").strip().lower() == "true"


def simuliere_aktuelle_energiedaten() -> dict[str, float | str]:
    """
    Erstellt simulierte aktuelle Energiedaten.

    Diese Funktion wird nur benutzt, wenn USE_MOCK_DATA=true ist.
    """
    verbrauch_w: float = round(uniform(8000.0, 25000.0), 2)
    erzeugung_w: float = round(uniform(5000.0, 30000.0), 2)

    return {
        "verbrauch": verbrauch_w,
        "erzeugung": erzeugung_w,
        "quelle": "mock_data",
        "collected_at": datetime.now().isoformat(),
    }


def normalisiere_professor_daten(serverantwort: Any) -> dict[str, float | str]:
    """
    Wandelt die Professor-Serverantwort in das interne Format um.

    Die Professor-API liefert ein Dictionary mit einer data-Liste.
    Jeder Eintrag enthält:
    - type: consumption oder generation
    - value: aktueller Leistungswert in Watt
    """
    if not isinstance(serverantwort, dict):
        raise ValueError("Die Serverantwort ist kein Dictionary.")

    if "data" not in serverantwort:
        raise KeyError("Die Serverantwort enthält keine data-Liste.")

    daten_liste: Any = serverantwort["data"]

    if not isinstance(daten_liste, list):
        raise ValueError("data ist keine Liste.")

    verbrauch_w: float = 0.0
    erzeugung_w: float = 0.0

    for eintrag in daten_liste:
        if not isinstance(eintrag, dict):
            continue

        typ: str = str(eintrag.get("type", "")).lower()
        wert: float = float(eintrag.get("value", 0.0))

        if typ == "consumption":
            verbrauch_w += wert

        elif typ == "generation":
            erzeugung_w += wert

    if verbrauch_w == 0.0 and erzeugung_w == 0.0:
        raise ValueError("Keine Verbrauchs- oder Erzeugungswerte gefunden.")

    return {
        "verbrauch": round(verbrauch_w, 2),
        "erzeugung": round(erzeugung_w, 2),
        "quelle": "professor_api",
        "collected_at": str(serverantwort.get("collected_at", "")),
    }


def hole_professor_daten() -> dict[str, float | str]:
    """
    Holt aktuelle PV-Daten vom Professor-Server.

    Wenn USE_MOCK_DATA=false ist, wird kein Mock-Fallback genutzt.
    Dadurch erkennt man sicher, ob die Professor-API wirklich funktioniert.
    """
    if USE_MOCK_DATA:
        logger.warning("Mock-Daten sind aktiviert.")
        return simuliere_aktuelle_energiedaten()

    if not PROFESSOR_API_URL or not PROFESSOR_API_KEY:
        raise RuntimeError("Professor-URL oder API-Key fehlt.")

    try:
        antwort: requests.Response = requests.get(
            PROFESSOR_API_URL,
            headers={"X-API-Key": PROFESSOR_API_KEY},
            timeout=10,
            verify=False,
        )
        antwort.raise_for_status()

        serverantwort: Any = antwort.json()
        daten: dict[str, float | str] = normalisiere_professor_daten(serverantwort)

        logger.info("Professor-Daten wurden erfolgreich geladen.")

        return daten

    except (
        requests.exceptions.RequestException,
        KeyError,
        TypeError,
        ValueError,
    ) as fehler:
        logger.error("Professor-Daten konnten nicht geladen werden: %s", fehler)
        raise RuntimeError(
            f"Professor-Daten konnten nicht geladen werden: {fehler}"
        ) from fehler


@app.route("/")
def startseite() -> dict[str, str]:
    """
    Gibt eine einfache Startnachricht zurück.
    """
    logger.info("Startseite des Servers wurde aufgerufen.")

    return {
        "message": "Solar Energy Server läuft.",
    }


@app.route("/api/energy/current")
def aktuelle_energiedaten() -> Any:
    """
    Gibt aktuelle Energiedaten zurück und speichert sie als Snapshot.
    """
    try:
        daten: dict[str, float | str] = hole_professor_daten()

        zeitpunkt: str = str(daten.get("collected_at") or datetime.now().isoformat())

        speichere_snapshot(
            timestamp=zeitpunkt,
            verbrauch_w=float(daten["verbrauch"]),
            erzeugung_w=float(daten["erzeugung"]),
            quelle=str(daten.get("quelle", "professor_api")),
        )

        logger.info("Aktuelle Energiedaten wurden bereitgestellt.")

        return jsonify(daten)

    except RuntimeError as fehler:
        logger.error("Aktuelle Energiedaten konnten nicht bereitgestellt werden.")

        return (
            jsonify(
                {
                    "error": str(fehler),
                    "quelle": "professor_api_failed",
                }
            ),
            503,
        )


@app.route("/api/energy/history")
def historische_energiedaten() -> Any:
    """
    Gibt gespeicherte Professor-Snapshots zurück.
    """
    try:
        daten: list[dict[str, Any]] = snapshots_als_liste()

        logger.info("Historische Professor-Snapshots wurden bereitgestellt.")

        return jsonify(daten)

    except ValueError as fehler:
        logger.error("Historische Daten konnten nicht geladen werden: %s", fehler)

        return (
            jsonify(
                {
                    "error": str(fehler),
                    "quelle": "storage_failed",
                }
            ),
            500,
        )


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True,
    )
