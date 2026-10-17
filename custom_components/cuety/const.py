# Cuety-integratie, versie 4.0.0
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
    """Signaal waarmee de knoppen het antwoord naar de tekstentiteit sturen."""
    return f"{DOMAIN}_antwoord_{entry_id}"
