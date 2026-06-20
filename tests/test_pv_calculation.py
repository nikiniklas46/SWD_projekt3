import pandas as pd

from Source.calculations import (
    berechne_pv_anteil,
    berechne_pv_dashboard_kennzahlen,
    bereite_snapshot_daten_vor,
    erstelle_tagesverlauf,
)


def erstelle_snapshot_testdaten() -> pd.DataFrame:
    """
    Erstellt Snapshot-Testdaten mit zwei Messpunkten.

    Returns:
        pd.DataFrame: Testdaten mit Verbrauch und Erzeugung in Watt.
    """
    return pd.DataFrame(
        {
            "timestamp": [
                "2026-06-20T13:00:00+02:00",
                "2026-06-20T13:05:00+02:00",
            ],
            "verbrauch_w": [
                12000.0,
                12000.0,
            ],
            "erzeugung_w": [
                6000.0,
                6000.0,
            ],
            "quelle": [
                "professor_api",
                "professor_api",
            ],
        }
    )


def test_bereite_snapshot_daten_vor_berechnet_wh() -> None:
    """
    Prüft, ob aus Wattwerten und Zeitdifferenz Wattstunden berechnet werden.
    """
    snapshots = erstelle_snapshot_testdaten()

    daten = bereite_snapshot_daten_vor(snapshots)

    assert "verbrauch_wh" in daten.columns
    assert "erzeugung_wh" in daten.columns

    assert round(float(daten.iloc[1]["verbrauch_wh"]), 2) == 1000.0
    assert round(float(daten.iloc[1]["erzeugung_wh"]), 2) == 500.0


def test_berechne_pv_anteil_liefert_50_prozent() -> None:
    """
    Prüft, ob ein halb gedeckter Verbrauch zu 50 Prozent PV-Anteil führt.
    """
    anteil = berechne_pv_anteil(
        verbrauch_wh=1000.0,
        erzeugung_wh=500.0,
    )

    assert anteil == 50.0


def test_berechne_pv_anteil_liefert_100_prozent_bei_ueberschuss() -> None:
    """
    Prüft, ob PV-Überschuss maximal 100 Prozent Verbrauchsdeckung ergibt.
    """
    anteil = berechne_pv_anteil(
        verbrauch_wh=1000.0,
        erzeugung_wh=2000.0,
    )

    assert anteil == 100.0


def test_berechne_pv_dashboard_kennzahlen() -> None:
    """
    Prüft, ob Momentan-, Tages-, Monats- und Jahreswerte berechnet werden.
    """
    snapshots = erstelle_snapshot_testdaten()

    kennzahlen = berechne_pv_dashboard_kennzahlen(snapshots)

    assert kennzahlen["momentanverbrauch_w"] == 12000.0
    assert kennzahlen["momentanerzeugung_w"] == 6000.0
    assert kennzahlen["tagesverbrauch_wh"] == 1000.0
    assert kennzahlen["tageserzeugung_wh"] == 500.0
    assert kennzahlen["monatsverbrauch_wh"] == 1000.0
    assert kennzahlen["monatserzeugung_wh"] == 500.0
    assert kennzahlen["jahresverbrauch_wh"] == 1000.0
    assert kennzahlen["jahreserzeugung_wh"] == 500.0
    assert kennzahlen["pv_anteil_tag"] == 50.0


def test_erstelle_tagesverlauf_enthaelt_kumulierte_werte() -> None:
    """
    Prüft, ob der Tagesverlauf kumulierte Tageswerte enthält.
    """
    snapshots = erstelle_snapshot_testdaten()

    tagesverlauf = erstelle_tagesverlauf(snapshots)

    assert "tagesverbrauch_wh" in tagesverlauf.columns
    assert "tageserzeugung_wh" in tagesverlauf.columns
    assert round(float(tagesverlauf.iloc[-1]["tagesverbrauch_wh"]), 2) == 1000.0
    assert round(float(tagesverlauf.iloc[-1]["tageserzeugung_wh"]), 2) == 500.0
