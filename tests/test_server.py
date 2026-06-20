from typing import Any

import pytest

from Source.server import normalisiere_professor_daten


def erstelle_professor_antwort() -> dict[str, Any]:
    """
    Erstellt eine realistische Beispielantwort der Professor-API.

    Returns:
        dict[str, Any]: Simulierte API-Antwort mit Verbrauchs- und Erzeugungswerten.
    """
    return {
        "collected_at": "2026-06-20T15:15:46.773537+02:00",
        "data": [
            {
                "path": "Building > Device > Consumption > Ptot",
                "type": "consumption",
                "value": 80000.0,
            },
            {
                "path": "Building > Device > PV1 > Ptot",
                "type": "generation",
                "value": 120000.0,
            },
            {
                "path": "Building > Device > PV2 > Ptot",
                "type": "generation",
                "value": 30000.0,
            },
        ],
        "age_seconds": 2.5,
    }


def test_normalisiere_professor_daten_summiert_generation() -> None:
    """
    Prüft, ob mehrere Erzeugungswerte korrekt aufsummiert werden.
    """
    antwort = erstelle_professor_antwort()

    daten = normalisiere_professor_daten(antwort)

    assert daten["verbrauch"] == 80000.0
    assert daten["erzeugung"] == 150000.0
    assert daten["quelle"] == "professor_api"


def test_normalisiere_professor_daten_uebernimmt_collected_at() -> None:
    """
    Prüft, ob der Zeitstempel aus der Professor-API übernommen wird.
    """
    antwort = erstelle_professor_antwort()

    daten = normalisiere_professor_daten(antwort)

    assert daten["collected_at"] == "2026-06-20T15:15:46.773537+02:00"


def test_normalisiere_professor_daten_ohne_data_liste_fehlgeschlagen() -> None:
    """
    Prüft, ob eine Antwort ohne data-Liste abgelehnt wird.
    """
    antwort = {
        "collected_at": "2026-06-20T15:15:46.773537+02:00",
    }

    with pytest.raises(KeyError):
        normalisiere_professor_daten(antwort)


def test_normalisiere_professor_daten_mit_falschem_format_fehlgeschlagen() -> None:
    """
    Prüft, ob ein falsches Antwortformat abgelehnt wird.
    """
    antwort = [
        {
            "type": "consumption",
            "value": 1000.0,
        }
    ]

    with pytest.raises(ValueError):
        normalisiere_professor_daten(antwort)


def test_normalisiere_professor_daten_ohne_passende_werte_fehlgeschlagen() -> None:
    """
    Prüft, ob eine data-Liste ohne Verbrauch und Erzeugung abgelehnt wird.
    """
    antwort = {
        "data": [
            {
                "type": "unknown",
                "value": 1000.0,
            }
        ]
    }

    with pytest.raises(ValueError):
        normalisiere_professor_daten(antwort)
