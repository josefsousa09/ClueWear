import board
import displayio
import terminalio
from adafruit_display_text import label


class DisplayManager:
    def __init__(self) -> None:
        self.display = board.DISPLAY
        self.screen = displayio.Group()
        self.bg_color = 0x0000
        self.bg_bitmap = displayio.Bitmap(
            self.display.width, self.display.height, 1)
        self.bg_palette = displayio.Palette(1)
        self.bg_palette[0] = self.bg_color
        self.bg_sprite = displayio.TileGrid(
            self.bg_bitmap, pixel_shader=self.bg_palette, x=0, y=0)
        self.screen.append(self.bg_sprite)
        self.main_label = label.Label(terminalio.FONT, text="", scale=2)
        self.button_labels = label.Label(
            terminalio.FONT, text="", scale=2)
        self.secondary_label = label.Label(terminalio.FONT, text="", scale=2)
        self.screen.append(self.main_label)
        self.screen.append(self.secondary_label)
        self.screen.append(self.button_labels)

    def ready_to_pair_screen(self):
        if self.main_label.text != "READY TO PAIR":
            self._update_main_label("READY TO PAIR", 0x0000FF)
            self._update_button_labels("PAUSE", "CALIBRATE")
            self.display.show(self.screen)

    def tracking_screen(self, tracking_status):
        if not tracking_status and self.main_label.text != "NOT TRACKING":
            self._update_main_label("NOT TRACKING", 0xFF0000)
            self._update_button_labels("RESUME", "CALIBRATE")

        elif tracking_status and self.main_label.text != "TRACKING":
            self._update_main_label("TRACKING", 0x00FF00)
            self._update_button_labels("PAUSE", "CALIBRATE")

    def calibration_screen(self, main_label, secondary_label):
        if self.button_labels.text != "":
            self._update_button_labels("", "")
        self._update_main_label(main_label, 0xFFFFFF)
        self._update_secondary_label(secondary_label)

    def calibration_menu_screen(self):
        if self.main_label.text != "CALIBRATION MODE":
            self._update_main_label("CALIBRATION MODE", 0xFFFFFF)
            self._update_button_labels("CANCEL", "START")

    def _update_main_label(self, text, color):
        space = (19 - len(text)) * 13 / 2
        self.main_label.text = text
        self.main_label.color = color
        self.main_label.x = int(space)
        self.main_label.y = 70

    def _update_secondary_label(self, text):
        space = (19 - len(text)) * 13 / 2
        self.secondary_label.text = text
        self.secondary_label.x = int(space)
        self.secondary_label.y = 120

    def _update_button_labels(self, left_text, right_text):
        size = len(left_text) + len(right_text) + 2
        self.button_labels.text = '<' + left_text + \
            ' '*(19-size) + right_text + '>'
        self.button_labels.x, self.button_labels.y = 5, 165
