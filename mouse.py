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
import gmm
from display_manager import DisplayManager
from settings import Settings
from helpers.helpers import Helpers


class Pointer:
    helpers = Helpers()
    def __init__(self):

        self.display_manager = DisplayManager()
        self.gmm = gmm.GMM()
        self.i2c = board.I2C()

        self.sensor = adafruit_lsm6ds.lsm6ds33.LSM6DS33(self.i2c)

        self.sensor_btn = digitalio.DigitalInOut(board.BUTTON_A)
        self.sensor_btn.direction = digitalio.Direction.INPUT
        self.sensor_btn.pull = digitalio.Pull.UP
        self.sensor_btn_last_touch_val = True
        self.sensor_btn_toggle_value = True

        self.calibrate_btn = digitalio.DigitalInOut(board.BUTTON_B)
        self.calibrate_btn.direction = digitalio.Direction.INPUT
        self.calibrate_btn.pull = digitalio.Pull.UP
        self.calibrate_btn_last_touch_val = True

        self.config_settings = self.helpers.read_config_file()

        self.clock = 0

    hid = HIDService()

    device_info = DeviceInfoService(
        software_revision=adafruit_ble.__version__,
        manufacturer="Adafruit")

    advertisement = ProvideServicesAdvertisement(hid)
    advertisement.appearance = 961
    scan_response = Advertisement()
    scan_response.complete_name = "CP HID"

    ble = adafruit_ble.BLERadio()

    def sensitivity_conversion(self,value):
        if value == 1:
            return 0.25
        elif value == 2:
            return 0.5
        elif value == 3:
            return 1
        elif value == 4:
            return 1.25
        elif value == 5:
            return 1.5

    def operate_mouse(self):
        dataset_empty = self.helpers.dataset_empty("gesture_training_dataset.csv")
        if not dataset_empty:
            print("Train")
            self.gmm.train(self.helpers.organise_data("gesture_training_dataset.csv"))
        # self.display_manager.ready_to_pair_screen()
        self.ble.start_advertising(self.advertisement)
        mouse = Mouse(self.hid.devices)
        vertical_sensitivity = self.sensitivity_conversion(self.config_settings['VERT.SENSITIVITY'])
        horizontal_sensitivity = self.sensitivity_conversion(self.config_settings['HORIZ.SENSITIVITY'])
        vertical_inverted = self.config_settings['VERT.INVERTED']
        horizontal_inverted = self.config_settings['HORIZ.INVERTED']
        while True:
            if self.ble.connected:
                sensor_btn_cur_state = self.sensor_btn.value
                calibrate_btn_cur_state = self.calibrate_btn.value
                if self.sensor_btn_toggle_value:
                    x, y, z = self.sensor.acceleration
                    prediction, m = self.gmm.pdf_classifier([x,y,z], 0.01) if not dataset_empty else "?", None
                    if prediction[0] == "?":
                        horizontal_mov = round(-x) * horizontal_sensitivity if horizontal_inverted == True else round(x) * horizontal_sensitivity 
                        vertical_mov = round(-y) * vertical_inverted if vertical_inverted == True else round(y) * vertical_sensitivity 
                        mouse.move(x=int(horizontal_mov))
                        mouse.move(y=int(vertical_mov))
                    elif prediction[0] == "left_click":
                        mouse.click(Mouse.LEFT_BUTTON)
                        time.sleep(0.5)
                        if (self.clock + 2) < time.monotonic():
                            self.clock = time.monotonic()
                    elif prediction[0] == "right_click":
                        mouse.click(Mouse.RIGHT_BUTTON)
                        if (self.clock + 2) < time.monotonic():
                            self.clock = time.monotonic()
                            time.sleep(0.5)
                if sensor_btn_cur_state != self.sensor_btn_last_touch_val and calibrate_btn_cur_state != self.calibrate_btn_last_touch_val:
                    time.sleep(0.5)
                    if not sensor_btn_cur_state or not calibrate_btn_cur_state:
                        self.calibrate_btn.deinit()
                        self.sensor_btn.deinit()
                        settings = Settings(self.display_manager)
                        settings.settings_menu()
                        del settings
                        self.config_settings = self.helpers.read_config_file()
                        vertical_sensitivity = self.sensitivity_conversion(self.config_settings['VERT.SENSITIVITY'])
                        horizontal_sensitivity = self.sensitivity_conversion(self.config_settings['HORIZ.SENSITIVITY'])
                        vertical_inverted = self.config_settings['VERT.INVERTED']
                        horizontal_inverted = self.config_settings['HORIZ.INVERTED']
                        self.calibrate_btn = digitalio.DigitalInOut(
                            board.BUTTON_B)
                        self.calibrate_btn.direction = digitalio.Direction.INPUT
                        self.calibrate_btn.pull = digitalio.Pull.UP
                        self.sensor_btn = digitalio.DigitalInOut(
                            board.BUTTON_A)
                        self.sensor_btn.direction = digitalio.Direction.INPUT
                        self.sensor_btn.pull = digitalio.Pull.UP
                        time.sleep(1)
                elif sensor_btn_cur_state != self.sensor_btn_last_touch_val and calibrate_btn_cur_state == self.calibrate_btn_last_touch_val:
                    if not sensor_btn_cur_state:
                        self.sensor_btn_toggle_value = not self.sensor_btn_toggle_value
                elif calibrate_btn_cur_state != self.calibrate_btn_last_touch_val and sensor_btn_cur_state == self.sensor_btn_last_touch_val:
                    if not calibrate_btn_cur_state:
                        self.calibrate_btn.deinit()
                        self.sensor_btn.deinit()
                        calibration = Calibration(self.display_manager,self.gmm)
                        calibration.calibration()
                        del calibration
                        dataset_empty = self.helpers.dataset_empty("gesture_training_dataset.csv")
                        self.calibrate_btn = digitalio.DigitalInOut(
                            board.BUTTON_B)
                        self.calibrate_btn.direction = digitalio.Direction.INPUT
                        self.calibrate_btn.pull = digitalio.Pull.UP
                        self.sensor_btn = digitalio.DigitalInOut(
                            board.BUTTON_A)
                        self.sensor_btn.direction = digitalio.Direction.INPUT
                        self.sensor_btn.pull = digitalio.Pull.UP

                self.calibrate_btn_last_touch_val = calibrate_btn_cur_state
                self.sensor_btn_last_touch_val = sensor_btn_cur_state
                # self.display_manager.tracking_screen(self.sensor_btn_toggle_value)
            else:
                if not self.ble.advertising:
                    self.ble.start_advertising(self.advertisement)
                # self.display_manager.ready_to_pair_screen()
