import sys
import time
import netswitch
import tinyweb
import micropython
import uasyncio


uasyncio.get_event_loop().run_until_complete(netswitch.wlan_ap())

app = tinyweb.webserver()

UID = ("{:02X}"*8).format(*machine.unique_id())
print(UID)

ssid = None
psk = None

@app.route('/client')
async def index(request, response):
    await response.start_html()
    await response.send("OK")
    uasyncio.get_event_loop().create_task(netswitch.wlan_client(ssid, psk))
    

@app.route('/ap')
async def index(request, response):
    await response.start_html()
    await response.send("OK")
    uasyncio.get_event_loop().create_task(netswitch.wlan_ap())


@app.resource('/api/scan')
def api_scan(data):
    results = netswitch.network_if.scan()
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
    await response.send_file("js/{}".format(file), content_type="text/javascript")
    

@app.route('/')
async def index(request, response):
    await response.start_html()
    with open("html/index.html", "r") as f:
        body = f.read()
        await response.send(body.format(
        uid=UID,
        name=sys.implementation.name,
        machine=sys.implementation._machine,
        mode=netswitch.mode))


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
        uasyncio.get_event_loop().create_task(netswitch.wlan_client(ssid, psk))
    else:
        await response.send("No form post?")

app.run(host='0.0.0.0', port=80)


