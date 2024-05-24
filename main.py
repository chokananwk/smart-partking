from microbit import *
import utime
import network
import urequests

# กำหนดพินสำหรับเซ็นเซอร์และไฟ LED ของแต่ละล็อค
lock_pins = {
    'A1': {'trigger': pin1, 'echo': pin2, 'green_led': pin0, 'red_led': pin8},
    'A2': {'trigger': pin5, 'echo': pin11, 'green_led': pin13, 'red_led': pin14},
    'A3': {'trigger': pin15, 'echo': pin16, 'green_led': pin9, 'red_led': pin10}
}

# WiFi configuration
SSID = 'your_wifi_ssid'
PASSWORD = 'your_wifi_password'
IFTTT_EVENT_NAME = 'parking_status'
IFTTT_KEY = 'https://maker.ifttt.com/trigger/parking_status/with/key/bLSpsURgmZHM1sxcf2yPlN'
IFTTT_URL = 'https://maker.ifttt.com/trigger/{}/with/key/{}'.format(IFTTT_EVENT_NAME, IFTTT_KEY)

def connect_wifi(ssid, password):
    sta_if = network.WLAN(network.STA_IF)
    if not sta_if.isconnected():
        print('connecting to network...')
        sta_if.active(True)
        sta_if.connect(ssid, password)
        while not sta_if.isconnected():
            pass
    print('network config:', sta_if.ifconfig())

def get_distance(trigger_pin, echo_pin):
    trigger_pin.write_digital(0)
    utime.sleep_us(2)
    trigger_pin.write_digital(1)
    utime.sleep_us(10)
    trigger_pin.write_digital(0)
    
    while echo_pin.read_digital() == 0:
        pulse_start = utime.ticks_us()
    
    while echo_pin.read_digital() == 1:
        pulse_end = utime.ticks_us()
    
    pulse_duration = utime.ticks_diff(pulse_end, pulse_start)
    distance = (pulse_duration * 0.0343) / 2
    return distance

def update_parking_status():
    status = {}
    for lock, pins in lock_pins.items():
        distance = get_distance(pins['trigger'], pins['echo'])
        if distance < 10: # ถ้าระยะน้อยกว่า 10 ซม. ถือว่ามีรถจอด
            pins['green_led'].write_digital(0)
            pins['red_led'].write_digital(1)
            status[lock] = "ไม่ว่าง"
        else:
            pins['green_led'].write_digital(1)
            pins['red_led'].write_digital(0)
            status[lock] = "ว่าง"
    return status

def send_status_to_ifttt(status):
    payload = {'value1': '\n'.join([f'ล็อค {lock}: {stat}' for lock, stat in status.items()])}
    try:
        response = urequests.post(IFTTT_URL, json=payload)
        response.close()
    except:
        display.scroll("Failed to send")

connect_wifi(SSID, PASSWORD)

last_status = {}

while True:
    current_status = update_parking_status()
    if current_status != last_status:
        send_status_to_ifttt(current_status)
        last_status = current_status
    utime.sleep(5)  # ตรวจสอบทุกๆ 5 วินาที
