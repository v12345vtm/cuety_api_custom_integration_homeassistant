from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import urllib.parse
import re
import threading

# Gebruik 80 zoals bij je oorspronkelijke script.
# Als poort 80 al bezet is, verander naar bijvoorbeeld 7000.
HOST = "0.0.0.0"
PORT = 80

# Virtuele Cuety-status
PLAYBACK_COUNT = 64
lock = threading.RLock()

active = [0] * PLAYBACK_COUNT
active[2] = 1  # Voorbeeld: playback 3 actief, zoals in je echte response

intensity = {pb: 0.5 for pb in range(1, PLAYBACK_COUNT + 1)}
speed = {pb: 0.20 for pb in range(1, PLAYBACK_COUNT + 1)}

cue = ["-"] * PLAYBACK_COUNT
cue[1] = 1

blackout = 0
last_http_response = {"apicall": "succeeded"}


class CuetyHttpServerMock(BaseHTTPRequestHandler):

    def send_json(self, response_data):
        response_json = json.dumps(response_data, separators=(",", ":"))
        body = response_json.encode("utf-8")

        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

        print(f"[HTTP Verzonden JSON] {response_json}")

    def do_GET(self):
        global blackout, last_http_response

        # Gebruik urlparse voor het pad, maar behoud '+' uit go+.
        raw_path = self.path.split("?", 1)[0]
        path = urllib.parse.unquote(raw_path)

        print(f"\n[HTTP GET Ontvangen] Pad: {path}")

        with lock:
            response_data = self.handle_request(path)

            # Dit endpoint toont de vorige response en mag die niet overschrijven.
            if path != "/mock/httpresponse":
                last_http_response = response_data.copy()

        self.send_json(response_data)

    def do_POST(self):
        # Sommige clients gebruiken POST; behandel die zoals GET.
        self.do_GET()

    def handle_request(self, path):
        global blackout

        # Laatste echte API-response als tekst beschikbaar maken voor HA.
        if path == "/mock/httpresponse":
            return {
                "httpresponse": json.dumps(last_http_response, separators=(",", ":")),
                "apicall": "succeeded"
            }

        # Cuety hello-response
        if "/ajax/hello" in path:
            return {"hello": 1, "apicall": "succeeded"}

        # Cuety status-response
        if "/ajax/status" in path:
            return {
                "label": "MyLPU-2",
                "receiving": {"osc": 0, "udp": 0, "tcp": 0}
            }

        # Feedback: 64 playback-statussen. Playback 10 is active[9].
        if "/ajax/ac" in path:
            return {"ac": active.copy(), "apicall": "succeeded"}

        # Cue-feedback
        if "/ajax/cue" in path:
            return {"cue": cue.copy(), "apicall": "succeeded"}

        # Blackout: /ajax/blackout, /ajax/blackout=1 of /ajax/blackout=0
        if "/ajax/blackout" in path:
            match = re.search(r"blackout(?:=|/)([01])", path)
            if match:
                blackout = int(match.group(1))
            return {"blackout": blackout, "apicall": "succeeded"}

        # Playback-endpoints, bijvoorbeeld /ajax/pb10/go+ of /ajax/pb10/int=0.59
        match = re.search(r"/ajax/pb(\d+)(?:/|$)", path)
        if match:
            pb = int(match.group(1))

            if not 1 <= pb <= PLAYBACK_COUNT:
                return {"apicall": "failed", "error": "playback_out_of_range"}

            command = path[match.end():].strip("/")

            if command.startswith("int"):
                value_match = re.search(r"int(?:=|/)([0-9]*\.?[0-9]+)", command)
                if value_match:
                    value = float(value_match.group(1))
                    if not 0.0 <= value <= 1.0:
                        return {"apicall": "failed", "error": "intensity_out_of_range"}
                    intensity[pb] = value

                return {"apicall": "succeeded", "intensity": intensity[pb]}

            if command.startswith("spd"):
                value_match = re.search(r"spd(?:=|/)([0-9]*\.?[0-9]+)", command)
                if value_match:
                    speed[pb] = float(value_match.group(1))
                return {"apicall": "succeeded", "speed": speed[pb]}

            if command == "go+":
                active[pb - 1] = 1
                return {"apicall": "succeeded"}

            if command in ("go-", "stop"):
                active[pb - 1] = 0
                return {"apicall": "succeeded"}

            if command.startswith("cue"):
                cue_match = re.search(r"cue(?:=|/)(\d+)", command)
                if cue_match:
                    cue[pb - 1] = int(cue_match.group(1))
                return {"cue": cue.copy(), "apicall": "succeeded"}

            return {
                "apicall": "succeeded",
                "active": active[pb - 1],
                "intensity": intensity[pb],
                "speed": speed[pb]
            }

        # Onbekend endpoint: behoud het gedrag van je oorspronkelijke mock.
        return {"apicall": "succeeded"}

    def log_message(self, format, *args):
        # Onderdruk de standaard HTTP-serverlogs.
        return


def run_server(port=PORT):
    server_address = (HOST, port)
    httpd = HTTPServer(server_address, CuetyHttpServerMock)

    print(f"Virtuele Cuety HTTP-Server gestart op {HOST}:{port}...")
    print("Klaar om Home Assistant verzoeken op te vangen.")
    print("Feedback: /ajax/ac | /ajax/status | /ajax/hello")
    print("Laatste response: /mock/httpresponse")
    print("Druk Ctrl+C om te stoppen.\n")

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServer wordt gestopt...")
    finally:
        httpd.server_close()
        print("Server gestopt.")


if __name__ == "__main__":
    run_server(port=PORT)
