import time
import board
import digitalio
from ml.gmm import GMM
import simpleio
import adafruit_lsm6ds.lsm6ds33
from helpers.helpers import Helpers
import circuitpython_csv as csv
import displayio
import terminalio
from adafruit_display_text import label



class Calibration:
    helpers = Helpers()
    gmm = GMM()

    def __init__(self,display_manager):
        self.display_manager = display_manager
        self.i2c = board.I2C()
        self.accel = adafruit_lsm6ds.lsm6ds33.LSM6DS33(self.i2c)

        
    def calibrate(self):
        filename = "profiles/profile_1_data.csv"
        for i in range(5, 0 ,-1):
            self.display_manager.calibration_screen("VERT. BEGINS IN",str(i) + " seconds")
            time.sleep(1)
        self.display_manager.calibration_screen("MOV. UP AND DOWN","")
        with open(filename, mode="w", encoding="utf-8") as file:
            start_time = time.monotonic()
            writer = csv.writer(file)
            while (time.monotonic() - start_time) <= 5:
                x,y,z = self.accel.acceleration
                writer.writerow([x,y,z,"general_mov"])
                time.sleep(0.1)
            for i in range(5, 0 , -1):
                self.display_manager.calibration_screen("HORIZ. BEGINS IN",str(i) + " seconds")
                time.sleep(1)
            self.display_manager.calibration_screen("MOV. SIDE TO SIDE","")
            start_time = time.monotonic()
            while (time.monotonic() - start_time) <= 5:
                x,y,z = self.accel.acceleration
                writer.writerow([x,y,z,"general_mov"])
                time.sleep(0.1)
            for i in range(5, 0 , -1):
                self.display_manager.calibration_screen("L.CLICK BEGINS IN",str(i) + " seconds")
                time.sleep(1)
            self.display_manager.calibration_screen("DO L.CLICK MOV.","")
            start_time = time.monotonic()
            while (time.monotonic() - start_time) <= 5:
                x,y,z = self.accel.acceleration
                writer.writerow([x,y,z,"left_click"])
                time.sleep(0.1)
            for i in range(5, 0 , -1):
                self.display_manager.calibration_screen("R.CLICK BEGINS IN",str(i) + " seconds")
                time.sleep(1)
            self.display_manager.calibration_screen("DO R.CLICK MOV.","")
            start_time = time.monotonic()
            while (time.monotonic() - start_time) <= 5:
                x,y,z = self.accel.acceleration
                writer.writerow([x,y,z,"right_click"])
                time.sleep(0.1)
            file.close()
        self.gmm.train()
        self.display_manager.calibration_screen("CALIBRATION COMPLETE","")
        time.sleep(3)

        

    def calibration(self):
        self.display_manager.calibration_menu_screen()

        cancel_calibration_btn = digitalio.DigitalInOut(board.BUTTON_A)
        cancel_calibration_btn.direction = digitalio.Direction.INPUT
        cancel_calibration_btn.pull = digitalio.Pull.UP
        cancel_calibration_btn_last_touch_val = False
        cancel_calibration_btn_toggle_val = False
        calibrate_btn = digitalio.DigitalInOut(board.BUTTON_B)
        calibrate_btn.direction = digitalio.Direction.INPUT
        calibrate_btn.pull = digitalio.Pull.UP
        calibrate_btn_last_touch_val = False
        calibrate_btn_toggle_val = False
        while True:
            calibrate_btn_curr_state = calibrate_btn.value
            cancel_calibration_btn_curr_state = cancel_calibration_btn.value
            if calibrate_btn_curr_state != calibrate_btn_last_touch_val:
                if not calibrate_btn_curr_state:
                    self.calibrate()
                    self.display_manager.calibration_menu_screen()
            if cancel_calibration_btn_curr_state != cancel_calibration_btn_last_touch_val:
                if not cancel_calibration_btn_curr_state:
                    cancel_calibration_btn_toggle_val = not cancel_calibration_btn_toggle_val
                    cancel_calibration_btn.deinit()
                    calibrate_btn.deinit()
                    cancel_calibration_btn = None
                    break
            cancel_calibration_btn_last_touch_val = cancel_calibration_btn_curr_state
            calibrate_btn_last_touch_val = calibrate_btn_curr_state


