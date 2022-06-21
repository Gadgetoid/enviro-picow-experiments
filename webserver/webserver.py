import os
import gc
import machine
import netswitch
import micropython
import uasyncio
import tinyweb
import WIFI_CONFIG

uasyncio.get_event_loop().run_until_complete(netswitch.wlan_client(WIFI_CONFIG.SSID, WIFI_CONFIG.PSK))

app = tinyweb.webserver()

UID = ("{:02X}"*8).format(*machine.unique_id())
IP = netswitch.ip_address()


@app.catchall()
def catchall(request, response):
    print(dir(request))
    path = request.path.decode("utf-8")
    if path == "/":
        path = "/index"
    file = "public{}.html".format(path)
    try:
        os.stat(file)
        data = open(file, "r").read()
        data = data.format(**globals(), mem_free=gc.mem_free())
        await response.start_html()
        await response.send(data)

    except OSError:
        response.code = 404
        await response.send_file("404.html", content_type="text/html")

        
app.run(host='0.0.0.0', port=80)