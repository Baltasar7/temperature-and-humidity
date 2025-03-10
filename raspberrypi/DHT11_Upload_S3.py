from machine import Pin
import utime as time
from dht import DHT11
import socket
import network
import sys
import json
import requests

""" Setup var and pin """
UPLOAD_SUCCESS = 0
UPLOAD_FAILED = 1
CONNECT_SUCCESS = 0
CONNECT_FAILED = 1
PRESIGNED_S3_URL_ENDPOINT = ""
HOME_WIFI_SSID = ""
HOME_WIFI_PW = ""
PHONE_WIFI_SSID = ""
PHONE_WIFI_PW = ""

wifi = network.WLAN(network.STA_IF)
wifi_led_pin = Pin('LED',Pin.OUT)
button_pin = Pin(15, Pin.IN, Pin.PULL_UP)
sensor_pin = Pin(16, Pin.OUT, Pin.PULL_UP)
sensor = DHT11(sensor_pin)


""" Connect Wi-fi function """
def connect_wifi(ssid, pw):
    wifi.active(False)
    time.sleep(1)
    wifi.active(True)
    wifi.connect(ssid, pw)

    wifi_led_pin.on()
    time.sleep(1)
    for i in range(15):
        if wifi.isconnected() == False:
            print(f"Waiting for Wi-fi({ssid}) connection...")
            time.sleep(1)
        else:
            for i in range(2):
                wifi_led_pin.off()
                time.sleep(0.5)
                wifi_led_pin.on()
                time.sleep(0.5)
            print(f"Connect Wi-fi({ssid}) done")
            print(wifi.ifconfig())
            wifi_led_pin.off()
            return CONNECT_SUCCESS
    print(f"Failed Wi-fi({ssid}) connection")
    wifi_led_pin.off()
    return CONNECT_FAILED  


""" Measure and sensor data upload function """
def measure_and_upload():
    """ Sensor measure """
    try:
        sensor.measure()
    except Exception as e:
        print(f"Sensor measure error: {e}")
        for i in range(10):
            wifi_led_pin.on()
            time.sleep(5)
            wifi_led_pin.off()
            time.sleep(1)
        return UPLOAD_FAILED
        #time.sleep(2)
        #sys.exit()
    temp = sensor.temperature()
    hum = sensor.humidity()
    print(f"temp:{temp}, hum:{hum}")
    
    """  Wifi Connection """ 
    if connect_wifi(HOME_WIFI_SSID, HOME_WIFI_PW) == CONNECT_FAILED:
        if connect_wifi(PHONE_WIFI_SSID, PHONE_WIFI_PW) == CONNECT_FAILED:
            return UPLOAD_FAILED

    """ Get Presigned S3 URL """
    try:
        response = requests.get(PRESIGNED_S3_URL_ENDPOINT)
        presigned_url = response.json().get('signed_url')
    except Exception as e:
        print(f"Failed to get presigned URL: {e}")
        for i in range(6):
            wifi_led_pin.on()
            time.sleep(10)
            wifi_led_pin.off()
            time.sleep(1)
        return UPLOAD_FAILED
        #time.sleep(2)
        #sys.exit()
    
    """ Prepare send data """
    current_time = time.localtime()
    formatted_time = "{:04}-{:02}-{:02} {:02}:{:02}:{:02}".format(
        current_time[0],
        current_time[1],
        current_time[2],
        current_time[3],
        current_time[4],
        current_time[5]
    )
    payload = {
        "temperature": round(temp, 1),
        "humidity": round(hum, 1),
        "timestamp": formatted_time
    }
    
    """ Uploaded to S3 """
    headers = {'Content-Type': 'application/json'}
    response = requests.put(presigned_url, data=json.dumps(payload), headers=headers)
    if response.status_code == 200:
        print("Data successfully uploaded to S3")
        for i in range(5):
            wifi_led_pin.on()
            time.sleep(0.1)
            wifi_led_pin.off()
            time.sleep(0.1)
    else:
        print(f"Failed to upload data: {response.status_code}")
        for i in range(4):
            wifi_led_pin.on()
            time.sleep(15)
            wifi_led_pin.off()
            time.sleep(1)
        return UPLOAD_FAILED
        #time.sleep(2)
        #sys.exit()
    return UPLOAD_SUCCESS


""" Sensor stabilize """
wifi_led_pin.off()
time.sleep(2)


""" Main loop """
while True:
    """ Cyclic measure and sensor data upload """
    for i in range(5):
        result = measure_and_upload()
        wifi.active(False)
        if result == UPLOAD_SUCCESS:
            break
    
    """ 30-minute intervals and manual upload """
    for i in range(60):
        if result == UPLOAD_SUCCESS:
            wifi_led_pin.on()
            time.sleep(0.2)
            wifi_led_pin.off()
            time.sleep(9.8)
        else:
            wifi_led_pin.on()
            time.sleep(1.0)
            wifi_led_pin.off()
            time.sleep(9.0)
            
        if button_pin.value() == 0:
            break
