import time
import board
import digitalio
import simpleio
import adafruit_lsm6ds.lsm6ds33
class Calibration:

    def __init__(self):     
        self.i2c = board.I2C()
        self.accel = adafruit_lsm6ds.lsm6ds33.LSM6DS33(self.i2c)
        self.mouse_min = -9
        self.mouse_max = 9
        self.step = (self.mouse_max - self.mouse_min) / 20.0

    def mouse_steps(self,axis):
        return round((axis - self.mouse_min) / self.step)

    def calibrate(self):
        x_movements = []
        y_movements = []
        cancel_calibration_btn = digitalio.DigitalInOut(board.BUTTON_B)
        cancel_calibration_btn.direction = digitalio.Direction.INPUT
        cancel_calibration_btn.pull = digitalio.Pull.UP
        cancel_calibration_btn_last_touch_val = False
        cancel_calibration_btn_toggle_val = False
        
        while True:
            cancel_calibration_btn_curr_state = cancel_calibration_btn.value
            if cancel_calibration_btn_toggle_val:
                # x,y,z = self.accel.acceleration
                # horizontal_mov = simpleio.map_range(self.mouse_steps(x), 1.0,20.0,-15.0, 15.0)
                # vertical_mov = simpleio.map_range(self.mouse_steps(y), 20.0,1.0,-15.0,15.0)
                # x_movements.append(horizontal_mov)
                # y_movements.append(vertical_mov)
                pass
            if cancel_calibration_btn_curr_state != cancel_calibration_btn_last_touch_val:
                if not cancel_calibration_btn_curr_state:
                    cancel_calibration_btn_toggle_val = not cancel_calibration_btn_toggle_val
                    cancel_calibration_btn.deinit()
                    cancel_calibration_btn = None
                    print("CALIBRATION CANCELLED")
                    break
            cancel_calibration_btn_last_touch_val = cancel_calibration_btn_curr_state
                 