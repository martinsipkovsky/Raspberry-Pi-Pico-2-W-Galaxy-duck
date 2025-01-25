import socketpool
import wifi
import microcontroller
import time

from adafruit_httpserver import Server, Request, Response, JSONResponse

import usb_hid
from adafruit_hid.mouse import Mouse
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keyboard_layout_win_cz import KeyboardLayout
from adafruit_hid.keycode import Keycode

AP_SSID = "Galaxy"
AP_PASSWORD = "GeForceRTX3080"

class HIDClient():
    def __init__(self):
        self.mouse = Mouse(usb_hid.devices)
        self.keyboard = Keyboard(usb_hid.devices)
        self.keyboardLayout = KeyboardLayout(self.keyboard)

    def mouseMove(self, x, y):
        self.mouse.move(x, y)
    
    def keyboardWrite(self, text):
        self.keyboardLayout.write(text)
    
    def keyboardKeycode(self, code):
        self.keyboard.press(code)
        time.sleep(0.1)
        self.keyboard.release(code)
    
    def winR(self):
        self.keyboard.press(227) # win key
        time.sleep(0.2)
        self.keyboard.press(21) # R key
        time.sleep(0.2)
        self.keyboard.release(227)
        self.keyboard.release(21)

hid = HIDClient()

print("Creating access point...")
wifi.radio.start_ap(ssid=AP_SSID, password=AP_PASSWORD)
print(f"Created access point {AP_SSID}")

pool = socketpool.SocketPool(wifi.radio)
server = Server(pool, "/static", debug=True)

@server.route("/")
def base(request: Request):
    """
    Serve a default static plain text message.
    """
    return Response(request, "Hello from the CircuitPython HTTP Server!")

@server.route("/cpu-information", append_slash=True)
def cpu_information_handler(request: Request):
    """
    Return the current CPU temperature, frequency, and voltage as JSON.
    """
    data = {
        "temperature": microcontroller.cpu.temperature,
        "frequency": microcontroller.cpu.frequency,
        "voltage": microcontroller.cpu.voltage,
    }
    return JSONResponse(request, data)

@server.route("/do")
def do(request: Request):
    for param in request.query_params.keys():
        if param.lower() == "keystrokes":
            hid.keyboardWrite(request.query_params["keystrokes"])
        elif param.lower() == "keycode":
            hid.keyboardKeycode(int(request.query_params["keycode"]))
        elif param.lower() == "winr":
            hid.winR()
        elif param.lower() == "sleep":
            t = float(int(request.query_params["sleep"])/1000)
            print(f"sleeping for {t}s.")
            time.sleep(t)

    
    return Response(request, "200")


# Použijte dostupnou IP adresu nebo výchozí IP pro AP
ap_ip = wifi.radio.ipv4_address_ap or "192.168.4.1"
print(f"Server running on http://{ap_ip}:80")
server.serve_forever(str(ap_ip), 80)


