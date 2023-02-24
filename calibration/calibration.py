import time
import board
import digitalio
import simpleio
import adafruit_lsm6ds.lsm6ds33
from helpers.helpers import Helpers
from ml.knn import KNN
import circuitpython_csv as csv
import gc


class Calibration:
    helpers = Helpers()
    knn = KNN()

    def __init__(self):
        self.i2c = board.I2C()
        self.accel = adafruit_lsm6ds.lsm6ds33.LSM6DS33(self.i2c)

    def calibrate(self):
        filename = "profiles/profile_1_data.csv"
        print("NEXT ONE IN 5 SECONDS")
        time.sleep(5)
        print("UP DOWN")
        with open(filename, mode="w", encoding="utf-8") as file:
            start_time = time.monotonic()
            writer = csv.writer(file)
            while (time.monotonic() - start_time) <= 5:
                x,z = self.accel.acceleration[0],self.accel.acceleration[2]
                writer.writerow([x,z,0])
                time.sleep(0.1)
            print("NEXT ONE IN 5 SECONDS")
            time.sleep(5)
            print("SIDE TO SIDE")
            start_time = time.monotonic()
            while (time.monotonic() - start_time) <= 5:
                x,z = self.accel.acceleration[0],self.accel.acceleration[2]
                writer.writerow([x,z,0])
                time.sleep(0.1)
            print("NEXT ONE IN 5 SECONDS")
            time.sleep(5)
            print("LEFT-CLICK MOVEMENT")
            start_time = time.monotonic()
            while (time.monotonic() - start_time) <= 5:
                x,z = self.accel.acceleration[0],self.accel.acceleration[2]
                writer.writerow([x,z,1])
                time.sleep(0.1)
            print("NEXT ONE IN 5 SECONDS")
            time.sleep(5)
            print("RIGHT-CLICK MOVEMENT")
            start_time = time.monotonic()
            while (time.monotonic() - start_time) <= 5:
                x,z = self.accel.acceleration[0],self.accel.acceleration[2]
                writer.writerow([x,z,2])
                time.sleep(0.1)
        print("DONE")
        

    def calibration(self):
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
                    self.calibrate()
            if cancel_calibration_btn_curr_state != cancel_calibration_btn_last_touch_val:
                if not cancel_calibration_btn_curr_state:
                    cancel_calibration_btn_toggle_val = not cancel_calibration_btn_toggle_val
                    cancel_calibration_btn.deinit()
                    calibrate_btn.deinit()
                    cancel_calibration_btn = None
                    print("Calibration cancelled")
                    break
            cancel_calibration_btn_last_touch_val = cancel_calibration_btn_curr_state
            calibrate_btn_last_touch_val = calibrate_btn_curr_state


