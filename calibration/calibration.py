import time
import board
import digitalio
import simpleio
import adafruit_lsm6ds.lsm6ds33
from helpers import csv_helpers


class Calibration:
    csv_helpers = csv_helpers.CsvHelpers()

    def __init__(self):
        self.i2c = board.I2C()
        self.accel = adafruit_lsm6ds.lsm6ds33.LSM6DS33(self.i2c)
        self.mouse_min = -9
        self.mouse_max = 9
        self.step = (self.mouse_max - self.mouse_min) / 20.0

    def mouse_steps(self, axis):
        return round((axis - self.mouse_min) / self.step)

    def calibrate(self):
        x_movements = []
        y_movements = []

        step_counter = 0

        calibrate_btn = digitalio.DigitalInOut(board.BUTTON_A)
        calibrate_btn.direction = digitalio.Direction.INPUT
        calibrate_btn.pull = digitalio.Pull.UP
        calibrate_btn_last_touch_val = False
        calibrate_btn_toggle_val = False

        cancel_calibration_btn = digitalio.DigitalInOut(board.BUTTON_B)
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

            if cancel_calibration_btn_curr_state != cancel_calibration_btn_last_touch_val:
                if not cancel_calibration_btn_curr_state:
                    cancel_calibration_btn_toggle_val = not cancel_calibration_btn_toggle_val
                    cancel_calibration_btn.deinit()
                    calibrate_btn.deinit()
                    cancel_calibration_btn = None
                    print("CALIBRATION CANCELLED")
                    break
            cancel_calibration_btn_last_touch_val = cancel_calibration_btn_curr_state
            calibrate_btn_last_touch_val = calibrate_btn_curr_state

    def calibration(self):
        print("MOVE SIDE TO SIDE")
        start_time = time.monotonic()
        movement_data = []
        while (time.monotonic() - start_time) < 5:
            movement = self.accel.acceleration
            movement_data.append(movement + ("horizontal",))
            time.sleep(0.1)
        print("UP AND DOWN")
        start_time = time.monotonic()
        while (time.monotonic() - start_time) < 5:
            movement = self.accel.acceleration
            movement_data.append(movement + ("vertical",))
            time.sleep(0.1)
        print("SAVING")
        self.csv_helpers.save_calibration_data(movement_data)
