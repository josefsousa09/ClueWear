import time
import board
import digitalio
from ml.gmm import GMM
import adafruit_lsm6ds.lsm6ds33
from helpers.helpers import Helpers
import circuitpython_csv as csv


class Calibration:
    helpers = Helpers()
    gmm = GMM()

    def __init__(self, display_manager):
        self.display_manager = display_manager
        self.i2c = board.I2C()
        self.sensor = adafruit_lsm6ds.lsm6ds33.LSM6DS33(self.i2c)

        self.cancel_calibration_btn = digitalio.DigitalInOut(board.BUTTON_A)
        self.cancel_calibration_btn.direction = digitalio.Direction.INPUT
        self.cancel_calibration_btn.pull = digitalio.Pull.UP
        self.cancel_calibration_btn_last_touch_val = False
        self.cancel_calibration_btn_toggle_val = False


        self.calibrate_btn = digitalio.DigitalInOut(board.BUTTON_B)
        self.calibrate_btn.direction = digitalio.Direction.INPUT
        self.calibrate_btn.pull = digitalio.Pull.UP
        self.calibrate_btn_last_touch_val = False

    def calibrate(self):
        filename = "profiles/profile_1_data.csv"
        for i in range(5, 0, -1):
            self.display_manager.calibration_screen(
                "VERT. BEGINS IN", str(i) + " seconds")
            time.sleep(1)
        self.display_manager.calibration_screen("DO VERT. MOV.", "")
        with open(filename, mode="w", encoding="utf-8") as file:
            start_time = time.monotonic()
            writer = csv.writer(file)
            while (time.monotonic() - start_time) <= 5:
                x, y, z = self.sensor.acceleration
                writer.writerow([x, y, z, "general_mov"])
                time.sleep(0.1)
            for i in range(5, 0, -1):
                self.display_manager.calibration_screen(
                    "HORIZ. BEGINS IN", str(i) + " seconds")
                time.sleep(1)
            self.display_manager.calibration_screen("DO HORIZ. MOV.", "")
            start_time = time.monotonic()
            while (time.monotonic() - start_time) <= 5:
                x, y, z = self.sensor.acceleration
                writer.writerow([x, y, z, "general_mov"])
                time.sleep(0.1)
            for i in range(5, 0, -1):
                self.display_manager.calibration_screen(
                    "L.CLICK BEGINS IN", str(i) + " seconds")
                time.sleep(1)
            self.display_manager.calibration_screen("DO L.CLICK MOV.", "")
            start_time = time.monotonic()
            while (time.monotonic() - start_time) <= 5:
                x, y, z = self.sensor.acceleration
                writer.writerow([x, y, z, "left_click"])
                time.sleep(0.1)
            for i in range(5, 0, -1):
                self.display_manager.calibration_screen(
                    "R.CLICK BEGINS IN", str(i) + " seconds")
                time.sleep(1)
            self.display_manager.calibration_screen("DO R.CLICK MOV.", "")
            start_time = time.monotonic()
            while (time.monotonic() - start_time) <= 5:
                x, y, z = self.sensor.acceleration
                writer.writerow([x, y, z, "right_click"])
                time.sleep(0.1)
            file.close()
        self.display_manager.calibration_completion_screen("PROCESSING")
        try:
            self.gmm.train()
            self.display_manager.calibration_completion_screen("COMPLETED")
        except:
            self.display_manager.calibration_completion_screen(
                "FAILED, TRY AGAIN")
        time.sleep(3)

    def calibration(self):
        self.display_manager.calibration_menu_screen()

        while True:
            calibrate_btn_curr_state = self.calibrate_btn.value
            cancel_calibration_btn_curr_state = self.cancel_calibration_btn.value
            if calibrate_btn_curr_state != self.calibrate_btn_last_touch_val:
                if not calibrate_btn_curr_state:
                    self.calibrate()
                    self.display_manager.calibration_menu_screen()
            if cancel_calibration_btn_curr_state != self.cancel_calibration_btn_last_touch_val:
                if not cancel_calibration_btn_curr_state:
                    self.cancel_calibration_btn.deinit()
                    self.calibrate_btn.deinit()
                    break
            self.cancel_calibration_btn_last_touch_val = cancel_calibration_btn_curr_state
            self.calibrate_btn_last_touch_val = calibrate_btn_curr_state
