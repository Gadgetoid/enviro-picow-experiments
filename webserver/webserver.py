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


# HTML files support string format syntax
# these values will be available.
# eg: <h1>UID is {UID}</h1>
CGI = {
    "UID": UID,
    "IP": IP
}

def get_mime_type(ext):
    if ext == "css":
        return "text/css"
    if ext == "js":
        return "text/javascript"
    return None


@app.catchall()
def catchall(request, response):
    print(dir(request), request.path)
    path = request.path.decode("utf-8")
    if path.endswith(".js") or path.endswith(".css"):
        # Handle .js and .css assets here
        file = "public{}".format(path)

        try:
            os.stat(file)  # Find requested file
            await response.send_file(file, content_type=get_mime_type(path.split(".")[-1]))
        except OSError:  # If file not found
            response.code = 404
            await response.send_file("404.html", content_type="text/html")

    elif len(path) > 1 and path.endswith("/"):
        await response.redirect(path[:-1])
    
    else:
        if path.endswith("/"):
            path += "index"
        file = "public{}.html".format(path)
        
        # CGI values for this request
        cgi = {
            "file": file,
            "mem_free": gc.mem_free(),
        }
        cgi.update(CGI)  # Add global CGI values

        try:
            os.stat(file)  # Find requested file
            data = open(file, "r").read()
            data = data.format(**cgi)
            await response.start_html()
            await response.send(data)

        except OSError:  # If file not found
            response.code = 404
            await response.send_file("404.html", content_type="text/html")

        
app.run(host='0.0.0.0', port=80)