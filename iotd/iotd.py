import os
import gc
import time
import netswitch
import uasyncio
import WIFI_CONFIG
from urllib import urequest
import ujson
from picographics import PicoGraphics, DISPLAY_PICO_DISPLAY_2
import jpegdec

graphics = PicoGraphics(DISPLAY_PICO_DISPLAY_2)


uasyncio.get_event_loop().run_until_complete(netswitch.wlan_client(WIFI_CONFIG.SSID, WIFI_CONFIG.PSK))

FILENAME_ENDPOINT = "https://en.wikipedia.org/w/api.php?action=query&format=json&formatversion=2&prop=images&titles=Template:POTD%20protected/{:04d}-{:02d}-{:02d}"
URL_ENDPOINT = "https://en.wikipedia.org/w/api.php?action=query&format=json&prop=imageinfo&iiprop=url&titles={}"

# We can't control the width/height of the image, but we can set a maximum height using wikimedia's thumbnailing functionality
IMAGE_HEIGHT = 320

d = time.localtime()
#d = (2022, 6, 12)

url = FILENAME_ENDPOINT.format(*d)

def get_json(url):
    socket = urequest.urlopen(url)
    j = ujson.load(socket)
    socket.close() # Essential to prevent memory leaks
    return j

def get_html(url):
    socket = urequest.urlopen(url)
    h = socket.read()
    socket.close() # Essential to prevent memory leaks
    return h


filename = get_json(url)["query"]["pages"][0]["images"][0]["title"]
print(gc.mem_free() / 1024)

print(filename)

url = URL_ENDPOINT.format(filename.replace(" ", "+"))
print("Fetching URL {}".format(url))

print(gc.mem_free() / 1024)
print("Request json...")
data = get_json(url)
image_url = next(iter(data["query"]["pages"].values()))["imageinfo"][0]["url"]
del data

# Mangle the image URL into a thumbnail URL for our desired maximum height
print(gc.mem_free() / 1024)
print("Process image URL...")
print(image_url)
fn = image_url.split("/")[-1]
image_url = image_url.replace("/commons/", "/commons/thumb/")
image_url += "/{}px-".format(IMAGE_HEIGHT)
image_url += fn
print(image_url)


print(gc.mem_free() / 1024)
print("Request image...")
socket = urequest.urlopen(image_url)

"""
If we try to read the whole image in one shot, it will fail with an OOM condition.
By chunking the input stream into a sensible size we can handle arbitrary sized files.
Tested up to 470k! (We'd probably run out of flash storage before this failed, maybe?)
"""
print(gc.mem_free() / 1024)
print("Write image")
data = bytearray(1024)
with open("iotd.jpg", "wb") as f:
    while True:
        if socket.readinto(data) == 0:
            break
        f.write(data)
socket.close()
del data


print(gc.mem_free() / 1024)
print("Check image")
ERR = "<!DOCTYPE html>"

"""
Fetching a new image will fail invariably until it's loaded in the browser
We need to figure out what headers Wikimedia requires in order to trigger the generation of a new thumbnail size.

Presumably this is an effort on their part to prevent an image resizing DDoS.
"""

f = open("iotd.jpg", "r")
if f.read(len(ERR)) == ERR:
    f.close()
    os.unlink("iotd.jpg")
    raise RuntimeError("Invalid image fetched! Try again.")
f.close()



print(gc.mem_free() / 1024)
print("Show image")
gc.collect()


jpeg = jpegdec.JPEG(graphics)

jpeg.open_file("iotd.jpg")
jpeg.decode()

graphics.update()
