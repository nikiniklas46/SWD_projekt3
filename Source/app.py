import pandas as pd
import streamlit as st

from Source.calculations import berechne_kennzahlen
from Source.data_loader import lade_daten
from Source.utils.logger import setup_logger

logger = setup_logger()

st.set_page_config(
    page_title="Solar Energy Dashboard",
    page_icon="☀️",
    layout="wide",
)


def main() -> None:
    """
    Startet das Streamlit-Dashboard.

    Die Anwendung lädt Solarenergiedaten entweder aus lokalen CSV-Beispieldaten
    oder aus einer CSV-URL.

    Returns:
        None
    """
    st.title("☀️ Solar Energy Dashboard")

    st.write(
        """
        Dieses Dashboard analysiert den Energieverbrauch und die Energieerzeugung.
        Die wichtigsten Variablen sind `verbrauch` und `erzeugung`.
        """
    )

    st.sidebar.header("Einstellungen")

    strompreis_pro_kwh: float = st.sidebar.number_input(
        "Strompreis pro kWh (€)",
        min_value=0.0,
        value=0.35,
        step=0.01,
    )

    datenquelle: str = st.sidebar.radio(
        "Datenquelle auswählen",
        ["CSV-Beispieldaten", "CSV-URL"],
    )

    if datenquelle == "CSV-Beispieldaten":
        daten: pd.DataFrame = lade_daten("data/input/example_data.csv")
        st.sidebar.success("CSV-Beispieldaten wurden geladen.")

    elif datenquelle == "CSV-URL":
        csv_url: str = st.sidebar.text_input(
            "CSV-URL eingeben",
            placeholder="https://example.com/solar_data.csv",
        )

        if not csv_url:
            st.warning("Bitte gib eine CSV-URL in der Sidebar ein.")
            st.stop()

        daten = lade_daten(csv_url)
        st.sidebar.success("Daten wurden von der CSV-URL geladen.")

    if "bilanz" not in daten.columns:
        daten["bilanz"] = daten["erzeugung"] - daten["verbrauch"]

    try:
        kennzahlen: dict[str, int | float | str] = berechne_kennzahlen(
            daten,
            strompreis_pro_kwh=strompreis_pro_kwh,
        )

    except ValueError as fehler:
        logger.error("Fehler bei der Berechnung: %s", fehler)
        st.error(f"Fehler bei der Berechnung: {fehler}")
        st.stop()

    zeige_kennzahlen(kennzahlen)
    zeige_diagramme(daten)


def zeige_kennzahlen(kennzahlen: dict[str, int | float | str]) -> None:
    """
    Zeigt die wichtigsten Kennzahlen im Dashboard an.

    Parameters:
        kennzahlen (dict[str, int | float | str]): Berechnete Kennzahlen.

    Returns:
        None
    """
    st.subheader("Kennzahlen")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Gesamtverbrauch", f"{kennzahlen['gesamt_verbrauch']} kWh")

    with col2:
        st.metric("Gesamterzeugung", f"{kennzahlen['gesamt_erzeugung']} kWh")

    with col3:
        st.metric("Gesamtbilanz", f"{kennzahlen['gesamt_bilanz']} kWh")

    with col4:
        st.metric("Eigenversorgung", f"{kennzahlen['eigenversorgung_prozent']} %")

    col5, col6, col7, col8 = st.columns(4)

    with col5:
        st.metric("Erspartes Geld", f"{kennzahlen['erspartes_geld']} €")

    with col6:
        st.metric(
            "Ø Verbrauch pro Tag",
            f"{kennzahlen['durchschnitt_verbrauch_tag']} kWh",
        )

    with col7:
        st.metric(
            "Ø Erzeugung pro Tag",
            f"{kennzahlen['durchschnitt_erzeugung_tag']} kWh",
        )

    with col8:
        st.metric("Erfasste Tage", kennzahlen["erfasste_tage"])

    if "haupt_status" in kennzahlen:
        st.info(f"Aktueller Gesamtstatus: {kennzahlen['haupt_status']}")


def zeige_diagramme(daten: pd.DataFrame) -> None:
    """
    Zeigt Diagramme für Verbrauch, Erzeugung und Bilanz an.

    Parameters:
        daten (pd.DataFrame): Bereinigter Datensatz mit Solarenergiedaten.

    Returns:
        None
    """
    st.subheader("Datenübersicht")
    st.dataframe(daten)

    st.subheader("Verbrauch und Erzeugung über Zeit")

    diagramm_daten: pd.DataFrame = daten.set_index("datum")[
        ["verbrauch", "erzeugung"]
    ]
    st.line_chart(diagramm_daten)

    st.subheader("Bilanz über Zeit")

    bilanz_daten: pd.DataFrame = daten.set_index("datum")[["bilanz"]]
    st.bar_chart(bilanz_daten)


if __name__ == "__main__":
    main()