import time
import board
import digitalio
import adafruit_lsm6ds.lsm6ds33
from adafruit_hid.mouse import Mouse
import adafruit_ble
from adafruit_ble.advertising import Advertisement
from adafruit_ble.advertising.standard import ProvideServicesAdvertisement
from adafruit_ble.services.standard.hid import HIDService
from adafruit_ble.services.standard.device_info import DeviceInfoService
from calibration.calibration import Calibration
from helpers.helpers import Helpers
from ml.gmm import GMM
from display_manager import DisplayManager


class Pointer:

    def __init__(self):

        self.gmm = GMM()
        self.helpers = Helpers()
        self.display_manager = DisplayManager()

        self.calibration = Calibration(self.display_manager)

        self.i2c = board.I2C()

        self.sensor = adafruit_lsm6ds.lsm6ds33.LSM6DS33(self.i2c)

        self.sensor_btn = digitalio.DigitalInOut(board.BUTTON_A)
        self.sensor_btn.direction = digitalio.Direction.INPUT
        self.sensor_btn.pull = digitalio.Pull.UP
        self.sensor_btn_last_touch_val = False
        self.sensor_btn_toggle_value = False
        self.tracking_status = False

        self.calibrate_btn = digitalio.DigitalInOut(board.BUTTON_B)
        self.calibrate_btn.direction = digitalio.Direction.INPUT
        self.calibrate_btn.pull = digitalio.Pull.UP
        self.calibrate_btn_last_touch_val = False
        self.calibrate_btn_toggle_value = False

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

    def operate_mouse(self):
        self.gmm.train()
        self.display_manager.ready_to_pair_screen()
        self.ble.start_advertising(self.advertisement)
        mouse = Mouse(self.hid.devices)
        while True:
            if self.ble.connected:
                sensor_btn_cur_state = self.sensor_btn.value
                calibrate_btn_cur_state = self.calibrate_btn.value
                if self.sensor_btn_toggle_value:
                    x, y, z = self.sensor.acceleration
                    prediction = self.gmm.pdf_classifier([x,y,z])
                    if prediction == "general_mov":
                        horizontal_mov = round(x)
                        vertical_mov = round(y)
                        mouse.move(x=int(horizontal_mov))
                        mouse.move(y=int(vertical_mov))
                    elif prediction == "left_click":
                        mouse.click(Mouse.LEFT_BUTTON)
                        time.sleep(0.5)
                        if (self.clock + 2) < time.monotonic():
                            self.clock = time.monotonic()
                    elif prediction == "right_click":
                        mouse.click(Mouse.RIGHT_BUTTON)
                        if (self.clock + 2) < time.monotonic():
                            self.clock = time.monotonic()
                            time.sleep(0.5)
                if sensor_btn_cur_state != self.sensor_btn_last_touch_val:
                    if sensor_btn_cur_state:
                        self.sensor_btn_toggle_value = not self.sensor_btn_toggle_value
                        self.tracking_status = not self.tracking_status
                if calibrate_btn_cur_state != self.calibrate_btn_last_touch_val:
                    if not calibrate_btn_cur_state and not self.is_calibrating:
                        self.is_calibrating = True
                        self.calibrate_btn.deinit()
                        self.sensor_btn.deinit()
                        self.calibration.calibration()
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
                self.display_manager.tracking_screen(self.tracking_status)
            else:
                if not self.ble.advertising:
                    self.ble.start_advertising(self.advertisement)
                self.display_manager.ready_to_pair_screen()
