import time
import board
import digitalio
import simpleio
import adafruit_lsm6ds.lsm6ds33
import adafruit_apds9960.apds9960
from adafruit_hid.mouse import Mouse
from adafruit_ble.services.standard.hid import HIDService

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

mouse_min = -9

mouse_max = 9

step = (mouse_max - mouse_min) / 20.0

last_touch_val = False
toggle_value = False
def mouse_steps(axis):
    return round((axis - mouse_min) / step)


clock = 0

distance = 245

hid = HIDService()

mouse = Mouse(hid.devices)

while True:
    cur_state = sensor_btn.value
    if cur_state != last_touch_val:
        if cur_state:
            toggle_value = not toggle_value
            print(toggle_value)
    last_touch_val = cur_state
    