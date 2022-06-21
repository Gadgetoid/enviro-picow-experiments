import os
import gc
import machine
import netswitch
import micropython
import uasyncio
import WIFI_CONFIG
from urllib import urequest
import ujson

uasyncio.get_event_loop().run_until_complete(netswitch.wlan_client(WIFI_CONFIG.SSID, WIFI_CONFIG.PSK))


#resource = urequest.urlopen("https://www.mediawiki.org/w/api.php?action=query&list=random&rnnamespace=0&rnlimit=1&format=json").read()
#resource = urequest.urlopen("https://en.wikipedia.org/api/rest_v1/page/random/summary").read()
resource = urequest.urlopen("https://en.wikipedia.org/w/api.php?format=json&action=query&grnnamespace=0&generator=random&prop=extracts&explaintext=").read()


j = ujson.loads(resource)

page = list(j['query']['pages'].keys())[0]

print(j['query']['pages'][page]['title'])
print(j['query']['pages'][page]['extract'][0:100])