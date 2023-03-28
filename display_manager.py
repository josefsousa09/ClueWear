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
        self.primary_label = label.Label(terminalio.FONT, text="", scale=2)
        self.button_labels = label.Label(
            terminalio.FONT, text="", scale=2)
        self.secondary_label = label.Label(terminalio.FONT, text="", scale=2)
        self.tertiary_label = label.Label(terminalio.FONT, text="", scale=2)
        self.screen.append(self.primary_label)
        self.screen.append(self.secondary_label)
        self.screen.append(self.button_labels)
        self.screen.append(self.tertiary_label)

    def ready_to_pair_screen(self):
        if self.primary_label.text != "READY TO PAIR":
            self._update_primary_label("READY TO PAIR", 0x0000FF)
            self._update_button_labels("PAUSE", "CALIBRATE")
            self.display.show(self.screen)

    def tracking_screen(self, tracking_status):
        if not tracking_status and self.primary_label.text != "NOT TRACKING":
            self._update_primary_label("NOT TRACKING", 0xFF0000)
            self._update_button_labels("RESUME", "CALIBRATE")
            self._update_tertiary_label("A+B FOR SETTINGS")
            self._update_secondary_label("")

        elif tracking_status and self.primary_label.text != "TRACKING":
            self._update_primary_label("TRACKING", 0x00FF00)
            self._update_button_labels("PAUSE", "CALIBRATE")
            self._update_tertiary_label("A+B FOR SETTINGS")
            self._update_secondary_label("")


    def calibration_screen(self, primary_label, secondary_label):
        if self.button_labels.text != "":
            self._update_button_labels("", "")
        self._update_primary_label(primary_label)
        self._update_secondary_label(secondary_label)
        self._update_tertiary_label("CALIBRATING")

    def calibration_completion_screen(self,tertiary_label):
        self._update_primary_label("")
        self._update_secondary_label("")
        self._update_tertiary_label(tertiary_label)

    def calibration_menu_screen(self):
        if self.primary_label.text != "CALIBRATION MODE":
            self._update_primary_label("CALIBRATION MODE", 0xFFFFFF)
            self._update_button_labels("CANCEL", "START")
            self._update_tertiary_label("")

    def view_setting(self,primary_label,secondary_label):
            self._update_primary_label(primary_label)
            self._update_secondary_label(secondary_label)
            self._update_button_labels("EDIT","NEXT")
            self._update_tertiary_label("A+B TO EXIT")

    def edit_setting(self, primary_label, secondary_label, numerical):
            self._update_primary_label(primary_label)
            self._update_secondary_label(secondary_label)
            if numerical:
                self._update_button_labels('-','+')
            else:
                self._update_button_labels('OFF','ON')
            self._update_tertiary_label("A+B TO SAVE")

    def _update_primary_label(self, text, colour=0xFFFFFF):
        space = (19 - len(text)) * 13 / 2
        self.primary_label.text = text
        self.primary_label.color = colour
        self.primary_label.x = int(space)
        self.primary_label.y = 70

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

    def _update_tertiary_label(self, text):
        space = (19 - len(text)) * 13 / 2
        self.tertiary_label.text = text
        self.tertiary_label.x = int(space)
        self.tertiary_label.y = 200
