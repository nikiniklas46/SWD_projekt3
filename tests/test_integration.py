import pandas as pd

from Source.calculations import berechne_kennzahlen


def test_integration_serverdaten_zu_kennzahlen() -> None:
    """
    Testet vereinfacht den Ablauf von Serverdaten zu berechneten Kennzahlen.
    """
    daten: pd.DataFrame = pd.DataFrame(
        {
            "datum": ["2025-01-01"],
            "verbrauch": [10.0],
            "erzeugung": [15.0],
        }
    )

    daten["bilanz"] = daten["erzeugung"] - daten["verbrauch"]

    kennzahlen: dict[str, int | float | str] = berechne_kennzahlen(daten)

    assert kennzahlen["gesamt_verbrauch"] == 10.0
    assert kennzahlen["gesamt_erzeugung"] == 15.0
    assert kennzahlen["gesamt_bilanz"] == 5.0
    assert kennzahlen["haupt_status"] == "Überschuss"