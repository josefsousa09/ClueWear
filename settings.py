import time
import board
import digitalio
from ml.gmm import GMM
import adafruit_lsm6ds.lsm6ds33
from helpers.helpers import Helpers

class Settings:
    helpers = Helpers()

    def __init__(self,display_manager):
        self.display_manager = display_manager
        self.i2c = board.I2C()
        
        self.curr_config = self.helpers.read_config_file()
        self.a_btn = digitalio.DigitalInOut(board.BUTTON_A)
        self.a_btn.direction = digitalio.Direction.INPUT
        self.a_btn.pull = digitalio.Pull.UP
        self.a_btn_last_touch_val = True
        self.a_btn_toggle_val = True


        self.b_btn = digitalio.DigitalInOut(board.BUTTON_B)
        self.b_btn.direction = digitalio.Direction.INPUT
        self.b_btn.pull = digitalio.Pull.UP
        self.b_btn_last_touch_val = True
        self.b_btn_toggle_val = True
        

    def next_setting(self,setting_name):
        if setting_name == 'VERT.SENSITIVITY':
            return 'HORIZ.SENSITIVITY'
        elif setting_name == 'HORIZ.SENSITIVITY':
            return 'VERT.INVERTED'
        elif setting_name == 'VERT.INVERTED':
            return 'HORIZ.INVERTED'
        else:
            return 'VERT.SENSITIVITY'
        
    def bool_change(self,value):
        if value == True:
            return "ON"
        else:
            return "OFF"

    def settings_menu(self):
        curr_setting_name = 'VERT.SENSITIVITY'
        while True:
            a_btn_curr_state = self.a_btn.value
            b_btn_curr_state = self.b_btn.value
            self.display_manager.view_setting(curr_setting_name, str(self.curr_config[curr_setting_name]) + "/5" if str(self.curr_config[curr_setting_name]).isdigit() else self.bool_change(self.curr_config[curr_setting_name]))
            if a_btn_curr_state != self.a_btn_last_touch_val and b_btn_curr_state != self.b_btn_last_touch_val:
                time.sleep(0.5)
                if not a_btn_curr_state or not b_btn_curr_state:
                    self.a_btn.deinit()
                    self.b_btn.deinit()
                    break
            if a_btn_curr_state != self.a_btn_last_touch_val:
                if not a_btn_curr_state:  
                    self.edit_setting(curr_setting_name)
                    self.display_manager.view_setting(curr_setting_name, str(self.curr_config[curr_setting_name]) + "/5" if str(self.curr_config[curr_setting_name]).isdigit() else self.bool_change(self.curr_config[curr_setting_name]))


            if b_btn_curr_state != self.b_btn_last_touch_val:
                if not b_btn_curr_state:
                    curr_setting_name = self.next_setting(curr_setting_name)

            self.a_btn_last_touch_val = a_btn_curr_state
            self.b_btn_last_touch_val = b_btn_curr_state

    def edit_setting(self,curr_setting):
        temp = self.curr_config[curr_setting]
        is_numerical = str(temp).isdigit()
        running = True
        while running:
            a_btn_curr_state = self.a_btn.value
            b_btn_curr_state = self.b_btn.value
            self.display_manager.edit_setting(curr_setting, str(temp) + "/5" if str(temp).isdigit() else self.bool_change(temp),is_numerical)
            
            if a_btn_curr_state != self.a_btn_last_touch_val and b_btn_curr_state != self.b_btn_last_touch_val:
                time.sleep(0.5)
                if not a_btn_curr_state or not b_btn_curr_state:
                    self.curr_config[curr_setting] = temp
                    running = False
            
            if a_btn_curr_state != self.a_btn_last_touch_val:
                if not a_btn_curr_state:
                    if is_numerical:
                        if int(temp) - 1 >= 1:
                            num = int(temp)
                            num-=1
                            temp = str(num)
                    elif temp == True:
                        temp = False
                    
                    self.display_manager.edit_setting(curr_setting, str(temp) + "/5" if str(temp).isdigit() else self.bool_change(temp),is_numerical)
                
            if b_btn_curr_state != self.b_btn_last_touch_val:
                if not b_btn_curr_state:
                    if is_numerical:
                        if int(temp) + 1 <= 5:
                            num = int(temp)
                            num+=1
                            temp = str(num)
                    elif temp == False:
                        temp = True

                    self.display_manager.edit_setting(curr_setting, str(temp) + "/5" if str(temp).isdigit() else self.bool_change(temp),is_numerical)


            self.a_btn_last_touch_val = a_btn_curr_state
            self.b_btn_last_touch_val = b_btn_curr_state

        self.helpers.update_config_file(self.curr_config)


