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


uasyncio.get_event_loop().run_until_complete(netswitch.wlan_client(WIFI_CONFIG.SSID, WIFI_CONFIG.PSK))

FILENAME_ENDPOINT = "https://en.wikipedia.org/w/api.php?action=query&format=json&formatversion=2&prop=images&titles=Template:POTD%20protected/{:04d}-{:02d}-{:02d}"
URL_ENDPOINT = "https://en.wikipedia.org/w/api.php?action=query&format=json&prop=imageinfo&iiprop=url&titles={}"

d = time.localtime()
d = (2022, 6, 13)

url = FILENAME_ENDPOINT.format(*d)

def get_json(url):
    d = urequest.urlopen(url).read()
    print(d)
    j = ujson.loads(d)
    del d
    return j

def get_image(url):
    return urequest.urlopen(url).read()


filename = get_json(url)["query"]["pages"][0]["images"][0]["title"]
print(gc.mem_free() / 1024)

print(filename)

url = URL_ENDPOINT.format(filename.replace(" ", "+"))
print("Fetching URL {}".format(url))

data = get_json(url)
print(gc.mem_free() / 1024)

page = next(iter(data["query"]["pages"].values()))
image_info = page["imageinfo"][0]
del page
image_url = image_info["url"]
del image_info

print(image_url)
fn = image_url.split("/")[-1]
image_url = image_url.replace("/commons/", "/commons/thumb/")
image_url += "/240px-"
image_url += fn
print(image_url)

with open("iotd.jpg", "wb") as f:
    f.write(urequest.urlopen(image_url).read())

ERR = "<!DOCTYPE html>"

f = open("iotd.jpg", "r")
if f.read(len(ERR)) == ERR:
    f.close()
    os.unlink("iotd.jpg")
    raise RuntimeError("Invalid image fetched! Try again.")
f.close()
