import WIFI_CONFIG
import netswitch
import time
import uasyncio
import ujson
from urllib import urequest
from picographics import PicoGraphics, DISPLAY_INKY_PACK
import jpegdec
import random


"""
Grab a random image from PlaceKitten.com
save it to flash, and display it on Inky Pack.
"""


graphics = PicoGraphics(DISPLAY_INKY_PACK)

WIDTH, HEIGHT = graphics.get_bounds()
FILENAME = "placekitten.jpg"
ENDPOINT = "http://placekitten.com/{0}/{1}"


def status_handler(mode, status, ip):
    graphics.set_update_speed(3)
    graphics.set_pen(1)
    graphics.clear()
    graphics.set_pen(0)
    graphics.text("Network: {}".format(WIFI_CONFIG.SSID), 10, 10, scale=2)
    status_text = "Connecting..."
    if status is not None:
        if status:
            status_text = "Connection successful!"
        else:
            status_text = "Connection failed!"

    graphics.text(status_text, 10, 30, scale=2)
    graphics.text("IP: {}".format(ip), 10, 60, scale=2)
    graphics.update()


graphics.set_font("bitmap8")
graphics.set_update_speed(1)

network_manager = netswitch.NetSwitch("GB", status_handler=status_handler)
uasyncio.get_event_loop().run_until_complete(network_manager.client(WIFI_CONFIG.SSID, WIFI_CONFIG.PSK))


url = ENDPOINT.format(WIDTH, HEIGHT + random.randint(0, 10))
print("Requesting URL: {}".format(url))
socket = urequest.urlopen(url)

# Load the image data into RAM (if you have enough!)
data = bytearray(1024 * 10)
socket.readinto(data)
socket.close()

"""
# Stream the image data from the socket onto disk in 1024 byte chunks
data = bytearray(1024)
with open(FILENAME, "wb") as f:
    while True:
        if socket.readinto(data) == 0:
            break
        f.write(data)
socket.close()
"""

jpeg = jpegdec.JPEG(graphics)
jpeg.open_RAM(data)
jpeg.decode(0, 0)

graphics.set_pen(1)
graphics.rectangle(0, HEIGHT - 14, WIDTH, 14)

graphics.set_pen(0)
graphics.text(url, 5, HEIGHT - 9, scale=1)

graphics.set_update_speed(1)
graphics.update()