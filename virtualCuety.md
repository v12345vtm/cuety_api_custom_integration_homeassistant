# Virtual Cuety LPU-2 Mock Server for Home Assistant

A lightweight Python-based HTTP mock server designed to emulate the Showtec Cuety LPU-2 lighting controller's HTTP API. This tool is ideal for testing Home Assistant custom integrations or third-party control scripts locally without needing physical hardware.

---

## 💡 How We Discovered the Solution

While attempting to integrate a Cuety device with Home Assistant, initial assumptions pointed toward a raw TCP/UDP socket server running on port 7000 (following the low-level ASCII documentation). 

However, by running a raw TCP capture and checking the PyCharm terminal logs, we discovered that Home Assistant's `aiohttp` client actually communicates using **standard HTTP requests** directed right at **port 7000**, utilizing the `/ajax/` endpoints (such as `GET /ajax/hello HTTP/1.1`) and expecting structured **JSON responses** like `{"apicall": "succeeded"}`.

Armed with this insight, we pivoted to a Python `BaseHTTPRequestHandler` server listening on port 7000, perfectly matching the integration's expectations.

---

## 🛠️ How the Python Script Works

The script (`virtual_cuety_http_port7000.py`) uses Python's built-in libraries (`http.server` and `json`) so **no external dependencies or `pip` installations are required**.

1. **HTTP Server Binding:** Binds an HTTP server to port `7000` on `0.0.0.0` (all local network interfaces).
2. **Request Routing (`do_GET`):** Parses incoming HTTP request paths:
   - `/ajax/hello`: Responds with a successful hello handshake payload.
   - `/ajax/pb...`: Emulates playback intensity, speed, cue, and active states.
   - `/ajax/blackout`: Mock controls for global blackout states.
3. **JSON Response Engine:** Automatically replies with HTTP status `200 OK` and a structured JSON body (`{"apicall": "succeeded", ...}`) which satisfies the Home Assistant custom integration parser.
4. **Console Logging:** Cleanly logs incoming requests and outgoing payloads for real-time debugging.

---

## 🚀 How to Use It

### Prerequisites
* Python 3.6 or higher installed on your computer.
* PyCharm (or any other Python IDE/editor).

### Step 1: Create the Script
Create a new file named `virtual_cuety.py` in your PyCharm project and paste the code below:

```python
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import urllib.parse

class CuetyHttpServerMock(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urllib.parse.urlparse(self.path)
        path = parsed_path.path
        
        print(f"\n[HTTP GET Received] Path: {path}")
        
        # Default Cuety API success response
        response_data = {"apicall": "succeeded"}
        
        # Handle specific Cuety HTTP API endpoints
        if "/ajax/hello" in path:
            response_data = {"hello": "succeeded", "apicall": "succeeded"}
            
        elif "/ajax/pb" in path:
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

        # Send HTTP 200 OK with JSON body
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        
        response_json = json.dumps(response_data)
        self.wfile.write(response_json.encode('utf-8'))
        print(f"[HTTP Sent JSON] {response_json}")

    def do_POST(self):
        self.do_GET()

    def log_message(self, format, *args):
        # Suppress default noisy server logs for cleaner output
        return

def run_server(port=7000):
    server_address = ('0.0.0.0', port)
    httpd = HTTPServer(server_address, CuetyHttpServerMock)
    print(f"Virtual Cuety HTTP Mock Server started on port {port}...")
    print("Waiting for Home Assistant requests...\n")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    print("Server stopped.")

if __name__ == '__main__':
    run_server(port=80)
```

### Step 2: Run the Mock Server
1. Open the script in **PyCharm**.
2. Run the file (`Shift + F10` or click the green Play button).
3. You should see the message: 
   `Virtual Cuety HTTP Mock Server started on port 7000...`

### Step 3: Configure Home Assistant
1. In Home Assistant, navigate to your Cuety integration setup.
2. Point the host IP to your PC's local IP address (or `127.0.0.1` if Home Assistant runs locally) on **port 7000**.
3. Watch your PyCharm console log incoming requests and successfully authenticated responses!

---

## 📜 License
This project is open-source and free to use for development and debugging purposes.
