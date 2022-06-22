import os
import gc
import time
import machine
import netswitch
import micropython
import uasyncio
import WIFI_CONFIG
from urllib import urequest
import ujson
from picographics import PicoGraphics, DISPLAY_PICO_DISPLAY_2
graphics = PicoGraphics(DISPLAY_PICO_DISPLAY_2)


uasyncio.get_event_loop().run_until_complete(netswitch.wlan_client(WIFI_CONFIG.SSID, WIFI_CONFIG.PSK))


#ENDPOINT = "https://en.wikiquote.org/w/api.php?format=json&action=expandtemplates&prop=wikitext&text={{QoD}}"

# Get a specific day
ENDPOINT = "https://en.wikiquote.org/w/api.php?format=json&action=expandtemplates&prop=wikitext&text={{{{Wikiquote:Quote%20of%20the%20day/{3}%20{1},%20{0}}}}}"

d = list(time.localtime())
d = [2022, 1, 1]
d.append(["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"][d[2]])


def parse_qotd(text):
    text = text.split("\n")
    return (
        text[6][2:].replace("[[","").replace("]]","").replace("<br>","\\ \n"),  # Quote
        text[8].split("|")[2][5:-4]                     # Author
    )


def get_json(url):
    j = ujson.load(urequest.urlopen(url))
    return j


url = ENDPOINT.format(*d)
print(url)
j = get_json(ENDPOINT.format(*d))

text = j['expandtemplates']['wikitext']

text, author = parse_qotd(text)

print(text)

graphics.set_font("bitmap8")
graphics.set_pen(0)
graphics.clear()
graphics.set_pen(0b00011100)
graphics.text("QoTD - {1} {3} {0:04d}".format(*d), 0, 0)
graphics.set_pen(255)
graphics.text(text, 0, 30, 320)
graphics.set_pen(0b00011100)
graphics.text(author, 0, 220)

graphics.update()