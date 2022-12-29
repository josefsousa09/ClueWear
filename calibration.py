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
        
        # self.cancel_toggle_btn = digitalio.DigitalInOut(board.)
        # self.cancel_toggle_btn.direction = digitalio.Direction.INPUT
        # self.cancel_toggle_btn.pull = digitalio.Pull.UP

    
    def mouse_steps(self,axis):
        return round((axis - self.mouse_min) / self.step)

    def cancel_calibration(self):
        pass
    # def signal_handler(signum,frame):
    #     raise Exception("Timed out")

    def calibrate(self):
        x_movements = []
        y_movements = []
        # signal.signal(signal.SIGALRM, self.signal_handler)
        # signal.alarm(10)
        # try:
        while True:
            x,y,z = self.accel.acceleration
            horizontal_mov = simpleio.map_range(self.mouse_steps(x), 1.0,20.0,-15.0, 15.0)
            vertical_mov = simpleio.map_range(self.mouse_steps(y), 20.0,1.0,-15.0,15.0)
            x_movements.append(horizontal_mov)
            y_movements.append(vertical_mov)
            print("printing")
        # except Exception:
        #     print("TIME OVER")
            # with open("/data.csv", "a") as fp:
            #     fp.write("{}, {}\n".format(horizontal_mov,vertical_mov))

    