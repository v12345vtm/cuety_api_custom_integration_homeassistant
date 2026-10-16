# Cuety Integratie voor Home Assistant

Welkom bij de repository van de **Cuety** custom component voor Home Assistant. Met deze integratie kun je je Cuety-verlichtingscontroller handmatig koppelen, bedienen en automatiseren binnen je Home Assistant-omgeving.

## 📋 Inhoudsopgave

* [Functies](#-functies)
* [Vereisten](#-vereisten)
* [Handmatige Installatie](#-handmatige-installatie)
* [Configuratie & Instellen](#-configuratie--instellen)
* [🧪 Testen / Testmodus](#-testen--testmodus)
* [Ondersteuning & Vragen](#-ondersteuning--vragen)

## ✨ Functies

* Configuratie via de Home Assistant gebruikersinterface (Config Flow).
* Ondersteuning voor knoppen (`button`), schakelaars (`switch`) en numerieke instellingen (`number`).
* Ingebouwde **Testmodus** om commando's en URL's te verifiëren zonder het fysieke apparaat aan te sturen.
* Volledige Nederlandse vertaling (`nl.json`) inbegrepen.

## 🛠️ Vereisten

* Een werkende installatie van **Home Assistant** (Core of Supervisor).
* Een bereikbare Cuety-controller op je lokale netwerk.

## 📥 Handmatige Installatie

Omdat deze integratie niet via de officiële HACS-store wordt aangeboden, dien je de bestanden handmatig aan je Home Assistant-omgeving toe te voegen:

1. Download of kloon deze repository naar je computer.
2. Zorg ervoor dat je de map genaamd `cuety` hebt (deze bevat de bestanden zoals `__init__.py`, `manifest.json`, etc.).
3. Plaats de map `cuety` in de map `custom_components` van je Home Assistant configuratiemap.
   * Het volledige pad moet er als volgt uitzien: `/config/custom_components/cuety/`
4. Herstart je Home Assistant-instantie om de nieuwe component te laden.

## ⚙️ Configuratie & Instellen

Nadat de bestanden zijn geplaatst en Home Assistant is herstart, kun je de integratie toevoegen:

1. Ga naar **Instellingen** > **Apparaten & Diensten** in je Home Assistant dashboard.
2. Klik rechtsboven op de knop **+ Integratie toevoegen**.
3. Zoek naar **Cuety** en selecteer deze uit de lijst.
4. Volg de instructies op het scherm (vul bijvoorbeeld het IP-adres van je Cuety-apparaat in).
5. Klik op **Opslaan** om de koppeling te voltooien.

Je Cuety-apparaten en bijbehorende entiteiten verschijnen direct in je overzicht en zijn klaar voor gebruik in dashboards en automatiseringen.

## 🧪 Testen / Testmodus

In testmodus reageert de echte Cuety niet. De schakelaars tonen alleen wat Home Assistant zelf heeft gezet. Je kunt deze modus gebruiken om de opbouw van de commando's te controleren:

1. **Herstart Home Assistant.**
2. **Voeg de integratie toe:** Ga naar **Instellingen** → **Apparaten & Diensten** → **Integratie toevoegen** en kies **Cuety**.
   * **Naam:** `Cuety`
   * **IP:** `192.168.2.29`
   * **Poort:** `80`
   * **Testmodus:** Vink deze optie aan (*Zet Testmodus aan*).
3. **Configureer playbacks:** Open de integratie, klik op **Configureren** en vul bij playbacks bijvoorbeeld `11` in.
4. **Controleer entiteiten:** Je krijgt nu onder andere de volgende entiteiten:
   * `switch.cuety_playback_11`
   * `number.cuety_playback_11_intensiteit`
   * `switch.cuety_blackout`
   * `button.cuety_release_alle_playbacks`
5. **Verifieer logboeken:** Zet `switch.cuety_playback_11` aan en kijk in **Instellingen** → **Systeem** → **Logboeken**. 
   * Daar staat de URL die zou worden verstuurd, bijvoorbeeld: `http://192.168.2.29:80/ajax/pb11/go+`
   * Die moet gelijk zijn aan je oude Node-RED-payload (`/ajax/pb11/go+`). Als dit klopt, bouwt de integratie de commando’s goed op.

## 💬 Ondersteuning & Vragen

Heb je vragen, loop je tegen een probleem aan of wil je iets melden? Open dan gerust een *Issue* in deze repository!
