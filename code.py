from adafruit_clue import clue
clue_data = clue.simple_text_display(title="CLUE Sensor Data!", title_scale=2)

while True:
    gesture = clue.gesture
    str = "No gesture"
    if gesture == 1:
        str = "UP"
    elif gesture == 2:
        str = "DOWN"
    elif gesture == 3:
        str = "LEFT"
    elif gesture == 4:
        str = "RIGHT"
    clue_data[5].text = f"Gesture: {str}"
    clue_data.show()
