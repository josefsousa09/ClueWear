import time
import board
import digitalio
import simpleio
import adafruit_lsm6ds.lsm6ds33
import adafruit_apds9960.apds9960
from adafruit_hid.mouse import Mouse
import adafruit_ble
from adafruit_ble.advertising import Advertisement
from adafruit_ble.advertising.standard import ProvideServicesAdvertisement
from adafruit_ble.services.standard.hid import HIDService
from adafruit_ble.services.standard.device_info import DeviceInfoService
# from adafruit_clue import clue

i2c = board.I2C()

accel = adafruit_lsm6ds.lsm6ds33.LSM6DS33(i2c)

prox = adafruit_apds9960.apds9960.APDS9960(i2c)

prox.enable_proximity = True

left_click = digitalio.DigitalInOut(board.BUTTON_A)
left_click.direction = digitalio.Direction.INPUT
left_click.pull = digitalio.Pull.UP

sensor_btn = digitalio.DigitalInOut(board.BUTTON_B)
sensor_btn.direction = digitalio.Direction.INPUT
sensor_btn.pull = digitalio.Pull.UP
last_touch_val = False
toggle_value = False

mouse_min = -9

mouse_max = 9

step = (mouse_max - mouse_min) / 20.0

def mouse_steps(axis):
    return round((axis - mouse_min) / step)

clock = 0

distance = 245

hid = HIDService()

device_info = DeviceInfoService(
    software_revision=adafruit_ble.__version__,
    manufacturer="Adafruit")

advertisement = ProvideServicesAdvertisement(hid)

advertisement.appearance = 961

scan_response = Advertisement()

scan_response.complete_name = "CP HID"

ble = adafruit_ble.BLERadio()

if not ble.connected:
    print("Ready to connect")

else:
    print("already connected")
    print(ble.connections)

mouse = Mouse(hid.devices)

while True:
    while not ble.connected:
        pass
    while ble.connected:
        cur_state = sensor_btn.value
        if toggle_value:
            x,y,z = accel.acceleration
            # swap horizontal ranges with vertical's when using in bracelet
            
            horizontal_mov = simpleio.map_range(mouse_steps(x), 1.0,20.0,-15.0, 15.0)
            vertical_mov = simpleio.map_range(mouse_steps(y), 20.0,1.0,-15.0,15.0)
            scroll_dir = simpleio.map_range(vertical_mov, -15.0,15.0,3.0,-3.0)

            if prox.proximity > distance:
                mouse.move(wheel=int(scroll_dir))
            else:
                mouse.move(x=int(horizontal_mov))
                mouse.move(y=int(vertical_mov))

            if prox.proximity > 150:
                mouse.click(Mouse.LEFT_BUTTON)
                time.sleep(0.2)
            
                if (clock + 2) < time.monotonic():
                    print("x", mouse_steps(x))
                    print("y", mouse_steps(y))
                    clock = time.monotonic()
                    
        if cur_state != last_touch_val:
            if cur_state:
                toggle_value = not toggle_value
        last_touch_val = cur_state
    ble.start_advertising(advertisement)
