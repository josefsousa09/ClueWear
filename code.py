from mouse import Mouse
import gc

mouse = Mouse()
gc.enable()

while True:
    mouse.operate_mouse()