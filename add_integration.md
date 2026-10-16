# Cuety Integratie voor Home Assistant

Welkom bij de repository van de **Cuety** custom component voor Home Assistant. Met deze integratie kun je je Cuety-verlichtingscontroller handmatig koppelen, bedienen en automatiseren binnen je Home Assistant-omgeving.

## 📋 Inhoudsopgave

* [Functies](#-functies)
* [Vereisten](#-vereisten)
* [Handmatige Installatie](#-handmatige-installatie)
* [Configuratie & Instellen](#-configuratie--instellen)
* [Ondersteuning & Vragen](#-ondersteuning--vragen)

## ✨ Functies

* Configuratie via de Home Assistant gebruikersinterface (Config Flow).
* Ondersteuning voor knoppen (`button`), schakelaars (`switch`) en numerieke instellingen (`number`).
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

## 💬 Ondersteuning & Vragen

Heb je vragen, loop je tegen een probleem aan of wil je iets melden? Open dan gerust een *Issue* in deze repository!
