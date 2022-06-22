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


ENDPOINT = "https://en.wikiquote.org/w/api.php?format=json&action=expandtemplates&prop=wikitext&text={{QoD}}"

def parse_qotd(text):
    text = text.split("\n")
    return (
        text[6][2:].replace("[[","").replace("]]",""),  # Quote
        text[8].split("|")[2][5:-4]                     # Author
    )


def get_json(url):
    j = ujson.load(urequest.urlopen(url))
    return j


j = get_json(ENDPOINT)

text = j['expandtemplates']['wikitext']

text, author = parse_qotd(text)

print(text)

graphics.set_font("bitmap8")
graphics.set_pen(0)
graphics.clear()
graphics.set_pen(0b00011100)
graphics.text("Quote of the day - {:04d}-{:02d}-{:02d}".format(*time.localtime()), 0, 0)
graphics.set_pen(255)
graphics.text(text, 0, 30, 320)
graphics.set_pen(0b00011100)
graphics.text(author, 0, 220)

graphics.update()