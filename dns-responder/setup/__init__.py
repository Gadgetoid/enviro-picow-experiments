import sys
import time
from network_manager import NetworkManager
import tinyweb
import catchalldns
import micropython
import uasyncio


# Thank you https://github.com/tripflex/captive-portal#known-endpoints
CAPTIVE_PORTAL_ENDPOINTS = [
    "/mobile/status.php",             # Android 8.0
    "/generate_204",                  # Android
    "/gen_204",                       # Android
    "/ncsi.txt",                      # Windows
    "/hotspot-detect.html",           # iOS/OSX
    "/hotspotdetect.html",            # iOS/OSX
    "/library/test/success.html",     # iOS
    "/success.txt",                   # OSX
    "/kindle-wifi/wifiredirect.html"  # Kindle
]

def status_handler(mode, status, ip):
    print(mode, status, ip)

network_manager = NetworkManager("XX", status_handler=status_handler)

uasyncio.get_event_loop().run_until_complete(network_manager.access_point())

my_ip = network_manager.ifaddress()

app = tinyweb.webserver()

dns = catchalldns.CatchallDNS(my_ip)

print(network_manager.UID)
print(my_ip)

ssid = None
psk = None

@app.route('/client')
async def index(request, response):
    await response.start_html()
    await response.send("OK")
    uasyncio.get_event_loop().create_task(network_manager.client(ssid, psk))
    

@app.route('/ap')
async def index(request, response):
    await response.start_html()
    await response.send("OK")
    uasyncio.get_event_loop().create_task(network_manager.access_point())


@app.resource('/api/scan')
def api_scan(data):
    results = network_manager._ap_if.scan()
    networks = {"networks": []}
    for result in results:
        name, mac, a, b, c, d = result
        mac = ("{:02X}:"*6).format(*mac)[:-1]
        name = name.decode("UTF-8")
        networks["networks"].append({
            "name": name,
            "mac": mac
        })
    return networks


@app.route('/js/<file>')
async def js(request, response, file):
    await response.send_file("setup/js/{}".format(file), content_type="text/javascript")
    

"""
for endpoint in CAPTIVE_PORTAL_ENDPOINTS:
    @app.route(endpoint)
    async def index(request, response):
        await response.redirect("http://pico.wireless")
"""

@app.catchall()
async def catchall(request, response):
    await response.redirect("http://pico.wireless")


@app.route('/', save_headers=["Host"])
async def index(request, response):
    print(request.headers)
    if request.headers.get(b"Host") != b"pico.wireless":
        print("{} -> http://pico.wireless".format(request.headers.get(b"Host")))
        await response.redirect("http://pico.wireless")
    else:
        await response.start_html()
        with open("setup/html/index.html", "r") as f:
            body = f.read()
            await response.send(body.format(
            uid=network_manager.UID,
            name=sys.implementation.name,
            machine=sys.implementation._machine,
            mode=network_manager.mode()))


@app.route('/connect', max_body_size=2048, save_headers=['Content-Length', 'Content-Type'], methods=['GET', 'POST'])
async def connect(request, response):
    global ssid, psk
    await response.start_html()
    if request.method == b"POST":
        await response.send("OK")
        form = await request.read_parse_form_data()
        print(form)
        ssid = form.get("networks")
        psk = form.get("psk")
        uasyncio.get_event_loop().create_task(network_manager.client(ssid, psk))
    else:
        await response.send("No form post?")

dns.run(host='0.0.0.0', port=53)
app.run(host='0.0.0.0', port=80)


