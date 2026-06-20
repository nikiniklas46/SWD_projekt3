from typing import Any

import pytest
import requests

from Source import app_connector


class FakeResponse:
    """
    Simuliert eine requests.Response für App-Connector-Tests.
    """

    def __init__(self, status_code: int, payload: Any) -> None:
        """
        Initialisiert eine FakeResponse.

        Parameters:
            status_code (int): Simulierter HTTP-Statuscode.
            payload (Any): Simulierter JSON-Inhalt.
        """
        self.status_code = status_code
        self.payload = payload

    def json(self) -> Any:
        """
        Gibt den simulierten JSON-Inhalt zurück.

        Returns:
            Any: Simulierte JSON-Antwort.
        """
        return self.payload


def test_hole_aktuelle_app_daten_erfolgreich(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Prüft, ob aktuelle App-Daten bei erfolgreicher Serverantwort geladen werden.
    """

    def fake_get(url: str, timeout: int) -> FakeResponse:
        """
        Simuliert einen erfolgreichen GET-Request.
        """
        return FakeResponse(
            200,
            {
                "verbrauch": 80000.0,
                "erzeugung": 150000.0,
                "quelle": "professor_api",
            },
        )

    monkeypatch.setattr(requests, "get", fake_get)

    daten = app_connector.hole_aktuelle_app_daten()

    assert daten["verbrauch"] == 80000.0
    assert daten["erzeugung"] == 150000.0
    assert daten["quelle"] == "professor_api"


def test_hole_aktuelle_app_daten_serverfehler(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Prüft, ob ein Serverfehler als RuntimeError behandelt wird.
    """

    def fake_get(url: str, timeout: int) -> FakeResponse:
        """
        Simuliert einen fehlgeschlagenen GET-Request.
        """
        return FakeResponse(
            503,
            {
                "error": "Professor-Daten konnten nicht geladen werden.",
            },
        )

    monkeypatch.setattr(requests, "get", fake_get)

    with pytest.raises(RuntimeError):
        app_connector.hole_aktuelle_app_daten()


def test_hole_historische_app_daten_erfolgreich(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Prüft, ob historische Snapshot-Daten geladen werden.
    """

    def fake_get(url: str, timeout: int) -> FakeResponse:
        """
        Simuliert einen erfolgreichen GET-Request für historische Daten.
        """
        return FakeResponse(
            200,
            [
                {
                    "timestamp": "2026-06-20T13:00:00+02:00",
                    "verbrauch_w": 80000.0,
                    "erzeugung_w": 150000.0,
                    "quelle": "professor_api",
                }
            ],
        )

    monkeypatch.setattr(requests, "get", fake_get)

    daten = app_connector.hole_historische_app_daten()

    assert isinstance(daten, list)
    assert daten[0]["verbrauch_w"] == 80000.0


def test_hole_historische_app_daten_falsches_format(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Prüft, ob ein falsches Format für historische Daten abgelehnt wird.
    """

    def fake_get(url: str, timeout: int) -> FakeResponse:
        """
        Simuliert eine Antwort mit falschem Format.
        """
        return FakeResponse(
            200,
            {
                "message": "Das ist keine Liste.",
            },
        )

    monkeypatch.setattr(requests, "get", fake_get)

    with pytest.raises(RuntimeError):
        app_connector.hole_historische_app_daten()
