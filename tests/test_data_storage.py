from pathlib import Path

import pandas as pd

from Source.data_storage import lade_snapshots, speichere_snapshot, snapshots_als_liste


def test_speichere_snapshot_erstellt_csv_datei(tmp_path: Path) -> None:
    """
    Prüft, ob ein Professor-Snapshot als CSV-Datei gespeichert wird.
    """
    dateipfad = tmp_path / "snapshots.csv"

    speichere_snapshot(
        timestamp="2026-06-20T13:00:00+02:00",
        verbrauch_w=80000.0,
        erzeugung_w=150000.0,
        quelle="professor_api",
        dateipfad=str(dateipfad),
    )

    assert dateipfad.exists()

    daten = pd.read_csv(dateipfad)

    assert len(daten) == 1
    assert daten.iloc[0]["verbrauch_w"] == 80000.0
    assert daten.iloc[0]["erzeugung_w"] == 150000.0
    assert daten.iloc[0]["quelle"] == "professor_api"


def test_lade_snapshots_laesst_mehrere_snapshots_zu(tmp_path: Path) -> None:
    """
    Prüft, ob mehrere gespeicherte Snapshots geladen werden können.
    """
    dateipfad = tmp_path / "snapshots.csv"

    speichere_snapshot(
        timestamp="2026-06-20T13:00:00+02:00",
        verbrauch_w=80000.0,
        erzeugung_w=150000.0,
        dateipfad=str(dateipfad),
    )

    speichere_snapshot(
        timestamp="2026-06-20T13:05:00+02:00",
        verbrauch_w=90000.0,
        erzeugung_w=160000.0,
        dateipfad=str(dateipfad),
    )

    daten = lade_snapshots(str(dateipfad))

    assert len(daten) == 2
    assert list(daten["verbrauch_w"]) == [80000.0, 90000.0]
    assert list(daten["erzeugung_w"]) == [150000.0, 160000.0]


def test_lade_snapshots_gibt_leeren_dataframe_zurueck_wenn_datei_fehlt(
    tmp_path: Path,
) -> None:
    """
    Prüft, ob bei fehlender Snapshot-Datei ein leerer DataFrame zurückgegeben wird.
    """
    dateipfad = tmp_path / "nicht_vorhanden.csv"

    daten = lade_snapshots(str(dateipfad))

    assert daten.empty
    assert list(daten.columns) == [
        "timestamp",
        "verbrauch_w",
        "erzeugung_w",
        "quelle",
    ]


def test_snapshots_als_liste_gibt_liste_zurueck(tmp_path: Path) -> None:
    """
    Prüft, ob Snapshots als Liste von Dictionaries zurückgegeben werden.
    """
    dateipfad = tmp_path / "snapshots.csv"

    speichere_snapshot(
        timestamp="2026-06-20T13:00:00+02:00",
        verbrauch_w=80000.0,
        erzeugung_w=150000.0,
        quelle="professor_api",
        dateipfad=str(dateipfad),
    )

    daten_liste = snapshots_als_liste(str(dateipfad))

    assert isinstance(daten_liste, list)
    assert len(daten_liste) == 1
    assert daten_liste[0]["verbrauch_w"] == 80000.0
