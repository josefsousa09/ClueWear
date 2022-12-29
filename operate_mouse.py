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
from calibration import Calibration


class ClueWear:
    calibration = Calibration()

    def __init__(self):

        self.i2c = board.I2C()

        self.accel = adafruit_lsm6ds.lsm6ds33.LSM6DS33(self.i2c)

        self.prox = adafruit_apds9960.apds9960.APDS9960(self.i2c)

        self.prox.enable_proximity = True
        self.calibrate_btn = digitalio.DigitalInOut(board.BUTTON_B)
        
        self.calibrate_btn.direction = digitalio.Direction.INPUT
        self.calibrate_btn.pull = digitalio.Pull.UP
        self.calibrate_btn_last_touch_val = False
        self.calibrate_btn_toggle_value = False

        self.sensor_btn = digitalio.DigitalInOut(board.BUTTON_A)
        self.sensor_btn.direction = digitalio.Direction.INPUT
        self.sensor_btn.pull = digitalio.Pull.UP
        self.sensor_btn_last_touch_val = False
        self.sensor_btn_toggle_value = False

        self.mouse_min = -9
        self.mouse_max = 9
        self.step = (self.mouse_max - self.mouse_min) / 20.0

        self.clock = 0

        self.distance = 245

        self.hid = HIDService()

        self.device_info = DeviceInfoService(
            software_revision=adafruit_ble.__version__,
            manufacturer="Adafruit")

        self.advertisement = ProvideServicesAdvertisement(self.hid)
        self.advertisement.appearance = 961
        self.scan_response = Advertisement()
        self.scan_response.complete_name = "CP HID"

        self.ble = adafruit_ble.BLERadio()

    def mouse_steps(self, axis):
        return round((axis - self.mouse_min) / self.step)

    def operate_mouse(self):
        if not self.ble.connected:
            print("Ready to connect")

        else:
            print("already connected")
            print(self.ble.connections)

        mouse = Mouse(self.hid.devices)

        while True:
            while not self.ble.connected:
                pass
            while self.ble.connected:
                sensor_btn_cur_state = self.sensor_btn.value
                calibrate_btn_cur_state = self.calibrate_btn.value

                if self.sensor_btn_toggle_value:
                    x, y, z = self.accel.acceleration
                    # swap horizontal ranges with vertical's when using in bracelet
                    horizontal_mov = simpleio.map_range(
                        self.mouse_steps(x), 1.0, 20.0, -15.0, 15.0)
                    vertical_mov = simpleio.map_range(
                        self.mouse_steps(y), 20.0, 1.0, -15.0, 15.0)
                    scroll_dir = simpleio.map_range(
                        vertical_mov, -15.0, 15.0, 3.0, -3.0)

                    if self.prox.proximity > self.distance:
                        mouse.move(wheel=int(scroll_dir))
                    else:
                        mouse.move(x=int(horizontal_mov))
                        mouse.move(y=int(vertical_mov))

                    if self.prox.proximity > 150:
                        mouse.click(Mouse.LEFT_BUTTON)
                        time.sleep(0.2)

                        if (self.clock + 2) < time.monotonic():
                            self.clock = time.monotonic()

                if sensor_btn_cur_state != self.sensor_btn_last_touch_val:
                    if sensor_btn_cur_state:
                        self.sensor_btn_toggle_value = not self.sensor_btn_toggle_value

                if calibrate_btn_cur_state != self.calibrate_btn_last_touch_val:
                    if not calibrate_btn_cur_state:
                        self.calibration.calibrate()
                    else:
                        pass

                self.calibrate_btn_last_touch_val = calibrate_btn_cur_state
                self.sensor_btn_last_touch_val = sensor_btn_cur_state
            self.ble.start_advertising(self.advertisement)
