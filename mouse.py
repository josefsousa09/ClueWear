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
from calibration.calibration import Calibration
from helpers.csv_helpers import CsvHelpers
from ml.knn import KNN
from ulab import numpy as np



class Pointer:

    calibration = Calibration()
    knn = KNN()
    csv_helpers = CsvHelpers()

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

        self.hid = HIDService()

        self.device_info = DeviceInfoService(
            software_revision=adafruit_ble.__version__,
            manufacturer="Adafruit")

        self.advertisement = ProvideServicesAdvertisement(self.hid)
        self.advertisement.appearance = 961
        self.scan_response = Advertisement()
        self.scan_response.complete_name = "CP HID"

        self.ble = adafruit_ble.BLERadio()

    dataset = csv_helpers.create_dataset("movement_data.csv")
    X_train,y_train = csv_helpers.seperate_labels_and_data(dataset)

    def mouse_steps(self, axis):
        return round((axis - self.mouse_min) / self.step)

    def operate_mouse(self):
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
                    x,y,z = self.accel.acceleration
                    x_gyro,y_gyro,z_gyro = self.accel.gyro
                    prediction = self.knn.knn(self.X_train,self.y_train,np.concatenate((np.array([[x,y,z]]), np.array([[x_gyro,y_gyro,z_gyro]]))),3)  # type: ignore 
                    if prediction == 0:
                        horizontal_mov = simpleio.map_range(
                            self.mouse_steps(x), 1.0, 20.0, -15.0, 15.0)
                        vertical_mov = simpleio.map_range(
                                self.mouse_steps(y), 20.0, 1.0, -15.0, 15.0)
                            # scroll_dir = simpleio.map_range(
                            #     vertical_mov, -15.0, 15.0, 3.0, -3.0)
                        mouse.move(x=int(vertical_mov))
                        mouse.move(y=int(horizontal_mov))
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
                        print("CALIBRATE")
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
            self.ble.start_advertising(self.advertisement)
