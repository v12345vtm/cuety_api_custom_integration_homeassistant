### Blueprints: Sonos naar Memotext

In zone 30 of zone 100 kun je deze Blueprint toevoegen via de URL:
`https://raw.githubusercontent.com/v12345vtm/cuety_api_custom_integration_homeassistant/refs/heads/main/memotext/media_memotext.yaml`

#### Benodigde Helpers
Zorg ervoor dat je de volgende helpers hebt aangemaakt in je `configuration.yaml`:

```yaml
input_text:
  keuken_media_kanaal:
    name: Keuken Media Kanaal
    max: 255
    icon: mdi:television
  keuken_media_artiest:
    name: Keuken Media Artiest
    max: 255
    icon: mdi:account-music
  keuken_media_titel:
    name: Keuken Media Titel
    max: 255
    icon: mdi:music
