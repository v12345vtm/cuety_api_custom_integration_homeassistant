# Cuety (LPU-2) voor Home Assistant

![Cuety (LPU-2)](https://i.imgur.com/qTj6VJn.png)

**Versie 5.2.0**

Home Assistant-integratie voor de Visual Productions Quety (LPU-2). De integratie stuurt de playbacks aan via de lokale HTTP-API van de Quety. Per playback krijg je een light. Daarnaast zijn er een schakelaar voor de blackout, knoppen, een sensor met de antwoorden van de Quety en services voor de commando's uit de API. Met de testmodus kun je alles uitproberen zonder Quety.

## Links

- Repository: https://github.com/v12345vtm/cuety_api_custom_integration_homeassistant
- Problemen melden: https://github.com/v12345vtm/cuety_api_custom_integration_homeassistant/issues
- Virtuele Cuety op GitHub: https://github.com/v12345vtm/cuety_api_custom_integration_homeassistant/blob/main/virtualcuety/virtualcuetyv5_1.py

## Wat je krijgt

Per Quety, met de naam `Cuety` als voorbeeld:

- `light.cuety_playback_11`: per playback. Aan is Go+, uit is release, en de helderheid is de intensiteit. Hier playback 11 als voorbeeld.
- `switch.cuety_blackout`: blackout aan of uit
- `button.cuety_release_alle_playbacks`: alle playbacks loslaten
- `button.cuety_hello`: stuurt `/ajax/hello`
- `button.cuety_status_opvragen`: stuurt `/ajax/pbxx/ac` en ververst daarna alle lights
- `sensor.cuety_httpresponse`: het antwoord van de Quety op het laatste commando

Met playbacks 1 t/m 11 zijn dat 16 entiteiten. Daarnaast zijn er services, zie [Services](#services).

## Migratie van versie 4

Versie 5 vervangt de schakelaar en de intensiteitsregelaar per playback door één light:

- `switch.cuety_playback_N` en `number.cuety_playback_N_intensiteit` bestaan niet meer. Gebruik `light.cuety_playback_N`.
- Pas je automatiseringen en dashboards aan.
- De oude entiteiten blijven in Home Assistant staan als niet beschikbaar. Verwijder ze via Instellingen → Apparaten en diensten → Entiteiten.
- De integratie hoeft niet opnieuw toegevoegd te worden. Vervang de map en herstart Home Assistant.

## Vereisten

- Home Assistant 2024.4 of nieuwer
- Een Quety (LPU-2) op hetzelfde netwerk als Home Assistant, of de testmodus

## Installeren

### Handmatig

1. Pak `cuety_v5.2.zip` uit. Je ziet dan `README.md` en de map `custom_components`.
2. Kopieer de map `custom_components/cuety` naar de map `custom_components` in je Home Assistant-map `config`. Het resultaat is `config/custom_components/cuety/`.
3. Herstart Home Assistant volledig. Alleen de integratie herladen is niet genoeg, omdat de Python-code pas bij een herstart opnieuw wordt ingelezen.

Stond er al een eerdere versie in `config/custom_components/cuety/`? Verwijder die map dan eerst, zodat er geen oude bestanden overblijven.

Het bestand `custom_components/virtuele_cuety.py` hoort niet bij de integratie. Het is een losstaand hulpmiddel om een Quety na te bootsen op je pc. Je hoeft het niet naar Home Assistant te kopiëren.

### Via GitHub en HACS

1. Ga in HACS naar de drie puntjes rechtsboven en kies Aangepaste repositories.
2. Vul als URL in: `https://github.com/v12345vtm/cuety_api_custom_integration_homeassistant` en kies de categorie Integratie.
3. Download de integratie via HACS en herstart Home Assistant.

## Integratie toevoegen

1. Ga naar Instellingen → Apparaten en diensten → Integratie toevoegen en zoek op `Cuety`.
2. Vul de naam in, bijvoorbeeld `Cuety`, het IP-adres van de Quety en de poort. De standaardpoort is 80.
3. Heb je geen Quety bij de hand? Zet dan **Testmodus** aan. Zie [Testmodus](#testmodus).
4. Klik bij de integratie op **Configureren** en vul bij **Aantal of bereik** in:

| Invoer | Playbacks |
|---|---|
| `11` | 1 t/m 11 |
| `5-11` | 5 t/m 11 |
| `11-11` | alleen 11 |

Een lijst met losse nummers, zoals `11, 12`, wordt niet ondersteund. Gebruik dan `11-12`. Het bereik moet tussen 1 en 99 liggen.

Wil je meer dan één Quety gebruiken? Voeg de integratie dan opnieuw toe, met een andere naam. Lees bij [Services](#services) hoe je dan het veld `quety` gebruikt.

## Testmodus

Met Testmodus gaat er niets naar het netwerk. De integratie heeft dan een ingebouwde simulator (`cuety/virtueel.py`). Die gebruikt dezelfde logica als `virtuele_cuety.py`.

- Lights, schakelaar, knoppen en sensor gedragen zich als bij een echte Quety: aan en uit, de helderheid, Release alle playbacks, de blackout en het antwoord in `httpresponse`.
- Elke Cuety-entiteit in de testmodus heeft zijn eigen stand. Na een herstart van Home Assistant begint die weer met alles uit.

## Virtuele Cuety (losstaand bestand)

`custom_components/virtuele_cuety.py` is een server die antwoordt als een Quety, op je pc of op een ander apparaat. Gebruik het als je de integratie met echt netwerkverkeer wilt testen, of als je andere programma's op een Quety wilt laten lijken.

Start het in een terminal, in de map `custom_components`:

```
python virtuele_cuety.py --port 8080
```

Poort 80, de standaard, kan alleen met admin-rechten. Met `--snapshot` begint de virtuele Cuety met pb3 aan en cue 1 op pb2.

In de integratie vul je dan het IP-adres van je pc in, poort `8080`, en zet je Testmodus uit.

Probeer in je browser: `http://<ip>:8080/ajax/hello`, `/ajax/pb01/go+`, `/ajax/pbxx/ac`, `/ajax/pbxx/rel` en `/mock/state`.

De virtuele Cuety is een nabootsing. Wat op een echte Quety is gezien, staat in de code als GEZIEN. Wat een aanname is, staat als AANNAME, bijvoorbeeld hoe de cue opschuift en hoe lang een knopdruk moet duren om release te worden. Zie je iets dat niet klopt met je echte Quety, meld het dan via de [Issues](https://github.com/v12345vtm/cuety_api_custom_integration_homeassistant/issues).

Let op: de virtuele Cuety op GitHub (`virtualcuetyv5_1.py`) is een oudere versie dan die in deze zip.

## Lights per playback

- **Aanzetten:** als er een helderheid is, stuurt de light eerst de intensiteit (`/ajax/pbNN/int=0.59`). Staat de playback nog uit, dan volgt Go+ (`/ajax/pbNN/go+`). Staat hij al aan, dan wordt alleen de intensiteit gezet. Zo springt de cue niet door.
- **Uitzetten:** release (`/ajax/pbNN/rel`).
- **Helderheid veranderen** terwijl de playback aan staat: alleen de intensiteit.
- **Stand:** na elk commando haalt de light de stand op bij de Quety, met `/ajax/pbNN/ac` (aan of uit) en `/ajax/pbNN/int` (intensiteit). Zo klopt de stand in Home Assistant met de hardware.

De helderheid van Home Assistant (0 t/m 255) wordt omgerekend naar de intensiteit van de Quety (0,00 t/m 1,00).

## Knoppen, httpresponse en de stand

- Elk commando dat Home Assistant naar de Quety stuurt, zet het antwoord in `sensor.cuety_httpresponse`. Het attribuut `commando` laat zien welk commando het was. Het attribuut `volledig_antwoord` bevat de volledige tekst. De status van de sensor toont de eerste 255 tekens.
- Opvragingen voor de stand komen niet in de sensor. Zo blijft het antwoord op je eigen commando zichtbaar.
- `button.cuety_hello` stuurt `/ajax/hello`.
- `button.cuety_status_opvragen` stuurt `/ajax/pbxx/ac` en ververst daarna alle lights.
- `button.cuety_release_alle_playbacks` stuurt `/ajax/pbxx/rel` en ververst daarna alle lights.

## Voorbeeldantwoorden van een echte Quety

| Commando | Antwoord |
|---|---|
| `/ajax/hello` | `{"hello":1,"apicall":"succeeded"}` |
| `/ajax/status` | `{"label":"MyLPU-2","receiving":{"osc":0,"udp":0,"tcp":0}}` (niet in de handleiding, wel op het apparaat) |
| `/ajax/pbxx/ac` | `{"ac":[0,0,1,0,…],"apicall":"succeeded"}` (een lijst met een 0 of 1 per playback) |
| `/ajax/pbxx/cue` | `{"cue":["-",1,"-",…],"apicall":"succeeded"}` |
| `/ajax/pb10/ac` | `{"ac":0,"apicall":"succeeded"}` (0 is uit, 1 is aan) |
| `/ajax/pb10/int` | `{"intensity":0.60,"apicall":"succeeded"}` (0 t/m 1) |
| `/ajax/pbNN/spd` | `{"speed":0.20,"apicall":"succeeded"}` |
| `/ajax/blackout=1` | `{"blackout":1,"apicall":"succeeded"}` |
| `/ajax/pbNN/go+` | `{"apicall":"succeeded"}` |

Een commando zonder waarde, zoals `go+`, geeft alleen `{"apicall":"succeeded"}` terug. Een opvraag geeft de waarde terug onder de naam van het commando.

## Hoe het werkt

**Detectie.** Bij het toevoegen en bij elke start stuurt de integratie `GET /ajax/hello` naar de Quety. Komt er een antwoord zonder foutcode, dan geldt de Quety als gevonden. Bij het toevoegen blijft het formulier dan staan met de melding dat de Quety niet bereikbaar is. Bij het opstarten probeert Home Assistant het later opnieuw.

**Commando's.** Elke actie is een `GET` naar `http://<ip>:<poort>/ajax/<commando>`. Zo betekent `/ajax/pb11/go+` dat playback 11 op Go+ gaat. Playbacks heten altijd met twee cijfers, `pb01` t/m `pb99`. Verzoeken gaan één voor één naar de Quety, zodat het kleine apparaat niet overbelast raakt.

**Stand.** De lights en de blackout-schakelaar halen de stand op: bij het opstarten, na een eigen commando, na een service die de stand verandert, en na de knoppen Status opvragen en Release alle playbacks. Verandert iemand de stand op de Quety zelf, dan zie je dat pas na het volgende commando of na Status opvragen.

**Testmodus.** Zie [Testmodus](#testmodus). Er gaat niets naar het netwerk; de simulator houdt de stand bij.

## Services

Je vindt de services onder Ontwikkelaarstools → Acties, bij `cuety`. Een voorbeeld:

```yaml
action: cuety.go_plus
data:
  playback: 11
```

Elke service heeft een optioneel veld `quety` met de naam van de integratie. Is er maar één Quety, dan laat je dat weg. Zijn er twee of meer, dan geef je de naam mee, bijvoorbeeld `quety: Cuety`.

Services met `ja` in de laatste kolom geven de tekst van de Quety terug. Die kun je opvangen met `response_variable` in een automatisering.

Na een service die de stand verandert, ververst de integratie de light of de schakelaar die erbij hoort.

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
- **De light toont de verkeerde stand.** Druk op Status opvragen. Klopt het dan nog niet, controleer dan in een browser `http://<ip>:<poort>/ajax/pb10/ac` en meld het via de Issues van de repository, met het antwoord.
- **De light is niet beschikbaar.** Dan geeft de Quety geen antwoord op de opvraag van de stand. Zie hierboven.
- **Nieuwe playbacks verschijnen niet.** Wacht enkele seconden. De integratie herlaadt zichzelf na het opslaan van de instelling.
- **In de testmodus klopt een antwoord niet met je echte Quety.** De testmodus volgt dezelfde logica als de virtuele Cuety, en die bevat aannames. Meld het via de Issues.

## Bekende beperkingen

- De detectie kijkt naar de statuscode van `/ajax/hello`, niet naar de inhoud van het antwoord. Elke server die op dat adres en die poort antwoordt zonder foutcode, telt als Quety.
- Een wijziging op de Quety zelf zie je pas na een commando of na Status opvragen.
- `change_speed` met een negatieve waarde is onzeker. De documentatie gebruikt bij snelheid een min zowel voor een absolute waarde als voor een verlaging. Gebruik voor een vaste snelheid liever `set_speed`.
- De documentatie gebruikt soms een en-dash (–) in plaats van een min. De integratie stuurt altijd een gewone min.
- Playback 00 wordt niet gebruikt. Het maximum van 99 is een aanname.
- De testmodus en de virtuele Cuety zijn nabootsingen. Hun aannames (zie AANNAME in de code) kloppen niet altijd met een echte Quety.
- Niet op alle versies van Home Assistant getest.

## TODO

- Snelheid (`spd`) per playback als entiteit toevoegen. De services bestaan al, maar er is nog geen entiteit.
- De detectie strenger maken met het antwoord van `/ajax/hello` (`"hello":1`) of met het label uit `/ajax/status`.
- Periodiek verversen van de stand, voor als de Quety ook door anderen wordt bediend. Nu gebeurt het na commando's en op verzoek.
- De lijst van `/ajax/pbxx/ac` gebruiken voor één snelle opvraag van alle playbacks, zodra vaststaat welke positie bij welke playback hoort.

## Versiegeschiedenis

- **5.2.0**: de testmodus gebruikt een ingebouwde simulator met dezelfde logica als de virtuele Cuety. Lights, release alle playbacks, blackout en httpresponse werken daardoor ook in de testmodus. De virtuele Cuety zit nu in de zip, naast de cuety-map. Afbeelding en links in de README en het manifest.
- **5.1.0**: de stand per playback is bevestigd op een echte Quety (`/ajax/pbNN/ac` geeft `ac`, `/ajax/pbNN/int` geeft `intensity`). Verzoeken gaan één voor één naar de Quety. README bijgewerkt.
- **5.0.0**: per playback één light, die de schakelaar en de intensiteitsregelaar vervangt. De antwoorden van de Quety worden als JSON verwerkt. De stand wordt na commando's opgehaald. De sensor heet nu httpresponse en toont het antwoord op elk commando.
- **4.0.0**: knoppen Hello en Status opvragen, en de sensor Laatste antwoord.
- **3.0.0**: versienummers in alle bestanden en deze README.
- **1.0.1**: playbacks als aantal of bereik. `11` geeft 1 t/m 11, `5-11` geeft 5 t/m 11. Losse lijsten werken niet meer.
- **1.0.0**: eerste werkende versie met een echte Quety, met schakelaars, intensiteit, blackout en release. Testmodus en detectie via `/ajax/hello`. Playbacks als lijst, zoals `11, 12`.

## Structuur

```
README.md                                 deze uitleg
custom_components/
├── cuety/                                de integratie
│   ├── __init__.py                       services en het opzetten van de integratie
│   ├── api.py                            HTTP-client, met de testmodus
│   ├── button.py                         knoppen: release, hello en status opvragen
│   ├── config_flow.py                    installatie en opties
│   ├── const.py                          constanten en signaalnamen
│   ├── entity.py                         basis voor alle entiteiten
│   ├── light.py                          light per playback
│   ├── manifest.json                     naam, domein, versie en links
│   ├── sensor.py                         httpresponse
│   ├── switch.py                         blackout
│   ├── virtueel.py                       simulator voor de testmodus
│   └── translations/nl.json              teksten in het Nederlands
└── virtuele_cuety.py                     losstaande virtuele Cuety, niet voor Home Assistant
```

## Bronnen

- Handleiding van de Quety (LPU-2), Appendix A: A.3 (TCP en UDP), A.4 (HTTP-tabel) en A.5 (terugkoppeling via de API).
- API-documentatie: https://api.visualproductions.nl/

## Licentie

Nog niet gekozen.
