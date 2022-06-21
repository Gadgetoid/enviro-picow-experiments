import sys
import rp2
import time
import network
import machine
import micropython
import uasyncio

UID = ("{:02X}"*8).format(*machine.unique_id())
WIFI_AP_TIMEOUT = 5
WIFI_CLIENT_TIMEOUT = 30

rp2.country("GB")
network_if = None
mode = None


def cleanup():
    global network_if, mode
    if network_if is not None:
        if network_if.isconnected():
            network_if.disconnect()
        #network_if.deinit()
        del network_if
        mode = None


def ip_address():
    if network_if is None:
        return '0.0.0.0'
    return network_if.ifconfig()[0]


async def wait():
    while not network_if.isconnected():
        print("...")
        await uasyncio.sleep_ms(1000)
    print(network_if.ifconfig())


async def wlan_client(ssid, psk):
    global network_if, mode
    await uasyncio.sleep_ms(1000)
    print("CLIENT: Connecting to {}".format(ssid))
    cleanup()
    network_if = network.WLAN(network.STA_IF)
    network_if.active(True)
    network_if.connect(ssid, psk)
    try:
        await uasyncio.wait_for(wait(), WIFI_CLIENT_TIMEOUT)
        mode = "client"
    except uasyncio.TimeoutError:
        cleanup()
        raise RuntimeError("WIFI AP Failed")

    
async def wlan_ap():
    print("AP: Connecting")
    global network_if, mode
    cleanup()
    network_if = network.WLAN(network.AP_IF)
    # network_if.config(pm = 0xa11140)
    # Doesn't seem to work?
    #network_if.config(
    #    essid="Envr{}".format(UID[0:4])
    #)
    """network_if.ifconfig((
        "10.10.0.1",
        "255.255.255.0",
        "10.10.0.1",
        "1.1.1.1"))"""
    network_if.active(True)
    try:
        await uasyncio.wait_for(wait(), WIFI_AP_TIMEOUT)
        mode = "ap"
    except uasyncio.TimeoutError:
        cleanup()
        raise RuntimeError("WIFI AP Failed")

