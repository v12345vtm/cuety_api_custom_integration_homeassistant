# Cuety Integratie voor Home Assistant

Welkom bij de repository van de **Cuety** custom component voor Home Assistant. Met deze integratie kun je je Cuety-verlichtingscontroller handmatig koppelen, bedienen en automatiseren binnen je Home Assistant-omgeving.

## 📋 Inhoudsopgave

* [Functies](#-functies)
* [Vereisten](#-vereisten)
* [Handmatige Installatie](#-handmatige-installatie)
* [Configuratie & Playbacks](#-configuratie--playbacks)
* [🧪 Testen / Testmodus](#-testen--testmodus)
* [Ondersteuning & Vragen](#-ondersteuning--vragen)

## ✨ Functies

* Configuratie via de Home Assistant gebruikersinterface (Config Flow).
* Ondersteuning voor knoppen (`button`), schakelaars (`switch`) en numerieke instellingen (`number`).
* Ingebouwde **Testmodus** om commando's en URL's te verifiëren zonder het fysieke apparaat aan te sturen.
* Flexibele playback-invoer (enkel getal of bereik).
* Volledige Nederlandse vertaling (`nl.json`) inbegrepen.

## 🛠️ Vereisten

* Een werkende installatie van **Home Assistant** (Core of Supervisor).
* Een bereikbare Cuety-controller op je lokale netwerk.

## 📥 Handmatige Installatie

Omdat deze integratie handmatig geïnstalleerd dient te worden (en niet via de standaard HACS-store loopt), voeg je de bestanden als volgt toe:

1. Download of kloon deze repository naar je computer.
2. Zorg ervoor dat je de map genaamd `cuety` hebt (deze bevat de bestanden zoals `__init__.py`, `manifest.json`, etc.).
3. Plaats de map `cuety` in de map `custom_components` van je Home Assistant configuratiemap.
   * Het volledige pad moet er als volgt uitzien: `/config/custom_components/cuety/`
4. Herstart je Home Assistant-instantie om de nieuwe component te laden.

## ⚙️ Configuratie & Playbacks

Nadat de bestanden zijn geplaatst en Home Assistant is herstart, kun je de integratie toevoegen:

1. Ga naar **Instellingen** → **Apparaten & Diensten** in je Home Assistant dashboard.
2. Klik rechtsboven op de knop **+ Integratie toevoegen**.
3. Zoek naar **Cuety** en selecteer deze uit de lijst.
4. Vul de gewenste gegevens in (zoals Naam, IP-adres en Poort) en klik op **Opslaan**.

### 🎛️ Playback configuratie

Bij het instellen of wijzigen van de opties (via de knop **Configureren** bij de integratie) geef je de gewenste playbacks op:

* **Enkel getal:** Een getal *N* betekent playbacks 1 t/m *N*. Invullen van `11` genereert dus 11 sets entiteiten.
* **Bereik:** Je kunt een bereik opgeven, bijvoorbeeld `5-11`.
* **Lijsten:** Een losse lijst met komma's (zoals `11, 12, 13`) wordt **niet** ondersteund. Schrijf dit als een bereik: `11-13`.

> **Voorbeeld bij 11 playbacks:**  
> Bij het instellen van 11 playbacks worden in totaal **24 entiteiten** aangemaakt:  
> * 11 schakelaars (playbacks)  
> * 11 regelaars (intensiteit)  
> * 1 blackout-schakelaar  
> * 1 knop om alle playbacks los te laten (*release*)  
>  
> De gegenereerde URL's gebruiken automatisch een voorloopnul conform de documentatie (`pb01` t/m `pb11`).

## 🧪 Testen / Testmodus

In de testmodus reageert de echte Cuety-controller niet. De schakelaars tonen alleen wat Home Assistant zelf heeft ingesteld. Dit is ideaal om te controleren of de integratie de juiste URL-payloads opbouwt.

1. **Herstart Home Assistant.**
2. **Voeg de integratie toe:** Ga naar **Instellingen** → **Apparaten en diensten** → **Integratie toevoegen** en kies **Cuety**.
   * **Naam:** `Cuety`
   * **IP:** `192.168.2.29`
   * **Poort:** `80`
   * **Testmodus:** Vink de optie *Testmodus aan* aan.
3. **Configureer playbacks:** Open de integratie, klik op **Configureren** en vul bij playbacks `11` in.
4. **Controleer gemaakte entiteiten:** Je krijgt nu onder andere:
   * `switch.cuety_playback_11`
   * `number.cuety_playback_11_intensiteit`
   * `switch.cuety_blackout`
   * `button.cuety_release_alle_playbacks`
5. **Verifieer logboeken:**  
   Zet `switch.cuety_playback_11` aan en ga naar **Instellingen** → **Systeem** → **Logboeken**.  
   Daar zie je de URL die zou worden verstuurd, bijvoorbeeld:  
   `http://192.168.2.29:80/ajax/pb11/go+`  
   Als deze overeenkomt met je oude Node-RED payload (`/ajax/pb11/go+`), bouwt de integratie de commando’s correct op.

## 💬 Ondersteuning & Vragen

Heb je vragen, loop je tegen een probleem aan of wil je een suggestie doen? Open dan gerust een *Issue* in deze repository!
