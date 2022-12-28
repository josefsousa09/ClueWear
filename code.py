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

prev_state = sensor_btn.value

mouse_min = -9

mouse_max = 9

step = (mouse_max - mouse_min) / 20.0


def mouse_steps(axis):
    return round((axis - mouse_min) / step)


clock = 0

distance = 245

hid = HIDService()

mouse = Mouse(hid.devices)

while True:
    cur_state = prev_state
    if cur_state != prev_state:
        print("sensor on")

        x, y, z = accel.acceleration

        horizontal_mov = simpleio.map_range(mouse_steps(x), 1.0, 20.0, -15.0, 15.0)
        vertical_mov = simpleio.map_range(mouse_steps(y), 20.0, 1.0, -15.0, 15.0)
        scroll_dir = simpleio.map_range(vertical_mov, -15.0, 15.0, 3.0, -3.0)

        if prox.proximity > distance:
            mouse.move(wheel=int(scroll_dir))
        else:
            mouse.move(x=int(horizontal_mov))
            mouse.move(y=int(vertical_mov))

        if not left_click.value:
            mouse.click(Mouse.LEFT_BUTTON)
            time.sleep(0.2)

            if (clock + 2) < time.monotonic():
                print("x", mouse_steps(x))
                print("y", mouse_steps(y))
                clock = time.monotonic()
    else:
        print("sensor off")
    prev_state = cur_state