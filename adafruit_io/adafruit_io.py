import time
import machine
from umqtt.simple import MQTTClient
import netswitch
import micropython
import uasyncio
import WIFI_CONFIG
import random


"""
Make a "WIFI_CONFIG.py" with the following:

SSID="ssid"
PSK="pass"

IO_USERNAME="aio username"
IO_KEY="aio_XXXXXX"
"""

uasyncio.get_event_loop().run_until_complete(netswitch.wlan_client(WIFI_CONFIG.SSID, WIFI_CONFIG.PSK))

UID = WIFI_CONFIG.IO_USERNAME + "-rp2040-" + ("{:02X}"*8).format(*machine.unique_id())
IP = netswitch.ip_address()

def handle_mqtt_message(topic, message):
    print("{}: {}".format(topic, message))
    

def get_topic(topic):
    return WIFI_CONFIG.IO_USERNAME + "/" + topic


mqtt = MQTTClient(UID, "io.adafruit.com", 8883,
                  user=WIFI_CONFIG.IO_USERNAME,
                  password=WIFI_CONFIG.IO_KEY,
                  ssl=True)

mqtt.connect()

mqtt.set_callback(handle_mqtt_message)
# Subscribe to API rate limiting and ban/error feeds
mqtt.subscribe(get_topic("throttle"))
mqtt.subscribe(get_topic("errors"))
mqtt.subscribe(get_topic("feeds/test"))

t_start = time.time()

while True:
    mqtt.check_msg()
    print(time.time() - t_start)
    if time.time() - t_start >= 30:
        mqtt.publish(get_topic("feeds/test"), "{}".format(random.randint(0, 100)))
        print("Publishing message.")
        t_start = time.time()
    time.sleep(2.0)
