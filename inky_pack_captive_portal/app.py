
import gc
import sys
import time
import qrcode
import machine
import logging
import tinyweb
import uasyncio
import catchalldns

from network_manager import NetworkManager
from picographics import PicoGraphics, DISPLAY_INKY_PACK

gc.collect()


DOMAIN = "pico.wireless"
COUNTRY_CODE = "GB"
logging.basicConfig(level=logging.INFO)


def measure_qr_code(size, code):
    w, h = code.get_size()
    module_size = int(size / w)
    return module_size * w, module_size


def draw_qr_code(ox, oy, size, code):
    size, module_size = measure_qr_code(size, code)
    graphics.set_pen(15)
    graphics.rectangle(ox, oy, size, size)
    graphics.set_pen(0)
    for x in range(size):
        for y in range(size):
            if code.get_module(x, y):
                graphics.rectangle(ox + x * module_size, oy + y * module_size, module_size, module_size)


def on_network_status_change(mode, status, ip):
    global blink, ssid, psk, my_ip
    log.info("{} {}. {}".format(mode, "Connecting" if status is None else "Connected" if status else "Failed", ip))
    led.value(blink)
    blink = not blink
    if status:
        ssid = network_manager.config("ssid")
        psk = network_manager.config("password")
        log.info("Network: {}, PSK: {}".format(ssid, psk))
        qr.set_text("WIFI:S:{ssid};T:WPA;P:{psk};H:false;;".format(ssid=ssid, psk=psk))
        graphics.set_pen(15)
        graphics.clear()
        wh, ms = measure_qr_code(128, qr)
        draw_qr_code(int((296 / 2) - (wh / 2)), int((128 / 2) - (wh / 2)), 128, qr)
        graphics.update()


def on_network_fail(mode, msg):
    print(msg)


# Helper to send some formatted HTML from the filesystem
async def send_html(response, file):
    await response.start_html()
    with open("html/{}.html".format(file), "r") as f:
        body = f.read()
        await response.send(body.format(
            uid=network_manager.UID,
            name=sys.implementation.name,
            machine=sys.implementation._machine,
            mode=network_manager.mode(),
            ssid=ssid,
            psk=psk))


network_manager = NetworkManager(COUNTRY_CODE, status_handler=on_network_status_change, error_handler=on_network_fail)

blink = False
ssid = None
psk = None
log = logging.getLogger('APP')

led = machine.Pin("LED", machine.Pin.OUT, value=0)
qr = qrcode.QRCode()
graphics = PicoGraphics(DISPLAY_INKY_PACK)

# Start access point
uasyncio.get_event_loop().run_until_complete(network_manager.access_point())
my_ip = network_manager.ifaddress()

web = tinyweb.webserver()
dns = catchalldns.CatchallDNS(my_ip)


async def catchall_redirect(request, response):
    log.info("301: {} -> http://{}".format(request.headers.get(b"Host"), DOMAIN))
    await response.redirect("http://" + DOMAIN)


# Server the main page at http://pico.wireless
@web.route('/', save_headers=["Host"])
async def index(request, response):
    if request.headers.get(b"Host").decode("ascii") == DOMAIN:
        await send_html(response, "index")
    else:
        await catchall_redirect(request, response)


# A catchall 301 redirect handles the various endpoints that OSes use to check connectivity
@web.catchall()
async def catchall(request, response):
    await catchall_redirect(request, response)


# Start DNS server
dns.run(host='0.0.0.0', port=53)

# Start web server (blocking!)
web.run(host='0.0.0.0', port=80)

# Unreachable!
