import time
import board
import digitalio
import simpleio
import adafruit_lsm6ds.lsm6ds33
from helpers.csv_helpers import CsvHelpers
from ml.knn import KNN
import circuitpython_csv as csv


class Calibration:
    csv_helpers = CsvHelpers()
    knn = KNN()
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
            if cancel_calibration_btn_curr_state != cancel_calibration_btn_last_touch_val:
                if not cancel_calibration_btn_curr_state:
                    cancel_calibration_btn_toggle_val = not cancel_calibration_btn_toggle_val
                    cancel_calibration_btn.deinit()
                    calibrate_btn.deinit()
                    cancel_calibration_btn = None
                    break
            cancel_calibration_btn_last_touch_val = cancel_calibration_btn_curr_state
            calibrate_btn_last_touch_val = calibrate_btn_curr_state

    def calibration(self):
        filename = "movement_data.csv"
        print("SIDE TO SIDE")
        start_time = time.monotonic()
        with open(filename, mode="w", encoding="utf-8") as file:
            writer = csv.writer(file)
            while (time.monotonic() - start_time) < 5:
                movement = self.accel.acceleration
                writer.writerow(movement + (0,))
                time.sleep(0.1)
        print("UP AND DOWN")
        start_time = time.monotonic()
        with open(filename, mode="w", encoding="utf-8") as file:
            writer = csv.writer(file)
            while (time.monotonic() - start_time) < 5:
                movement = self.accel.acceleration
                writer.writerow(movement + (1,))
                time.sleep(0.1)
        print("SAVING DATA")
        dataset = self.csv_helpers.create_dataset(filename)
        self.csv_helpers.seperate_labels_and_data(dataset)
  


      
