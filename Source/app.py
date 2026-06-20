from datetime import datetime
from typing import Any

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st
from streamlit_autorefresh import st_autorefresh

from Source.app_connector import hole_aktuelle_app_daten, hole_historische_app_daten
from Source.calculations import (
    berechne_kennzahlen,
    berechne_pv_dashboard_kennzahlen,
    erstelle_tagesverlauf,
)
from Source.data_loader import lade_daten
from Source.utils.logger import setup_logger

logger = setup_logger()

st.set_page_config(
    page_title="Solar Energy Dashboard",
    page_icon="☀️",
    layout="wide",
)


def formatiere_kw(wert_w: float) -> str:
    """
    Formatiert Watt als Kilowatt.
    """
    return f"{wert_w / 1000:.2f} kW"


def formatiere_kwh(wert_wh: float) -> str:
    """
    Formatiert Wattstunden als Kilowattstunden.
    """
    return f"{wert_wh / 1000:.2f} kWh"


def berechne_verbrauchsanteile(
    verbrauch_wh: float,
    erzeugung_wh: float,
) -> tuple[float, float, float]:
    """
    Berechnet PV-gedeckten Verbrauch, Netzbezug und PV-Anteil.

    Returns:
        tuple[float, float, float]: Verbrauch aus PV, Netzbezug, PV-Anteil in Prozent.
    """
    if verbrauch_wh <= 0:
        return 0.0, 0.0, 0.0

    verbrauch_aus_pv_wh: float = min(verbrauch_wh, erzeugung_wh)
    netzbezug_wh: float = max(verbrauch_wh - verbrauch_aus_pv_wh, 0.0)
    pv_anteil_prozent: float = (verbrauch_aus_pv_wh / verbrauch_wh) * 100

    return verbrauch_aus_pv_wh, netzbezug_wh, pv_anteil_prozent


def main() -> None:
    """
    Startet das Streamlit-Dashboard.
    """
    st.title("☀️ Solar Energy Dashboard")

    st.write("""
        Dieses Dashboard analysiert aktuelle PV-Daten.
        Die Professor-Daten werden über den eigenen Flask-Server geladen,
        gespeichert und für Tages-, Monats- und Jahreskennzahlen verwendet.
        """)

    st.sidebar.header("Einstellungen")

    datenquelle: str = st.sidebar.radio(
        "Datenquelle auswählen",
        ["Professor-Server-Daten", "CSV-Beispieldaten"],
    )

    if datenquelle == "Professor-Server-Daten":
        zeige_professor_dashboard()

    elif datenquelle == "CSV-Beispieldaten":
        zeige_csv_dashboard()

    else:
        st.error("Unbekannte Datenquelle.")
        st.stop()


def zeige_professor_dashboard() -> None:
    """
    Zeigt das Dashboard für echte Professor-Server-Daten.
    """
    automatisch_aktualisieren: bool = st.sidebar.checkbox(
        "Automatisch aktualisieren",
        value=True,
    )

    aktualisierungsintervall: int = st.sidebar.number_input(
        "Aktualisierung alle x Sekunden",
        min_value=5,
        max_value=300,
        value=10,
        step=5,
    )

    if automatisch_aktualisieren:
        st_autorefresh(
            interval=aktualisierungsintervall * 1000,
            key="dashboard_autorefresh",
        )

    try:
        aktuelle_daten: dict[str, Any] = hole_aktuelle_app_daten()
        historische_daten: list[dict[str, Any]] = hole_historische_app_daten()

    except RuntimeError as fehler:
        logger.error(
            "Professor-Daten konnten im Dashboard nicht geladen werden: %s",
            fehler,
        )
        st.error(f"Professor-Daten konnten nicht geladen werden: {fehler}")
        st.stop()

    quelle: str = str(aktuelle_daten.get("quelle", "unbekannt"))

    if quelle == "professor_api":
        st.success("Echte Professor-Daten werden verwendet.")
    else:
        st.warning(f"Aktuelle Datenquelle: {quelle}")

    st.caption(
        f"Letzte Dashboard-Aktualisierung: {datetime.now().strftime('%H:%M:%S')}"
    )

    snapshots: pd.DataFrame = pd.DataFrame(historische_daten)

    if snapshots.empty:
        st.warning("Noch keine gespeicherten Snapshots vorhanden.")
        st.stop()

    try:
        kennzahlen: dict[str, float | str] = berechne_pv_dashboard_kennzahlen(snapshots)

    except ValueError as fehler:
        logger.error("PV-Kennzahlen konnten nicht berechnet werden: %s", fehler)
        st.error(f"PV-Kennzahlen konnten nicht berechnet werden: {fehler}")
        st.stop()

    zeige_pv_kennzahlen(kennzahlen, anzahl_snapshots=len(snapshots))
    zeige_pv_diagramme(snapshots, kennzahlen)


def zeige_pv_kennzahlen(
    kennzahlen: dict[str, float | str],
    anzahl_snapshots: int,
) -> None:
    """
    Zeigt die geforderten PV-Kennzahlen an.
    """
    st.subheader("Geforderte PV-Kennzahlen")

    if anzahl_snapshots < 2:
        st.info("""
            Es gibt bisher nur sehr wenige Snapshots.
            Deshalb können Tages-, Monats- und Jahreswerte noch fast gleich aussehen.
            """)

    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            "Momentanverbrauch",
            formatiere_kw(float(kennzahlen["momentanverbrauch_w"])),
        )

    with col2:
        st.metric(
            "Momentanerzeugung",
            formatiere_kw(float(kennzahlen["momentanerzeugung_w"])),
        )

    col3, col4 = st.columns(2)

    with col3:
        st.metric(
            "Tagesverbrauch",
            formatiere_kwh(float(kennzahlen["tagesverbrauch_wh"])),
        )

    with col4:
        st.metric(
            "Tageserzeugung",
            formatiere_kwh(float(kennzahlen["tageserzeugung_wh"])),
        )

    col5, col6 = st.columns(2)

    with col5:
        st.metric(
            "Monatsverbrauch",
            formatiere_kwh(float(kennzahlen["monatsverbrauch_wh"])),
        )

    with col6:
        st.metric(
            "Monatserzeugung",
            formatiere_kwh(float(kennzahlen["monatserzeugung_wh"])),
        )

    col7, col8 = st.columns(2)

    with col7:
        st.metric(
            "Jahresverbrauch",
            formatiere_kwh(float(kennzahlen["jahresverbrauch_wh"])),
        )

    with col8:
        st.metric(
            "Jahreserzeugung",
            formatiere_kwh(float(kennzahlen["jahreserzeugung_wh"])),
        )

    col9, col10, col11 = st.columns(3)

    with col9:
        st.metric(
            "PV-Anteil Tag",
            f"{float(kennzahlen['pv_anteil_tag']):.2f} %",
        )

    with col10:
        st.metric(
            "PV-Anteil Monat",
            f"{float(kennzahlen['pv_anteil_monat']):.2f} %",
        )

    with col11:
        st.metric(
            "PV-Anteil Jahr",
            f"{float(kennzahlen['pv_anteil_jahr']):.2f} %",
        )


def zeige_pv_diagramme(
    snapshots: pd.DataFrame,
    kennzahlen: dict[str, float | str],
) -> None:
    """
    Zeigt die geforderten PV-Diagramme an.
    """
    st.subheader("Zeitverlauf des aktuellen Tages")

    try:
        tagesverlauf: pd.DataFrame = erstelle_tagesverlauf(snapshots)

    except ValueError as fehler:
        st.warning(f"Tagesverlauf kann noch nicht erstellt werden: {fehler}")
        return

    diagramm_daten: pd.DataFrame = pd.DataFrame(
        {
            "Zeitpunkt": tagesverlauf["timestamp"],
            "Tageserzeugung (Wh)": tagesverlauf["tageserzeugung_wh"],
            "Tagesverbrauch (W)": tagesverlauf["verbrauch_w"],
        }
    )

    diagramm_daten = diagramm_daten.set_index("Zeitpunkt")

    st.line_chart(diagramm_daten)

    st.subheader("Verhältnis Verbrauch aus PV zu Gesamtverbrauch")

    st.caption("""
        Wenn der PV-Anteil bei 100 % liegt, bedeutet das:
        Der Verbrauch wurde rechnerisch vollständig durch PV gedeckt.
        Dann besteht das Tortendiagramm aus nur einem sichtbaren Anteil.
        """)

    col1, col2, col3 = st.columns(3)

    with col1:
        zeige_tortendiagramm(
            titel="Tag",
            verbrauch_wh=float(kennzahlen["tagesverbrauch_wh"]),
            erzeugung_wh=float(kennzahlen["tageserzeugung_wh"]),
        )

    with col2:
        zeige_tortendiagramm(
            titel="Monat",
            verbrauch_wh=float(kennzahlen["monatsverbrauch_wh"]),
            erzeugung_wh=float(kennzahlen["monatserzeugung_wh"]),
        )

    with col3:
        zeige_tortendiagramm(
            titel="Jahr",
            verbrauch_wh=float(kennzahlen["jahresverbrauch_wh"]),
            erzeugung_wh=float(kennzahlen["jahreserzeugung_wh"]),
        )

    with st.expander("Gespeicherte Professor-Snapshots anzeigen"):
        st.dataframe(snapshots)


def zeige_tortendiagramm(
    titel: str,
    verbrauch_wh: float,
    erzeugung_wh: float,
) -> None:
    """
    Zeigt ein sauberes Donut-Tortendiagramm für den PV-Anteil.
    """
    verbrauch_aus_pv_wh, netzbezug_wh, pv_anteil_prozent = berechne_verbrauchsanteile(
        verbrauch_wh,
        erzeugung_wh,
    )

    if verbrauch_wh <= 0:
        st.info(f"Für {titel} gibt es noch keinen Verbrauchswert.")
        return

    labels: list[str] = ["Verbrauch aus PV"]
    werte: list[float] = [verbrauch_aus_pv_wh]
    farben: list[str] = ["#00D084"]

    if netzbezug_wh > 0:
        labels.append("Netzbezug")
        werte.append(netzbezug_wh)
        farben.append("#FFB000")

    fig, ax = plt.subplots(figsize=(2.8, 2.8))

    ax.pie(
        werte,
        colors=farben,
        startangle=90,
        counterclock=False,
        wedgeprops={
            "width": 0.38,
            "edgecolor": "white",
            "linewidth": 2,
        },
    )

    ax.text(
        0,
        0.08,
        f"{pv_anteil_prozent:.1f} %",
        ha="center",
        va="center",
        fontsize=14,
        fontweight="bold",
    )

    ax.text(
        0,
        -0.16,
        "PV-Anteil",
        ha="center",
        va="center",
        fontsize=8,
    )

    ax.set_title(titel, fontsize=12, fontweight="bold")
    ax.axis("equal")

    st.pyplot(fig, use_container_width=False)
    plt.close(fig)

    st.markdown(f"""
        **{titel}**  
        Verbrauch aus PV: `{formatiere_kwh(verbrauch_aus_pv_wh)}`  
        Netzbezug: `{formatiere_kwh(netzbezug_wh)}`  
        Gesamtverbrauch: `{formatiere_kwh(verbrauch_wh)}`
        """)


def zeige_csv_dashboard() -> None:
    """
    Zeigt das alte Dashboard für CSV-Beispieldaten.
    """
    st.subheader("CSV-Beispieldaten")

    strompreis_pro_kwh: float = st.sidebar.number_input(
        "Strompreis pro kWh (€)",
        min_value=0.0,
        value=0.35,
        step=0.01,
    )

    daten: pd.DataFrame = lade_daten("data/input/example_data.csv")
    st.sidebar.success("CSV-Beispieldaten wurden geladen.")

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

    zeige_csv_kennzahlen(kennzahlen)
    zeige_csv_diagramme(daten)


def zeige_csv_kennzahlen(kennzahlen: dict[str, int | float | str]) -> None:
    """
    Zeigt Kennzahlen für CSV-Beispieldaten.
    """
    st.subheader("CSV-Kennzahlen")

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


def zeige_csv_diagramme(daten: pd.DataFrame) -> None:
    """
    Zeigt Diagramme für CSV-Beispieldaten.
    """
    st.subheader("CSV-Datenübersicht")
    st.dataframe(daten)

    st.subheader("Verbrauch und Erzeugung über Zeit")

    diagramm_daten: pd.DataFrame = daten.set_index("datum")[["verbrauch", "erzeugung"]]
    st.line_chart(diagramm_daten)

    st.subheader("Bilanz über Zeit")

    bilanz_daten: pd.DataFrame = daten.set_index("datum")[["bilanz"]]
    st.bar_chart(bilanz_daten)


if __name__ == "__main__":
    main()
