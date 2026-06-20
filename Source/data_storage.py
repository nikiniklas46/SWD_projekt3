from pathlib import Path
from typing import Any

import pandas as pd

from Source.utils.logger import setup_logger

logger = setup_logger()

SNAPSHOT_DATEI: str = "data/output/professor_snapshots.csv"


def speichere_daten(daten: pd.DataFrame, dateipfad: str) -> None:
    """
    Speichert allgemeine Daten als CSV-Datei.
    """
    zielpfad = Path(dateipfad)
    zielpfad.parent.mkdir(parents=True, exist_ok=True)

    daten.to_csv(zielpfad, index=False)

    logger.info("Daten wurden gespeichert: %s", zielpfad)


def lade_gespeicherte_daten(dateipfad: str) -> pd.DataFrame:
    """
    Lädt gespeicherte CSV-Daten.
    """
    quelldatei = Path(dateipfad)

    if not quelldatei.exists():
        logger.error("Gespeicherte Datei wurde nicht gefunden: %s", quelldatei)
        raise FileNotFoundError(f"Datei wurde nicht gefunden: {quelldatei}")

    daten: pd.DataFrame = pd.read_csv(quelldatei)

    logger.info("Gespeicherte Daten wurden geladen: %s", quelldatei)

    return daten


def speichere_snapshot(
    timestamp: str,
    verbrauch_w: float,
    erzeugung_w: float,
    quelle: str = "professor_api",
    dateipfad: str = SNAPSHOT_DATEI,
) -> None:
    """
    Speichert einen aktuellen Professor-Datenpunkt als Snapshot.

    Die Werte werden als momentane Leistung in Watt gespeichert.
    """
    zielpfad = Path(dateipfad)
    zielpfad.parent.mkdir(parents=True, exist_ok=True)

    neuer_snapshot: pd.DataFrame = pd.DataFrame(
        [
            {
                "timestamp": timestamp,
                "verbrauch_w": float(verbrauch_w),
                "erzeugung_w": float(erzeugung_w),
                "quelle": quelle,
            }
        ]
    )

    datei_existiert: bool = zielpfad.exists() and zielpfad.stat().st_size > 0

    neuer_snapshot.to_csv(
        zielpfad,
        mode="a",
        header=not datei_existiert,
        index=False,
    )

    logger.info("Professor-Snapshot wurde gespeichert: %s", zielpfad)


def lade_snapshots(dateipfad: str = SNAPSHOT_DATEI) -> pd.DataFrame:
    """
    Lädt gespeicherte Professor-Snapshots.
    """
    quelldatei = Path(dateipfad)

    if not quelldatei.exists():
        logger.warning("Noch keine Professor-Snapshots vorhanden.")
        return pd.DataFrame(
            columns=[
                "timestamp",
                "verbrauch_w",
                "erzeugung_w",
                "quelle",
            ]
        )

    daten: pd.DataFrame = pd.read_csv(quelldatei)

    erwartete_spalten: list[str] = [
        "timestamp",
        "verbrauch_w",
        "erzeugung_w",
        "quelle",
    ]

    fehlende_spalten: list[str] = [
        spalte for spalte in erwartete_spalten if spalte not in daten.columns
    ]

    if fehlende_spalten:
        raise ValueError(f"Fehlende Spalten in Snapshot-Datei: {fehlende_spalten}")

    daten["timestamp"] = pd.to_datetime(
        daten["timestamp"],
        errors="coerce",
        utc=True,
    )
    daten["verbrauch_w"] = pd.to_numeric(daten["verbrauch_w"], errors="coerce")
    daten["erzeugung_w"] = pd.to_numeric(daten["erzeugung_w"], errors="coerce")

    daten = daten.dropna(subset=["timestamp", "verbrauch_w", "erzeugung_w"])
    daten = daten.sort_values("timestamp")

    logger.info("Professor-Snapshots wurden geladen.")

    return daten


def snapshots_als_liste(dateipfad: str = SNAPSHOT_DATEI) -> list[dict[str, Any]]:
    """
    Gibt gespeicherte Snapshots als Liste zurück.
    """
    daten: pd.DataFrame = lade_snapshots(dateipfad)

    if daten.empty:
        return []

    daten = daten.copy()
    daten["timestamp"] = daten["timestamp"].astype(str)

    return daten.to_dict(orient="records")
