import time
import board
import digitalio
import simpleio
import adafruit_lsm6ds.lsm6ds33
from calibration.calibration_status import CalibrationStatus


class Calibration:

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
            if cancel_calibration_btn_toggle_val:
                x, y, z = self.accel.acceleration
                horizontal_mov = simpleio.map_range(
                    self.mouse_steps(x), 1.0, 20.0, -15.0, 15.0)
                vertical_mov = simpleio.map_range(
                    self.mouse_steps(y), 20.0, 1.0, -15.0, 15.0)

                if step_counter == CalibrationStatus.START.value:
                    print("START")
                    x_movements.append(horizontal_mov)
                    y_movements.append(vertical_mov)

                elif step_counter == CalibrationStatus.CENTER.value:
                    print("CENTER")
                    x_movements.append(horizontal_mov)
                    y_movements.append(vertical_mov)

                elif step_counter == CalibrationStatus.UP.value:
                    print("UP")
                    x_movements.append(horizontal_mov)
                    y_movements.append(vertical_mov)

                elif step_counter == CalibrationStatus.DOWN.value:
                    print("DOWN")
                    x_movements.append(horizontal_mov)
                    y_movements.append(vertical_mov)

                elif step_counter == CalibrationStatus.RIGHT.value:
                    print("RIGHT")
                    x_movements.append(horizontal_mov)
                    y_movements.append(vertical_mov)

                elif step_counter == CalibrationStatus.LEFT.value:
                    print("LEFT")
                    x_movements.append(horizontal_mov)
                    y_movements.append(vertical_mov)

                elif step_counter == CalibrationStatus.END.value:
                    print("Processing...")
                    print(x_movements)
                    print(y_movements)
                    step_counter = CalibrationStatus.START.value

            if calibrate_btn_curr_state != calibrate_btn_last_touch_val:
                if not calibrate_btn_curr_state:
                    calibrate_btn_toggle_val = not calibrate_btn_toggle_val
                    step_counter+=1
                    
            if cancel_calibration_btn_curr_state != cancel_calibration_btn_last_touch_val:
                if not cancel_calibration_btn_curr_state:
                    cancel_calibration_btn_toggle_val = not cancel_calibration_btn_toggle_val
                    cancel_calibration_btn.deinit()
                    cancel_calibration_btn = None
                    print("CALIBRATION CANCELLED")
                    break
            cancel_calibration_btn_last_touch_val = cancel_calibration_btn_curr_state
