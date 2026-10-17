# Cuety-integratie, versie 5.0.0
"""Constanten en signaalnamen van de Cuety-integratie."""

DOMAIN = "cuety"

CONF_NAME = "name"
CONF_HOST = "host"
CONF_PORT = "port"
CONF_PLAYBACKS = "playbacks"
CONF_DEMO = "demo"

DEFAULT_PORT = 80
MAX_PLAYBACK = 99

# De docs noemen het snelheidscommando zowel /spd= als /sp=. Werkt snelheid niet? Zet dit op "sp".
SPEED = "spd"


def antwoord_signal(entry_id: str) -> str:
    """Signaal waarmee de client elk antwoord naar de tekstentiteit httpresponse stuurt."""
    return f"{DOMAIN}_antwoord_{entry_id}"


def refresh_signal(entry_id: str) -> str:
    """Signaal waarmee lights en de blackout-schakelaar hun stand opnieuw ophalen."""
    return f"{DOMAIN}_refresh_{entry_id}"
