import pandas as pd
import pytest

from Source.calculations import berechne_kennzahlen, pruefe_daten_fuer_berechnung


def test_berechne_kennzahlen_mit_ueberschuss() -> None:
    """
    Testet die Berechnung der Kennzahlen bei Energieüberschuss.
    """
    daten: pd.DataFrame = pd.DataFrame(
        {
            "datum": ["2025-01-01", "2025-01-02"],
            "verbrauch": [10.0, 20.0],
            "erzeugung": [15.0, 25.0],
        }
    )

    ergebnis: dict[str, int | float | str] = berechne_kennzahlen(
        daten,
        strompreis_pro_kwh=0.35,
    )

    assert ergebnis["gesamt_verbrauch"] == 30.0
    assert ergebnis["gesamt_erzeugung"] == 40.0
    assert ergebnis["gesamt_bilanz"] == 10.0
    assert ergebnis["eigenversorgung_prozent"] == 100.0
    assert ergebnis["erspartes_geld"] == 10.5
    assert ergebnis["erfasste_tage"] == 2
    assert ergebnis["haupt_status"] == "Überschuss"


def test_berechne_kennzahlen_mit_netzbezug() -> None:
    """
    Testet die Berechnung der Kennzahlen bei Netzbezug.
    """
    daten: pd.DataFrame = pd.DataFrame(
        {
            "datum": ["2025-01-01", "2025-01-02"],
            "verbrauch": [20.0, 30.0],
            "erzeugung": [10.0, 15.0],
        }
    )

    ergebnis: dict[str, int | float | str] = berechne_kennzahlen(
        daten,
        strompreis_pro_kwh=0.40,
    )

    assert ergebnis["gesamt_verbrauch"] == 50.0
    assert ergebnis["gesamt_erzeugung"] == 25.0
    assert ergebnis["gesamt_bilanz"] == -25.0
    assert ergebnis["eigenversorgung_prozent"] == 50.0
    assert ergebnis["erspartes_geld"] == 10.0
    assert ergebnis["haupt_status"] == "Netzbezug"


def test_leerer_datensatz_wirft_fehler() -> None:
    """
    Testet, ob ein leerer Datensatz einen Fehler auslöst.
    """
    daten: pd.DataFrame = pd.DataFrame()

    with pytest.raises(ValueError):
        pruefe_daten_fuer_berechnung(daten)


def test_fehlende_spalte_wirft_fehler() -> None:
    """
    Testet, ob fehlende Spalten erkannt werden.
    """
    daten: pd.DataFrame = pd.DataFrame(
        {
            "datum": ["2025-01-01"],
            "verbrauch": [10.0],
        }
    )

    with pytest.raises(ValueError):
        pruefe_daten_fuer_berechnung(daten)


def test_negativer_strompreis_wirft_fehler() -> None:
    """
    Testet, ob ein negativer Strompreis einen Fehler auslöst.
    """
    daten: pd.DataFrame = pd.DataFrame(
        {
            "datum": ["2025-01-01"],
            "verbrauch": [10.0],
            "erzeugung": [12.0],
        }
    )

    with pytest.raises(ValueError):
        berechne_kennzahlen(daten, strompreis_pro_kwh=-0.35)
