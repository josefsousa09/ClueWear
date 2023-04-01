import time
import board
import digitalio
import simpleio
import adafruit_lsm6ds.lsm6ds33
from adafruit_hid.mouse import Mouse
import adafruit_ble
from adafruit_ble.advertising import Advertisement
from adafruit_ble.advertising.standard import ProvideServicesAdvertisement
from adafruit_ble.services.standard.hid import HIDService
from adafruit_ble.services.standard.device_info import DeviceInfoService
from calibration import Calibration
import gesture_recognition_gmm
from display_manager import DisplayManager
from settings import Settings
from helpers.helpers import Helpers


class Pointer:
    helpers = Helpers()
    def __init__(self):

        self.display_manager = DisplayManager()
        self.gmm = gesture_recognition_gmm.GMM()
        self.i2c = board.I2C()

        self.buzzer = board.P0

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

        self.on_melody = [
        (440, 0.25),
        (494, 0.25),
        (523, 0.25),
        (587, 0.25),
        (659, 0.25),
        (698, 0.25),
        (784, 0.25),
        (880, 0.25),
        ]

        self.connection_lost_melody = [
                        (880, 0.1),
                        (784, 0.1),
                        (659, 0.1),
                        (587, 0.1),
                        (523, 0.1),
                        (494, 0.1),
                        (440, 0.1),
                        (392, 0.1),
                        (330, 0.1),
                        (294, 0.1),
                        (262, 0.1),
                        (220, 0.1),
                        ]


        self.config_settings = self.helpers.read_config_file()

        self.clock = 0

    hid = HIDService()

    device_info = DeviceInfoService(
        software_revision=adafruit_ble.__version__,
        manufacturer="Adafruit")

    advertisement = ProvideServicesAdvertisement(hid)
    advertisement.appearance = 962
    # scan_response = Advertisement()
    # scan_response.complete_name = "GBUID"

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

    
    def play_melody(self,melody):
        for freq, duration in melody:
            simpleio.tone(self.buzzer, freq, duration)
            time.sleep(0.05)

    def operate_mouse(self):
        dataset_empty = self.helpers.dataset_empty("gesture_training_dataset.csv")
        if not dataset_empty:
            self.gmm.train(self.helpers.organise_data("gesture_training_dataset.csv"))
        self.display_manager.ready_to_pair_screen()
        self.ble.start_advertising(self.advertisement)
        self.play_melody(self.on_melody)
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
                self.display_manager.tracking_screen(self.sensor_btn_toggle_value)
            else:
                if not self.ble.advertising:
                    self.play_melody(self.connection_lost_melody)
                    self.ble.start_advertising(self.advertisement)
                self.display_manager.ready_to_pair_screen()
