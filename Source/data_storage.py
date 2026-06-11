from pathlib import Path

import pandas as pd

from Source.utils.logger import setup_logger

logger = setup_logger()


def speichere_daten(daten: pd.DataFrame, dateipfad: str) -> None:
    """
    Speichert bereinigte PV-Daten in einer CSV-Datei.

    Falls der Zielordner noch nicht existiert, wird er automatisch erstellt.

    Parameters:
        daten (pd.DataFrame): Bereinigter Datensatz.
        dateipfad (str): Zielpfad der Ausgabedatei.

    Returns:
        None
    """
    zielpfad: Path = Path(dateipfad)

    zielpfad.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    daten.to_csv(
        zielpfad,
        index=False,
    )

    logger.info("Daten wurden gespeichert: %s", zielpfad)


def lade_gespeicherte_daten(dateipfad: str) -> pd.DataFrame:
    """
    Lädt gespeicherte PV-Daten aus einer CSV-Datei.

    Parameters:
        dateipfad (str): Pfad zur gespeicherten CSV-Datei.

    Returns:
        pd.DataFrame: Geladene PV-Daten.

    Raises:
        FileNotFoundError: Wenn die Datei nicht existiert.
    """
    quelldatei: Path = Path(dateipfad)

    if not quelldatei.exists():
        logger.error("Gespeicherte Datei wurde nicht gefunden: %s", quelldatei)
        raise FileNotFoundError(f"Datei wurde nicht gefunden: {quelldatei}")

    daten: pd.DataFrame = pd.read_csv(quelldatei)

    logger.info("Gespeicherte Daten wurden geladen: %s", quelldatei)

    return daten
