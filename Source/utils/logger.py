import logging


def setup_logger() -> logging.Logger:
    """
    Erstellt und konfiguriert einen Logger für das Solar-Energy-Dashboard.

    Der Logger schreibt Log-Nachrichten sowohl in eine Datei
    als auch in die Konsole.

    Returns:
        logging.Logger: Konfigurierter Logger für die Anwendung.
    """
    logger: logging.Logger = logging.getLogger("solar_energy_logger")
    logger.setLevel(logging.INFO)

    # Verhindert doppelte Handler bei erneutem Aufruf
    if logger.handlers:
        return logger

    formatter: logging.Formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(message)s"
    )

    file_handler: logging.FileHandler = logging.FileHandler(
        "solar_energy_app.log",
        encoding="utf-8"
    )
    file_handler.setFormatter(formatter)

    console_handler: logging.StreamHandler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger