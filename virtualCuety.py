from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import urllib.parse


class CuetyHttpServerMock(BaseHTTPRequestHandler):
    def do_GET(self):
        # Parse de URL en query parameters
        parsed_path = urllib.parse.urlparse(self.path)
        path = parsed_path.path

        print(f"\n[HTTP GET Ontvangen] Pad: {path}")

        # Standaard response structuur voor Cuety HTTP API
        response_data = {"apicall": "succeeded"}

        # Specifieke endpoints afhandelen op basis van de Cuety HTTP API
        if "/ajax/hello" in path:
            response_data = {"hello": "succeeded", "apicall": "succeeded"}

        elif "/ajax/pb" in path:
            # Bijv. /ajax/pb01/int of /ajax/pb01/int=0.55
            if "int" in path:
                if "=" in path:
                    val = path.split("=")[-1]
                    response_data = {"apicall": "succeeded", "intensity": float(val)}
                else:
                    response_data = {"apicall": "succeeded", "intensity": 0.5}
            elif "spd" in path:
                response_data = {"apicall": "succeeded", "speed": 0.0}
            elif "cue" in path:
                response_data = {"apicall": "succeeded", "cue": 1}
            elif "ac" in path:
                response_data = {"apicall": "succeeded", "active": 1}
            else:
                response_data = {"apicall": "succeeded"}

        elif "/ajax/blackout" in path:
            response_data = {"apicall": "succeeded", "blackout": 0}

        # Verstuur HTTP 200 OK met JSON body
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()

        response_json = json.dumps(response_data)
        self.wfile.write(response_json.encode('utf-8'))
        print(f"[HTTP Verzonden JSON] {response_json}")

    def do_POST(self):
        self.do_GET()

    # Onderdruk standaard logberichten van de server zelf in de console voor overzicht
    def log_message(self, format, *args):
        return


def run_server(port=7000):
    server_address = ('0.0.0.0', port)
    httpd = HTTPServer(server_address, CuetyHttpServerMock)
    print(f"Virtuele Cuety HTTP-Server gestart op poort {port}...")
    print("Klaar om Home Assistant verzoeken op te vangen...\n")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    print("Server gestopt.")


if __name__ == '__main__':
    run_server(port=80)
