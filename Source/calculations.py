import pandas as pd


def pruefe_daten_fuer_berechnung(daten: pd.DataFrame) -> None:
    """
    Überprüft, ob der Datensatz für die Berechnung geeignet ist.

    Es wird geprüft:
    - ob der Datensatz leer ist
    - ob die benötigten Spalten vorhanden sind
    - ob negative Werte vorhanden sind

    Parameters:
        daten (pd.DataFrame): Datensatz mit Solarenergiedaten.

    Raises:
        ValueError: Wenn der Datensatz ungültig ist.
    """
    benoetigte_spalten: list[str] = ["datum", "verbrauch", "erzeugung"]

    if daten.empty:
        raise ValueError("Der Datensatz ist leer.")

    fehlende_spalten: list[str] = [
        spalte for spalte in benoetigte_spalten if spalte not in daten.columns
    ]

    if fehlende_spalten:
        raise ValueError(f"Fehlende Spalten im Datensatz: {fehlende_spalten}")

    if (daten["verbrauch"] < 0).any():
        raise ValueError("Der Datensatz enthält negative Verbrauchswerte.")

    if (daten["erzeugung"] < 0).any():
        raise ValueError("Der Datensatz enthält negative Erzeugungswerte.")


def berechne_kennzahlen(
    gefilterte_daten: pd.DataFrame,
    strompreis_pro_kwh: float = 0.35,
) -> dict[str, int | float | str]:
    """
    Berechnet zentrale Kennzahlen zur Solarenergieanalyse.

    Dazu gehören Gesamtverbrauch, Gesamterzeugung, Energiebilanz,
    Eigenversorgung, erspartes Geld, Tagesdurchschnitte und Statusinformationen.

    Parameters:
        gefilterte_daten (pd.DataFrame): Gefilterter Datensatz mit den Spalten
        datum, verbrauch und erzeugung.

        strompreis_pro_kwh (float): Strompreis pro kWh in Euro.

    Returns:
        dict[str, int | float | str]: Wörterbuch mit den berechneten Kennzahlen.

    Raises:
        ValueError: Wenn der Datensatz ungültig ist oder der Strompreis negativ ist.
    """
    pruefe_daten_fuer_berechnung(gefilterte_daten)

    if strompreis_pro_kwh < 0:
        raise ValueError("Der Strompreis darf nicht negativ sein.")

    taegliche_daten: (
        pd.DataFrame
    ) = (  # nach Datum gruppieren und Verbrauch/Erzeugung summieren, damit die Kennzahlen auf Tagesbasis berechnet werden können
        gefilterte_daten.groupby("datum")[["verbrauch", "erzeugung"]].sum().sort_index()
    )

    taegliche_daten["bilanz"] = (
        taegliche_daten["erzeugung"] - taegliche_daten["verbrauch"]
    )

    gesamt_verbrauch: float = float(taegliche_daten["verbrauch"].sum())
    gesamt_erzeugung: float = float(taegliche_daten["erzeugung"].sum())
    gesamt_bilanz: float = gesamt_erzeugung - gesamt_verbrauch

    durchschnitt_verbrauch_tag: float = float(taegliche_daten["verbrauch"].mean())
    durchschnitt_erzeugung_tag: float = float(taegliche_daten["erzeugung"].mean())

    erfasste_tage: int = len(
        taegliche_daten
    )  # Anzahl der Tage, die im Datensatz erfasst sind

    gedeckte_energie: float = min(gesamt_verbrauch, gesamt_erzeugung)

    if gesamt_verbrauch == 0:
        eigenversorgung_prozent: float = 0.0
    else:
        eigenversorgung_prozent = round(
            (gedeckte_energie / gesamt_verbrauch) * 100,
            2,
        )

    erspartes_geld: float = gedeckte_energie * strompreis_pro_kwh

    if gesamt_bilanz > 0:
        haupt_status: str = "Überschuss"
    elif gesamt_bilanz < 0:
        haupt_status = "Netzbezug"
    else:
        haupt_status = "Ausgeglichen"

    return {
        "gesamt_verbrauch": round(gesamt_verbrauch, 2),
        "gesamt_erzeugung": round(gesamt_erzeugung, 2),
        "gesamt_bilanz": round(gesamt_bilanz, 2),
        "eigenversorgung_prozent": eigenversorgung_prozent,
        "erspartes_geld": round(erspartes_geld, 2),
        "durchschnitt_verbrauch_tag": round(durchschnitt_verbrauch_tag, 2),
        "durchschnitt_erzeugung_tag": round(durchschnitt_erzeugung_tag, 2),
        "erfasste_tage": erfasste_tage,
        "haupt_status": haupt_status,
    }
