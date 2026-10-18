"""Virtuele Cuety (LPU-2) voor testen zonder hardware. ( v5.1.0)

Antwoordt op dezelfde URL's met hetzelfde JSON-formaat als de echte Quety.
In de commentaren staat wat op een echte Quety is gezien (GEZIEN),
wat uit de handleiding komt (HANDLEIDING) en wat een aanname is (AANNAME).

Starten:     python virtuele_cuety.py                (poort 80, dat vraagt admin-rechten)
             python virtuele_cuety.py --port 8080
Beginstand:  python virtuele_cuety.py --snapshot     (pb3 aan, cue 1 op pb2, zoals in je voorbeeld)

Hulpmiddelen (geen onderdeel van de echte Quety): /mock/state en /mock/httpresponse.
"""
from __future__ import annotations

import argparse
import json
import math
import re
import threading
import time
import urllib.parse
from http.server import BaseHTTPRequestHandler, HTTPServer

PLAYBACK_COUNT = 64   # AANNAME: de handleiding noemt pb64, maar geen bovengrens. De lijsten hebben 64 items.
CUE_MAX = 48          # HANDLEIDING: cues 1 t/m 48
LONG_PRESS_S = 0.5    # AANNAME: btn=1 tot btn=0 langer dan dit is een lange druk (release)

OK = '{"apicall":"succeeded"}'     # GEZIEN: het antwoord op go+
FOUT = '{"apicall":"failed"}'      # AANNAME: formaat van een fout


def _json(obj: dict) -> str:
    return json.dumps(obj, separators=(",", ":"))


def _getal(sleutel: str, waarde: float) -> str:
    """Getallen met twee decimalen, zoals de Quety (0.20, 0.60). GEZIEN bij speed en intensity."""
    return '{"%s":%.2f,"apicall":"succeeded"}' % (sleutel, waarde)


def _lijst_getallen(sleutel: str, waarden: list[float]) -> str:
    """AANNAME: formaat van de opvraag van alle waarden tegelijk."""
    lijst = ",".join(f"{w:.2f}" for w in waarden)
    return '{"%s":[%s],"apicall":"succeeded"}' % (sleutel, lijst)


def _nieuwe_waarde(huidig: float, tekst: str, soort: str) -> float | None:
    """Rekent de nieuwe waarde uit voor intensiteit ('int') of snelheid ('spd').

    int: '0.55' is absoluut (0 t/m 1), '++0.05' telt op, '-0.05' telt af (begrensd op 0 en 1).
    spd: '-0.20' is absoluut (HANDLEIDING: sp=-0.20), '++0.1' telt op (begrensd op -1 en 1).
    Een en-dash (–) wordt niet als min geaccepteerd. Geeft None bij een ongeldige waarde.
    """
    lo, hi = (0.0, 1.0) if soort == "int" else (-1.0, 1.0)
    try:
        if tekst.startswith("++"):
            waarde = huidig + float(tekst[2:])
        elif soort == "int" and tekst.startswith("-"):
            waarde = huidig + float(tekst)
        else:
            waarde = float(tekst)
            if not lo <= waarde <= hi:
                return None
            return waarde
    except ValueError:
        return None
    if not math.isfinite(waarde):
        return None
    return min(hi, max(lo, waarde))


class Quety:
    """De stand van één virtuele Quety. Alle toegang loopt via één lock."""

    def __init__(self, snapshot: bool = False) -> None:
        self.lock = threading.RLock()
        # Index = playbacknummer - 1. De handleiding toont de lijsten ook zo:
        # pbxx/all/ac=[1,1,0,...] en pbxx/all/cue=[1,-,4,...] beginnen bij playback 1.
        self.active = [0] * PLAYBACK_COUNT
        self.intensity = [0.5] * PLAYBACK_COUNT
        self.speed = [0.20] * PLAYBACK_COUNT
        self.cue: list = ["-"] * PLAYBACK_COUNT
        self.flash = [0] * PLAYBACK_COUNT
        self.blackout = 0
        self.button_down: dict[int, float] = {}
        self.laatste_antwoord = OK
        if snapshot:
            self.active[2] = 1   # pb3 aan
            self.cue[1] = 1      # cue 1 op pb2

    # ---- publieke ingangen -------------------------------------------------

    def handle(self, pad: str) -> tuple[int, str]:
        """Geeft (HTTP-statuscode, JSON-tekst) voor een pad zoals /ajax/pb10/go+."""
        with self.lock:
            code, tekst = self._verwerk(pad)
            self.laatste_antwoord = tekst
            return code, tekst

    def debug(self, pad: str) -> tuple[int, str]:
        """Hulpmiddelen voor jou, geen onderdeel van de echte Quety."""
        with self.lock:
            if pad == "/mock/state":
                return 200, _json({
                    "actief": [f"pb{i + 1:02d}" for i, v in enumerate(self.active) if v == 1],
                    "cue": {f"pb{i + 1:02d}": c for i, c in enumerate(self.cue) if c != "-"},
                    "intensiteit": {f"pb{i + 1:02d}": round(v, 2) for i, v in enumerate(self.intensity)},
                    "blackout": self.blackout,
                })
            if pad == "/mock/httpresponse":
                return 200, _json({"httpresponse": self.laatste_antwoord, "apicall": "succeeded"})
            return 404, FOUT

    # ---- routes ------------------------------------------------------------

    def _verwerk(self, pad: str) -> tuple[int, str]:
        if not pad.startswith("/ajax/"):
            return 404, FOUT
        cmd = pad[len("/ajax/"):].rstrip("/")

        if cmd == "hello":                                       # GEZIEN
            return 200, '{"hello":1,"apicall":"succeeded"}'
        if cmd == "status":                                      # GEZIEN (zonder apicall-sleutel)
            return 200, '{"label":"MyLPU-2","receiving":{"osc":0,"udp":0,"tcp":0}}'

        m = re.fullmatch(r"blackout(?:=([01]))?", cmd)           # GEZIEN: blackout=1 geeft de stand terug
        if m:
            if m.group(1) is not None:
                self.blackout = int(m.group(1))
            return 200, _json({"blackout": self.blackout, "apicall": "succeeded"})

        if cmd == "pbxx/ac":                                     # GEZIEN: lijst met 64 waarden
            return 200, _json({"ac": self.active, "apicall": "succeeded"})
        if cmd == "pbxx/cue":                                    # GEZIEN: lijst met "-" en cue-nummers
            return 200, _json({"cue": self.cue, "apicall": "succeeded"})
        if cmd == "pbxx/rel":                                    # HANDLEIDING: release all playbacks
            self.active = [0] * PLAYBACK_COUNT
            return 200, OK

        m = re.fullmatch(r"pbxx/(int|spd|sp)(?:=(.+))?", cmd)
        if m:
            return self._alle(m.group(1), m.group(2))

        m = re.fullmatch(r"pb(\d{2})/(.+)", cmd)                 # twee cijfers, zoals pb01
        if m:
            return self._playback(int(m.group(1)), m.group(2))

        return 404, FOUT

    def _alle(self, soort: str, waarde: str | None) -> tuple[int, str]:
        lijst = self.intensity if soort == "int" else self.speed
        naam = "intensity" if soort == "int" else "speed"
        if waarde is None:
            return 200, _lijst_getallen(naam, lijst)
        nieuw = [_nieuwe_waarde(w, waarde, soort) for w in lijst]
        if any(n is None for n in nieuw):
            return 400, FOUT
        lijst[:] = nieuw
        return 200, OK

    def _playback(self, n: int, cmd: str) -> tuple[int, str]:
        if not 1 <= n <= PLAYBACK_COUNT:
            return 404, FOUT                                     # AANNAME: onbekende playback
        i = n - 1
        if cmd == "ac":                                          # GEZIEN: 0 of 1
            return 200, _json({"ac": self.active[i], "apicall": "succeeded"})
        if cmd == "int":                                         # GEZIEN
            return 200, _getal("intensity", self.intensity[i])
        if cmd in ("spd", "sp"):                                 # GEZIEN (sleutel speed)
            return 200, _getal("speed", self.speed[i])
        if cmd == "go+":                                         # GEZIEN: alleen apicall
            self._go(i)
            return 200, OK
        if cmd == "go-":                                         # HANDLEIDING: go back
            self._go(i, terug=True)
            return 200, OK
        if cmd == "rel":                                         # HANDLEIDING: release playback
            self.active[i] = 0
            return 200, OK
        if cmd == "btn=1":                                       # HANDLEIDING: knop, eerst =1
            self.button_down[n] = time.monotonic()
            return 200, OK
        if cmd == "btn=0":                                       # HANDLEIDING: dan =0, de tijd bepaalt
            begin = self.button_down.pop(n, None)
            if begin is not None and time.monotonic() - begin >= LONG_PRESS_S:
                self.active[i] = 0
            else:
                self._go(i)
            return 200, OK
        m = re.fullmatch(r"fla=([01])", cmd)                     # HANDLEIDING
        if m:
            self.flash[i] = int(m.group(1))
            return 200, OK
        m = re.fullmatch(r"jmp=(\d+)", cmd)                      # HANDLEIDING: cue 1 t/m 48
        if m:
            cue_nr = int(m.group(1))
            if not 1 <= cue_nr <= CUE_MAX:
                return 400, FOUT
            self.cue[i] = cue_nr
            self.active[i] = 1                                   # AANNAME: jump start de playback
            return 200, OK
        m = re.fullmatch(r"int=(.+)", cmd)                       # HANDLEIDING
        if m:
            nieuw = _nieuwe_waarde(self.intensity[i], m.group(1), "int")
            if nieuw is None:
                return 400, FOUT
            self.intensity[i] = nieuw
            return 200, OK                                       # AANNAME: alleen apicall, zoals go+
        m = re.fullmatch(r"(?:spd|sp)=(.+)", cmd)                # HANDLEIDING
        if m:
            nieuw = _nieuwe_waarde(self.speed[i], m.group(1), "spd")
            if nieuw is None:
                return 400, FOUT
            self.speed[i] = nieuw
            return 200, OK
        return 404, FOUT

    def _go(self, i: int, terug: bool = False) -> None:
        """Go+ of go-. AANNAME: de eerste Go+ zet cue 1, daarna telt de cue op of af."""
        self.active[i] = 1
        huidig = self.cue[i]
        if huidig == "-":
            self.cue[i] = 1
        elif terug:
            self.cue[i] = max(1, huidig - 1)
        else:
            self.cue[i] = min(CUE_MAX, huidig + 1)


class _Verzoek(BaseHTTPRequestHandler):
    server_version = "CueyVirtueel/2.0"

    def do_GET(self) -> None:
        pad = urllib.parse.unquote(urllib.parse.urlsplit(self.path).path)
        if pad.startswith("/mock/"):
            code, tekst = self.server.quety.debug(pad)
        else:
            code, tekst = self.server.quety.handle(pad)
        body = tekst.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)
        print(f"{time.strftime('%H:%M:%S')}  {pad:<30} -> {code} {tekst}")

    def log_message(self, format: str, *args: object) -> None:
        pass  # de eigen regel hierboven is genoeg


class _Server(HTTPServer):
    """Eén verzoek tegelijk, zoals een klein apparaat. AANNAME."""

    def __init__(self, adres: tuple[str, int], quety: Quety) -> None:
        super().__init__(adres, _Verzoek)
        self.quety = quety


def main() -> None:
    parser = argparse.ArgumentParser(description="Virtuele Cuety (LPU-2) voor testen zonder hardware.")
    parser.add_argument("--port", type=int, default=80, help="poort (standaard 80, dat vraagt admin-rechten)")
    parser.add_argument("--host", default="0.0.0.0", help="adres waarop geluisterd wordt")
    parser.add_argument("--snapshot", action="store_true", help="begin met pb3 aan en cue 1 op pb2")
    args = parser.parse_args()

    server = _Server((args.host, args.port), Quety(snapshot=args.snapshot))
    print(f"Virtuele Cuety luistert op {args.host}:{args.port}. Stoppen met Ctrl+C.")
    print("Probeer: /ajax/hello  /ajax/pb01/go+  /ajax/pbxx/ac  /ajax/pbxx/rel  /mock/state\n")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nGestopt.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
