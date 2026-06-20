import pandas as pd


def pruefe_daten_fuer_berechnung(daten: pd.DataFrame) -> None:
    """
    Prüft, ob die Daten für die klassischen CSV-Berechnungen geeignet sind.
    """
    benoetigte_spalten: list[str] = ["datum", "verbrauch", "erzeugung"]

    if daten.empty:
        raise ValueError("Die Daten dürfen nicht leer sein.")

    fehlende_spalten: list[str] = [
        spalte for spalte in benoetigte_spalten if spalte not in daten.columns
    ]

    if fehlende_spalten:
        raise ValueError(f"Fehlende Spalten: {fehlende_spalten}")

    if (daten["verbrauch"] < 0).any():
        raise ValueError("Verbrauchswerte dürfen nicht negativ sein.")

    if (daten["erzeugung"] < 0).any():
        raise ValueError("Erzeugungswerte dürfen nicht negativ sein.")


def berechne_kennzahlen(
    gefilterte_daten: pd.DataFrame,
    strompreis_pro_kwh: float = 0.35,
) -> dict[str, int | float | str]:
    """
    Berechnet klassische Kennzahlen für CSV-Daten.

    Diese Funktion bleibt für die Beispiel-CSV-Daten erhalten.
    """
    pruefe_daten_fuer_berechnung(gefilterte_daten)

    if strompreis_pro_kwh < 0:
        raise ValueError("Der Strompreis darf nicht negativ sein.")

    daten: pd.DataFrame = gefilterte_daten.copy()
    daten["datum"] = pd.to_datetime(daten["datum"], errors="coerce")
    daten = daten.dropna(subset=["datum"])

    taegliche_daten: pd.DataFrame = (
        daten.groupby("datum")[["verbrauch", "erzeugung"]].sum().sort_index()
    )

    taegliche_daten["bilanz"] = (
        taegliche_daten["erzeugung"] - taegliche_daten["verbrauch"]
    )

    gesamt_verbrauch: float = float(taegliche_daten["verbrauch"].sum())
    gesamt_erzeugung: float = float(taegliche_daten["erzeugung"].sum())
    gesamt_bilanz: float = gesamt_erzeugung - gesamt_verbrauch

    durchschnitt_verbrauch_tag: float = float(taegliche_daten["verbrauch"].mean())
    durchschnitt_erzeugung_tag: float = float(taegliche_daten["erzeugung"].mean())

    erfasste_tage: int = len(taegliche_daten)

    gedeckte_energie: float = min(gesamt_verbrauch, gesamt_erzeugung)

    if gesamt_verbrauch == 0:
        eigenversorgung_prozent: float = 0.0
    else:
        eigenversorgung_prozent = round((gedeckte_energie / gesamt_verbrauch) * 100, 2)

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
        "durchschnitt_verbrauch_tag": round(durchschnitt_verbrauch_tag, 2),
        "durchschnitt_erzeugung_tag": round(durchschnitt_erzeugung_tag, 2),
        "erfasste_tage": erfasste_tage,
        "eigenversorgung_prozent": eigenversorgung_prozent,
        "erspartes_geld": round(erspartes_geld, 2),
        "haupt_status": haupt_status,
    }


def bereite_snapshot_daten_vor(
    daten: pd.DataFrame,
    maximale_luecke_sekunden: int = 300,
) -> pd.DataFrame:
    """
    Bereitet gespeicherte Professor-Snapshots für Energie-Berechnungen vor.

    Die Professor-API liefert momentane Leistung in Watt.
    Aus Leistung über Zeit wird näherungsweise Energie in Wattstunden berechnet.
    """
    benoetigte_spalten: list[str] = [
        "timestamp",
        "verbrauch_w",
        "erzeugung_w",
    ]

    if daten.empty:
        raise ValueError("Keine Professor-Snapshots vorhanden.")

    fehlende_spalten: list[str] = [
        spalte for spalte in benoetigte_spalten if spalte not in daten.columns
    ]

    if fehlende_spalten:
        raise ValueError(f"Fehlende Snapshot-Spalten: {fehlende_spalten}")

    vorbereitete_daten: pd.DataFrame = daten.copy()

    vorbereitete_daten["timestamp"] = pd.to_datetime(
        vorbereitete_daten["timestamp"],
        errors="coerce",
        utc=True,
    ).dt.tz_convert("Europe/Berlin")

    vorbereitete_daten["verbrauch_w"] = pd.to_numeric(
        vorbereitete_daten["verbrauch_w"],
        errors="coerce",
    )
    vorbereitete_daten["erzeugung_w"] = pd.to_numeric(
        vorbereitete_daten["erzeugung_w"],
        errors="coerce",
    )

    vorbereitete_daten = vorbereitete_daten.dropna(
        subset=[
            "timestamp",
            "verbrauch_w",
            "erzeugung_w",
        ]
    )

    if vorbereitete_daten.empty:
        raise ValueError("Nach der Bereinigung sind keine Snapshots vorhanden.")

    if (vorbereitete_daten["verbrauch_w"] < 0).any():
        raise ValueError("Verbrauchswerte dürfen nicht negativ sein.")

    if (vorbereitete_daten["erzeugung_w"] < 0).any():
        raise ValueError("Erzeugungswerte dürfen nicht negativ sein.")

    vorbereitete_daten = vorbereitete_daten.sort_values("timestamp")

    vorbereitete_daten["zeitdifferenz_sekunden"] = (
        vorbereitete_daten["timestamp"].diff().dt.total_seconds()
    )

    vorbereitete_daten["zeitdifferenz_sekunden"] = vorbereitete_daten[
        "zeitdifferenz_sekunden"
    ].fillna(0)

    vorbereitete_daten["zeitdifferenz_sekunden"] = vorbereitete_daten[
        "zeitdifferenz_sekunden"
    ].clip(lower=0, upper=maximale_luecke_sekunden)

    vorbereitete_daten["zeitdifferenz_stunden"] = (
        vorbereitete_daten["zeitdifferenz_sekunden"] / 3600
    )

    vorbereitete_daten["verbrauch_wh"] = (
        vorbereitete_daten["verbrauch_w"] * vorbereitete_daten["zeitdifferenz_stunden"]
    )

    vorbereitete_daten["erzeugung_wh"] = (
        vorbereitete_daten["erzeugung_w"] * vorbereitete_daten["zeitdifferenz_stunden"]
    )

    return vorbereitete_daten


def berechne_pv_anteil(
    verbrauch_wh: float,
    erzeugung_wh: float,
) -> float:
    """
    Berechnet den Anteil des Verbrauchs, der rechnerisch durch PV gedeckt wird.
    """
    if verbrauch_wh <= 0:
        return 0.0

    verbrauch_aus_pv: float = min(verbrauch_wh, erzeugung_wh)

    return round((verbrauch_aus_pv / verbrauch_wh) * 100, 2)


def berechne_pv_dashboard_kennzahlen(
    snapshots: pd.DataFrame,
) -> dict[str, float | str]:
    """
    Berechnet alle PV-Dashboard-Kennzahlen für Professor-Snapshots.
    """
    daten: pd.DataFrame = bereite_snapshot_daten_vor(snapshots)

    letzter_datensatz: pd.Series = daten.iloc[-1]
    aktueller_zeitpunkt = letzter_datensatz["timestamp"]

    tagesdaten: pd.DataFrame = daten[
        daten["timestamp"].dt.date == aktueller_zeitpunkt.date()
    ]

    monatsdaten: pd.DataFrame = daten[
        (daten["timestamp"].dt.year == aktueller_zeitpunkt.year)
        & (daten["timestamp"].dt.month == aktueller_zeitpunkt.month)
    ]

    jahresdaten: pd.DataFrame = daten[
        daten["timestamp"].dt.year == aktueller_zeitpunkt.year
    ]

    tagesverbrauch_wh: float = float(tagesdaten["verbrauch_wh"].sum())
    tageserzeugung_wh: float = float(tagesdaten["erzeugung_wh"].sum())

    monatsverbrauch_wh: float = float(monatsdaten["verbrauch_wh"].sum())
    monatserzeugung_wh: float = float(monatsdaten["erzeugung_wh"].sum())

    jahresverbrauch_wh: float = float(jahresdaten["verbrauch_wh"].sum())
    jahreserzeugung_wh: float = float(jahresdaten["erzeugung_wh"].sum())

    return {
        "zeitpunkt": str(aktueller_zeitpunkt),
        "momentanverbrauch_w": round(float(letzter_datensatz["verbrauch_w"]), 2),
        "momentanerzeugung_w": round(float(letzter_datensatz["erzeugung_w"]), 2),
        "tagesverbrauch_wh": round(tagesverbrauch_wh, 2),
        "tageserzeugung_wh": round(tageserzeugung_wh, 2),
        "monatsverbrauch_wh": round(monatsverbrauch_wh, 2),
        "monatserzeugung_wh": round(monatserzeugung_wh, 2),
        "jahresverbrauch_wh": round(jahresverbrauch_wh, 2),
        "jahreserzeugung_wh": round(jahreserzeugung_wh, 2),
        "pv_anteil_tag": berechne_pv_anteil(
            tagesverbrauch_wh,
            tageserzeugung_wh,
        ),
        "pv_anteil_monat": berechne_pv_anteil(
            monatsverbrauch_wh,
            monatserzeugung_wh,
        ),
        "pv_anteil_jahr": berechne_pv_anteil(
            jahresverbrauch_wh,
            jahreserzeugung_wh,
        ),
    }


def erstelle_tagesverlauf(snapshots: pd.DataFrame) -> pd.DataFrame:
    """
    Erstellt den Tagesverlauf für Diagramme.
    """
    daten: pd.DataFrame = bereite_snapshot_daten_vor(snapshots)

    aktueller_zeitpunkt = daten.iloc[-1]["timestamp"]

    tagesdaten: pd.DataFrame = daten[
        daten["timestamp"].dt.date == aktueller_zeitpunkt.date()
    ].copy()

    tagesdaten["tagesverbrauch_wh"] = tagesdaten["verbrauch_wh"].cumsum()
    tagesdaten["tageserzeugung_wh"] = tagesdaten["erzeugung_wh"].cumsum()

    return tagesdaten
