from pathlib import Path

import pandas as pd

from Source.data_loader import lade_daten


def test_lade_daten_gueltige_csv(tmp_path: Path) -> None:
    """
    Testet, ob eine gültige CSV-Datei korrekt geladen und vorbereitet wird.
    """
    datei: Path = (
        tmp_path / "test_data.csv"
    )  # Test-CSV-Datei mit gültigen Daten erstellen

    datei.write_text(  # Inhalt der Test-CSV-Datei
        "Datum,Verbrauch(kWh),Erzeugung(kWh)\n"
        "2025-01-01,10.0,15.0\n"
        "2025-01-02,12.0,8.0\n",
        encoding="utf-8",
    )

    daten: pd.DataFrame = lade_daten(datei)  # Daten mit der Funktion laden

    assert len(daten) == 2
    assert list(daten["verbrauch"]) == [
        10.0,
        12.0,
    ]  # Überprüfen, ob die Verbrauchswerte korrekt geladen wurden
    assert list(daten["erzeugung"]) == [15.0, 8.0]
    assert "datum" in daten.columns
    assert "bilanz" in daten.columns
    assert "woche" in daten.columns


def test_lade_daten_berechnet_bilanz(tmp_path: Path) -> None:
    """
    Testet, ob die Bilanz korrekt berechnet wird.
    """
    datei: Path = tmp_path / "test_data.csv"

    datei.write_text(  # Test-CSV-Datei mit einem Eintrag erstellen
        "Datum,Verbrauch(kWh),Erzeugung(kWh)\n" "2025-01-01,10.0,15.0\n",
        encoding="utf-8",
    )

    daten: pd.DataFrame = lade_daten(datei)

    assert (
        daten.iloc[0]["bilanz"] == 5.0
    )  # Überprüfen, ob die Bilanz korrekt berechnet wurde (15.0 - 10.0 = 5.0)
