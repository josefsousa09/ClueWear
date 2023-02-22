import time
import board
import digitalio
import adafruit_lsm6ds.lsm6ds33
import adafruit_apds9960.apds9960
from adafruit_hid.mouse import Mouse
import adafruit_ble
from adafruit_ble.advertising import Advertisement
from adafruit_ble.advertising.standard import ProvideServicesAdvertisement
from adafruit_ble.services.standard.hid import HIDService
from adafruit_ble.services.standard.device_info import DeviceInfoService
from calibration.calibration import Calibration
from helpers.helpers import Helpers
from ml.knn import KNN
from ulab import numpy as np
from adafruit_ble.services import Service
from adafruit_ble.uuid import VendorUUID

class Pointer(Service):

    calibration = Calibration()
    knn = KNN()
    helpers = Helpers()

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

        self.is_calibrating = False

    hid = HIDService()

    device_info = DeviceInfoService(
        software_revision=adafruit_ble.__version__,
        manufacturer="Adafruit")

    advertisement = ProvideServicesAdvertisement(hid)
    advertisement.appearance = 961
    scan_response = Advertisement()
    scan_response.complete_name = "CP HID"

    ble = adafruit_ble.BLERadio()

    X_train, y_train = helpers.create_dataset("movement_data.csv")

    def operate_mouse(self):
        self.ble.start_advertising(self.advertisement)

        if not self.ble.connected:
            print("Ready to pair")

        else:
            print("paired")
            print(self.ble.connections)

        mouse = Mouse(self.hid.devices)

        while True:
            
            while not self.ble.connected:
                continue
            while self.ble.connected:
                sensor_btn_cur_state = self.sensor_btn.value
                calibrate_btn_cur_state = self.calibrate_btn.value
                if self.sensor_btn_toggle_value:
                    x, y, z = self.accel.acceleration
                    prediction = self.knn.knn(
                        self.X_train, self.y_train, np.array([[x, y, z]]), 3)
                    if prediction == 0:
                        horizontal_mov = round(z) * 2.5
                        vertical_mov = round(x) * 2.5
                        mouse.move(x=int(-horizontal_mov))
                        mouse.move(y=int(vertical_mov))
                    elif prediction == 1:
                        mouse.click(Mouse.LEFT_BUTTON)
                        time.sleep(0.5)
                        if (self.clock + 2) < time.monotonic():
                            self.clock = time.monotonic()
                    else:
                        mouse.click(Mouse.RIGHT_BUTTON)
                        if (self.clock + 2) < time.monotonic():
                            self.clock = time.monotonic()
                if sensor_btn_cur_state != self.sensor_btn_last_touch_val:
                    if sensor_btn_cur_state:
                        self.sensor_btn_toggle_value = not self.sensor_btn_toggle_value

                if calibrate_btn_cur_state != self.calibrate_btn_last_touch_val:
                    if not calibrate_btn_cur_state and not self.is_calibrating:
                        print("Calibrating Mode")
                        self.is_calibrating = True
                        self.calibrate_btn.deinit()
                        self.sensor_btn.deinit()
                        self.calibration.calibrate()

                        self.calibrate_btn = digitalio.DigitalInOut(
                            board.BUTTON_B)
                        self.calibrate_btn.direction = digitalio.Direction.INPUT
                        self.calibrate_btn.pull = digitalio.Pull.UP

                        self.sensor_btn = digitalio.DigitalInOut(
                            board.BUTTON_A)
                        self.sensor_btn.direction = digitalio.Direction.INPUT
                        self.sensor_btn.pull = digitalio.Pull.UP

                        self.is_calibrating = False

                self.calibrate_btn_last_touch_val = calibrate_btn_cur_state
                self.sensor_btn_last_touch_val = sensor_btn_cur_state
