from mouse import Pointer
import gc

pointer = Pointer()
gc.enable()

while True:
    pointer.operate_mouse()