import time
import board
import simpleio
import digitalio
import adafruit_lsm6ds.lsm6ds33
from helpers.helpers import Helpers
import circuitpython_csv as csv


class Calibration:
    helpers = Helpers()

    def __init__(self, display_manager, gmm):
        self.gmm = gmm
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

        self.buzzer = board.P0

        self.gestures = {"L.CLICK":"left_click","R.CLICK":"right_click"}

    def calibrate(self):
        filename = "gesture_training_dataset.csv"
        with open(filename, mode="w", encoding="utf-8") as file:
            writer = csv.writer(file)
            for k,v in self.gestures.items():
                for i in range(5, 0, -1):
                    self.display_manager.calibration_screen(
                        f"{k} BEGINS IN", str(i) + " seconds")
                    time.sleep(1)
                self.display_manager.calibration_screen(f"DO {k} MOV.", "")
                start_time = time.monotonic()
                while (time.monotonic() - start_time) <= 10:
                    x, y, z = self.sensor.acceleration
                    writer.writerow([x, y, z, v])
                    time.sleep(0.1)
                for _ in range(3):
                    simpleio.tone(self.buzzer, 440, 0.1)
                    time.sleep(0.1)
            file.close()
        try:
            self.display_manager.calibration_completion_screen("PROCESSING")
            self.gmm.train(self.helpers.organise_data("gesture_training_dataset.csv"))
            self.display_manager.calibration_completion_screen("COMPLETED")
        except:
            self.display_manager.calibration_completion_screen(
                "FAILED, TRY AGAIN")
        time.sleep(3)

    def calibration_menu(self):
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