# Cuety (LPU-2) voor Home Assistant

**Versie 4.0.0**

Home Assistant-integratie voor de Visual Productions Quety (LPU-2). De integratie stuurt de playbacks aan via de lokale HTTP-API van de Quety. Je krijgt schakelaars, intensiteitsregelaars en knoppen, een sensor met het laatste antwoord, en services voor de commando's uit de API.



![Afbeelding beschrijving](https://i.imgur.com/qTj6VJn.png)


## Wat je krijgt

Per Quety krijg je deze entiteiten. De voorbeelden gaan uit van de naam `Cuety`.

- `switch.cuety_blackout`: blackout aan of uit
- `button.cuety_release_alle_playbacks`: alle playbacks loslaten
- `button.cuety_hello`: stuurt `/ajax/hello` en zet het antwoord in de sensor
- `button.cuety_status_opvragen`: vraagt `/ajax/pbxx/ac` op en zet het antwoord in de sensor
- `sensor.cuety_laatste_antwoord`: het antwoord van de laatste knopdruk
- Per playback, hier 11 als voorbeeld:
  - `switch.cuety_playback_11`: aan is Go+, uit is release
  - `number.cuety_playback_11_intensiteit`: intensiteit van 0 tot 100 %

Met playbacks 1 t/m 11 zijn dat 27 entiteiten in totaal. Daarnaast zijn er services voor alles wat niet als entiteit bestaat, zie [Services](#services).

## Vereisten

- Home Assistant 2024.4 of nieuwer
- Een Quety (LPU-2) op hetzelfde netwerk als Home Assistant, of Testmodus om zonder Quety te testen

## Installeren

### Handmatig

1. Pak `cuety_v4.zip` uit.
2. Kopieer de map `custom_components/cuety` naar de map `custom_components` in je Home Assistant-map `config`. Het resultaat is `config/custom_components/cuety/`.
3. Herstart Home Assistant volledig. Alleen de integratie herladen is niet genoeg, omdat de Python-code pas bij een herstart opnieuw wordt ingelezen.

Stond er al een eerdere versie in `config/custom_components/cuety/`? Verwijder die map dan eerst, zodat er geen oude bestanden overblijven.

### Via GitHub en HACS

1. Zet de inhoud van deze zip in een GitHub-repository.
2. Ga in HACS naar de drie puntjes rechtsboven en kies Aangepaste repositories. Vul de URL van je repository in en kies de categorie Integratie.
3. Download de integratie via HACS en herstart Home Assistant.

## Integratie toevoegen

1. Ga naar Instellingen → Apparaten en diensten → Integratie toevoegen en zoek op `Cuety`.
2. Vul de naam in, bijvoorbeeld `Cuety`, het IP-adres van de Quety en de poort. De standaardpoort is 80.
3. Heb je geen Quety bij de hand? Zet dan **Testmodus** aan. Er gaat dan niets naar het netwerk.
4. Klik bij de integratie op **Configureren** en vul bij **Aantal of bereik** in:

| Invoer | Playbacks |
|---|---|
| `11` | 1 t/m 11 |
| `5-11` | 5 t/m 11 |
| `11-11` | alleen 11 |

Een lijst met losse nummers, zoals `11, 12`, wordt niet ondersteund. Gebruik dan `11-12`. Het bereik moet tussen 1 en 99 liggen.

Wil je meer dan één Quety gebruiken? Voeg de integratie dan opnieuw toe, met een andere naam. Lees bij [Services](#services) hoe je dan het veld `quety` gebruikt.

## Knoppen en het laatste antwoord

De knoppen `Hello` en `Status opvragen` doen een opvraag bij de Quety. Het antwoord komt in de sensor `Laatste antwoord`.

- **Hello** stuurt `/ajax/hello`. Volgens de handleiding antwoordt de Quety daarop met `hello`.
- **Status opvragen** stuurt `/ajax/pbxx/ac`, de opvraag "Get all active playback status" uit de handleiding. De handleiding beschrijft de terugkoppeling van de status als een lijst met 0 en 1 per playback, bijvoorbeeld `[1,1,0,1,…]`.

De sensor toont het antwoord als status, tot 255 tekens. Dat is de maximale lengte van een statuswaarde in Home Assistant. Het volledige antwoord staat in het attribuut `volledig_antwoord`. Het attribuut `commando` laat zien welke knop het antwoord heeft opgehaald. Een nieuwe knopdruk vervangt het vorige antwoord.

## Hoe het werkt

**Detectie.** Bij het toevoegen en bij elke start stuurt de integratie `GET /ajax/hello` naar de Quety. Komt er een antwoord zonder foutcode, dan geldt de Quety als gevonden. Bij het toevoegen blijft het formulier dan staan met de melding dat de Quety niet bereikbaar is. Bij het opstarten probeert Home Assistant het later opnieuw.

**Commando's.** Elke actie is een `GET` naar `http://<ip>:<poort>/ajax/<commando>`. Zo betekent `/ajax/pb11/go+` dat playback 11 op Go+ gaat. Playbacks heten altijd met twee cijfers, `pb01` t/m `pb99`.

**Status.** De integratie leest de Quety niet uit. Home Assistant onthoudt de laatste stand die je vanuit Home Assistant hebt gezet, ook na een herstart. Verandert iemand de stand op de Quety zelf, dan ziet Home Assistant dat niet.

**Testmodus.** De integratie doet alsof er een Quety is. Er gaat niets naar het netwerk. Elk commando verschijnt als waarschuwing in het log, met de URL die verstuurd zou worden.

## Services

Je vindt de services onder Ontwikkelaarstools → Acties, bij `cuety`. Een voorbeeld:

```yaml
action: cuety.go_plus
data:
  playback: 11
```

Elke service heeft een optioneel veld `quety` met de naam van de integratie. Is er maar één Quety, dan laat je dat weg. Zijn er twee of meer, dan geef je de naam mee, bijvoorbeeld `quety: Cuety`.

Services met `ja` in de laatste kolom geven de tekst van de Quety terug. Die kun je opvangen met `response_variable` in een automatisering.

| Service | Velden | Werking | Geeft antwoord |
|---|---|---|---|
| `go_plus` | `playback` | Go+ op één playback | nee |
| `go_back` | `playback` | Go- op één playback | nee |
| `release` | `playback` | Release van één playback | nee |
| `release_all` | — | Alle playbacks loslaten | nee |
| `jump` | `playback`, `cue` (1 t/m 48) | Springen naar een cue | nee |
| `flash` | `playback`, `on` (aan of uit) | Flash aan of uit | nee |
| `press_button` | `playback`, `duration` (optioneel, standaard 0,1 s) | Knop nabootsen: kort is Go+, lang is release | nee |
| `set_intensity` | `playback`, `value` (0 t/m 1) | Intensiteit zetten | nee |
| `change_intensity` | `playback`, `delta` (-1 t/m 1) | Intensiteit verschuiven | nee |
| `get_intensity` | `playback` | Intensiteit uitlezen | ja |
| `set_speed` | `playback`, `value` (-1 t/m 1) | Snelheid zetten | nee |
| `change_speed` | `playback`, `delta` (-1 t/m 1) | Snelheid verschuiven, zie beperkingen | nee |
| `get_speed` | `playback` | Snelheid uitlezen | ja |
| `set_all_intensity` | `value` (0 t/m 1) | Intensiteit van alle playbacks zetten | nee |
| `get_all_intensity` | — | Intensiteit van alle playbacks uitlezen | ja |
| `set_all_speed` | `value` (0 t/m 1) | Snelheid van alle playbacks zetten | nee |
| `get_all_speed` | — | Snelheid van alle playbacks uitlezen | ja |
| `get_active_cues` | — | Actieve cues uitlezen | ja |
| `get_active_status` | — | Status van de playbacks uitlezen | ja |
| `blackout` | `on` (aan of uit) | Blackout aan of uit | nee |
| `hello` | — | Verbinding testen | ja |
| `raw` | `command` | Elk ander commando sturen, zoals `pb11/go+` | ja |

## Probleemoplossing

- **Config-flow kon niet geladen worden: 500.** Zoek in Instellingen → Systeem → Logboeken op `cuety`. Controleer ook of de map precies `custom_components/cuety` heet en of Home Assistant volledig is herstart.
- **Kan de Quety niet bereiken.** Controleer het IP-adres en de poort. Test in een browser met `http://<ip>:<poort>/ajax/hello`. Krijg je geen antwoord, dan ligt het aan het netwerk of aan de poort.
- **Meerdere Quety's gevonden.** Geef bij de service het veld `quety` mee.
- **Nieuwe playbacks verschijnen niet.** Wacht enkele seconden. De integratie herlaadt zichzelf na het opslaan van de instelling.
- **De sensor Laatste antwoord is leeg.** De sensor krijgt pas een waarde na een knopdruk op Hello of Status opvragen.

Een fout die hier niet bij staat? Meld die dan via de Issues van de repository, met de melding uit het log.

## Bekende beperkingen

- De detectie kijkt naar de statuscode van `/ajax/hello`, niet naar de inhoud van het antwoord. Elke server die op dat adres en die poort antwoordt zonder foutcode, telt als Quety. De handleiding geeft `hello` als antwoord; dat kan later voor strengere detectie worden gebruikt. In v4 is de detectie niet veranderd.
- Hoe het HTTP-antwoord op de statusopvraag eruitziet, is niet op een echte Quety getest. De sensor toont de tekst zoals hij binnenkomt.
- `change_speed` met een negatieve waarde is onzeker. De documentatie gebruikt bij snelheid een min zowel voor een absolute waarde als voor een verlaging. Gebruik voor een vaste snelheid liever `set_speed`.
- De documentatie gebruikt soms een en-dash (–) in plaats van een min. De integratie stuurt altijd een gewone min.
- De teksten die de services teruggeven, zoals `get_intensity`, komen rechtstreeks van de Quety. Het formaat is niet vastgelegd, dus de integratie leest ze niet uit.
- Playback 00 wordt niet gebruikt. Het maximum van 99 is een aanname.
- Niet op alle versies van Home Assistant getest.

## Versiegeschiedenis

- **4.0.0**: knoppen Hello en Status opvragen, en de sensor Laatste antwoord. De commando's zijn nagekeken tegen de HTTP-tabel in de handleiding. De entiteiten van 3.0.0 zijn ongewijzigd.
- **3.0.0**: versienummers in alle bestanden en deze README. De entiteiten, de API-client en de detectie zijn ongewijzigd sinds 1.0.0.
- **1.0.1**: playbacks als aantal of bereik. `11` geeft 1 t/m 11, `5-11` geeft 5 t/m 11. Losse lijsten werken niet meer.
- **1.0.0**: eerste werkende versie met een echte Quety, met schakelaars, intensiteit, blackout en release. Testmodus en detectie via `/ajax/hello`. Playbacks als lijst, zoals `11, 12`.

## Structuur

```
custom_components/cuety/
├── __init__.py            services en het opzetten van de integratie
├── api.py                 HTTP-client voor de Quety
├── button.py              knoppen: release, hello en status opvragen
├── config_flow.py         installatie en opties
├── const.py               constanten
├── entity.py              basis voor alle entiteiten
├── manifest.json          naam, domein en versie
├── number.py              intensiteit per playback
├── sensor.py              sensor met het laatste antwoord
├── switch.py              blackout en playbacks
└── translations/nl.json   teksten in het Nederlands
```

## Bronnen

- Handleiding van de Quety (LPU-2), Appendix A: de HTTP-tabel (A.4) en de terugkoppeling (A.5).

## Licentie

Nog niet gekozen.
