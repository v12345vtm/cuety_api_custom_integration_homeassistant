todo 


# Analyse van je bug

Ja, je code kan dit gedrag verklaren. Ik zie twee mogelijke oorzaken, waarvan de eerste veruit de waarschijnlijkste is. Ik leg ze allebei uit, met een concrete fix.

## Oorzaak 1 (meest waarschijnlijk): de verse poll overschrijft je juiste lokale stand

In `light.py`:

```python
async def async_turn_off(self, **kwargs: Any) -> None:
    await self._client.release(self._playback)
    self._attr_is_on = False                              # (1) juiste stand
    await self.async_update_ha_state(force_refresh=True)  # (2) → async_update()
```

en `async_update()`:

```python
async def async_update(self) -> None:
    actief = await self._client.get_playback_active(self._playback)   # pbXX/ac
    ...
    if actief is not None:
        self._attr_is_on = actief                     # (3) overschrijft (1)
```

De volgorde is dus:

1. `release()` stuurt `pb01/rel`. De Quety zet de playback fysiek uit.
2. Jij zet `_attr_is_on = False`.
3. `async_update_ha_state(force_refresh=True)` doet **meteen** een `pb01/ac`.
4. De Quety heeft zijn eigen `ac`-vlag nog niet bijgewerkt (duurt even op echte hardware), dus antwoordt `{"ac":1,...}`.
5. `_attr_is_on` wordt weer `True`. De entiteit blijft dus "on" in HA, terwijl het fysiek uit is.

Waarom de **Status opvragen**-knop wél werkt: die doet eerst een `get_active_status()` (dat is een HTTP-roundtrip, dus ~100 ms vertraging), en pas daarna `async_dispatcher_send(...)`. Elke light doet dan `async_schedule_update_ha_state(True)`, wat als *task* wordt ingepland (nog een paar ms extra). Tegen de tijd dat `async_update()` pollt, is de Quety bijgewerkt en geeft `ac:0` terug → alles klopt.

Het verschil is dus puur **timing**: bij `light.turn_off` poll je te snel; bij de knop niet.

## Oorzaak 2 (minder waarschijnlijk, maar check je logs)

`_controleer()` in `api.py` gooit een `CueyError` als de Quety `apicall` op iets anders dan `"succeeded"` zet. Als `pbXX/rel` op jouw firmware een ander antwoord geeft dan `{"apicall":"succeeded"}`, dan:

- gaat het fysieke commando wel door (het is al verzonden),
- maar `async_turn_off` crasht vóór `_attr_is_on = False`,
- dus blijft HA "on" tonen.

**Check:** staat er in je HA-log een `CueyError ... op 'pb01/rel'` na het schakelen? Zo ja → oorzaak 2. Zo nee → oorzaak 1.

## De fix

Voor oorzaak 1 (en als bonus ook netter voor oorzaak 2) is de oplossing: **niet pollen direct na een geslaagd commando**. Je weet de nieuwe stand al (je hebt hem zelf net gezet), dus schrijf die gewoon weg met `async_write_ha_state()`. Dat stuurt geen HTTP-verzoek en overschrijft dus niets met verouderde data.

### `light.py`

```python
async def async_turn_on(self, **kwargs: Any) -> None:
    brightness = kwargs.get(ATTR_BRIGHTNESS)
    if brightness is not None:
        await self._client.set_intensity(self._playback, _naar_intensiteit(brightness))
        self._attr_brightness = brightness
    if not self._attr_is_on:
        await self._client.go(self._playback)
        self._attr_is_on = True
    self.async_write_ha_state()          # was: await self.async_update_ha_state(force_refresh=True)

async def async_turn_off(self, **kwargs: Any) -> None:
    await self._client.release(self._playback)
    self._attr_is_on = False
    self.async_write_ha_state()          # was: await self.async_update_ha_state(force_refresh=True)
```

### `switch.py` (heeft exact dezelfde bug)

```python
async def async_turn_on(self, **kwargs: Any) -> None:
    await self._client.blackout(True)
    self._attr_is_on = True
    self.async_write_ha_state()

async def async_turn_off(self, **kwargs: Any) -> None:
    await self._client.blackout(False)
    self._attr_is_on = False
    self.async_write_ha_state()
```

Wil je toch periodiek verifiëren of de Quety het echt heeft overgenomen, dan kun je na het schrijven een **uitgestelde** refresh inplannen (bv. 0,5 s later), zodat de Quety tijd heeft om bij te werken:

```python
import asyncio

async def async_turn_off(self, **kwargs: Any) -> None:
    await self._client.release(self._playback)
    self._attr_is_on = False
    self.async_write_ha_state()
    self.hass.async_create_task(self._navertrekken())

async def _navertrekken(self) -> None:
    await asyncio.sleep(0.5)
    await self.async_update_ha_state(force_refresh=True)
```

Maar in de praktijk is `async_write_ha_state()` alleen genoeg; de **Status opvragen**-knop blijft dan je handmatige "corrigeer alles"-knop.

## Klein detail

In `async_turn_on` staat `if not self._attr_is_on:` — als `_attr_is_on` nog `None` is (net na opstarten), is `not None` = `True`, dus je stuurt onterecht een `go+`. Beter is `if self._attr_is_on is not True:` of `if not self._attr_is_on:` vervangen door `if self._attr_is_on is False:`. Niet de bug die je meldt, maar wel een kleine verbetering.

## Samenvatting

- **Bug**: je pollt de Quety onmiddellijk na het commando; de Quety is dan nog niet bijgewerkt, en de verse (maar verouderde) poll overschrijft je juiste lokale stand.
- **Waarom de knop werkt**: die introduceert van nature vertraging (HTTP-request + scheduled task), genoeg voor de Quety om bij te werken.
- **Fix**: `async_write_ha_state()` in plaats van `async_update_ha_state(force_refresh=True)` in `async_turn_on`/`async_turn_off` van zowel `light.py` als `switch.py`.
