import time
import board
import digitalio
import simpleio
import adafruit_lsm6ds.lsm6ds33
from helpers import csv_helpers
import gc


class Calibration:
    csv_helpers = csv_helpers.CsvHelpers()

    def __init__(self):
        self.i2c = board.I2C()
        self.accel = adafruit_lsm6ds.lsm6ds33.LSM6DS33(self.i2c)

    def calibrate(self):
        calibrate_btn = digitalio.DigitalInOut(board.BUTTON_B)
        calibrate_btn.direction = digitalio.Direction.INPUT
        calibrate_btn.pull = digitalio.Pull.UP
        calibrate_btn_last_touch_val = False
        calibrate_btn_toggle_val = False

        cancel_calibration_btn = digitalio.DigitalInOut(board.BUTTON_A)
        cancel_calibration_btn.direction = digitalio.Direction.INPUT
        cancel_calibration_btn.pull = digitalio.Pull.UP
        cancel_calibration_btn_last_touch_val = False
        cancel_calibration_btn_toggle_val = False

        while True:
            calibrate_btn_curr_state = calibrate_btn.value
            cancel_calibration_btn_curr_state = cancel_calibration_btn.value

            if calibrate_btn_curr_state != calibrate_btn_last_touch_val:
                if not calibrate_btn_curr_state:
                    self.calibration()
                    gc.collect()
            if cancel_calibration_btn_curr_state != cancel_calibration_btn_last_touch_val:
                if not cancel_calibration_btn_curr_state:
                    cancel_calibration_btn_toggle_val = not cancel_calibration_btn_toggle_val
                    cancel_calibration_btn.deinit()
                    calibrate_btn.deinit()
                    cancel_calibration_btn = None
                    gc.collect()
                    break
            cancel_calibration_btn_last_touch_val = cancel_calibration_btn_curr_state
            calibrate_btn_last_touch_val = calibrate_btn_curr_state

    def calibration(self):
        print("SIDE TO SIDE")
        start_time = time.monotonic()
        movement_data = []
        while (time.monotonic() - start_time) < 5:
            movement = self.accel.acceleration
            movement_data.append(movement + ("horizontal",))
            time.sleep(0.15)
        print("UP AND DOWN")
        start_time = time.monotonic()
        while (time.monotonic() - start_time) < 5:
            movement = self.accel.acceleration
            movement_data.append(movement + ("vertical",))
            time.sleep(0.15)
        self.csv_helpers.save_calibration_data(movement_data)
        gc.collect()
        print(self.csv_helpers.import_data().pop())
