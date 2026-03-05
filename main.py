import os
os.environ["GPIOZERO_PIN_FACTORY"] = "lgpio"

import time
import threading
import subprocess
from signal import pause

from gpiozero import Button

from luma.core.interface.serial import spi, i2c, noop
from luma.core.render import canvas
from luma.core.legacy import text

from luma.core.legacy.font import proportional, TINY_FONT
from luma.led_matrix.device import max7219
from luma.oled.device import ssd1306

from PIL import ImageFont

# -----------------------------
# BUTTON
# -----------------------------

BUTTON_PIN = 17
button = Button(BUTTON_PIN, pull_up=True, bounce_time=0.05)

# -----------------------------
# MATRIX (SPI)
# -----------------------------

spi_serial = spi(port=0, device=0, gpio=noop())

matrix = max7219(
    spi_serial,
    cascaded=2,
    width=16,
    height=8,
    block_orientation=-90,
    rotate=2,
    blocks_arranged_in_reverse_order=False,
)

matrix.contrast(8 * 16)

# -----------------------------
# OLED (I2C)
# -----------------------------

i2c_serial = i2c(port=1, address=0x3C)
oled = ssd1306(i2c_serial)

font = ImageFont.load_default()

# -----------------------------
# STATE
# -----------------------------

display_on = True
last_temp = 0.0

# -----------------------------
# CPU TEMP
# -----------------------------

def get_cpu_temp() -> float:
    try:
        with open("/sys/class/thermal/thermal_zone0/temp") as f:
            return round(int(f.read()) / 1000.0, 1)
    except FileNotFoundError:
        result = subprocess.run(["vcgencmd", "measure_temp"], capture_output=True, text=True)
        return float(result.stdout.strip().replace("temp=", "").replace("'C", ""))

# -----------------------------
# DISPLAY UPDATE
# -----------------------------

def draw_smiley(draw):
    # Face outline — center (64, 32), radius 28
    draw.ellipse((36, 4, 92, 60), outline="white")
    # Eyes
    draw.ellipse((49, 18, 57, 26), fill="white")  # left eye
    draw.ellipse((71, 18, 79, 26), fill="white")  # right eye
    # Smile — arc of a circle centered at (64, 36), radius 14
    draw.arc((50, 24, 78, 52), start=25, end=155, fill="white")

def update_oled():
    with canvas(oled) as draw:
        if display_on:
            draw_smiley(draw)

def update_matrix():
    with canvas(matrix) as draw:
        if display_on:
            msg = f"{last_temp:.1f}C"
            text(draw, (0, 1), msg, fill="white", font=proportional(TINY_FONT))

# -----------------------------
# DISPLAY LOOP
# -----------------------------

def display_loop():
    global last_temp
    while True:
        last_temp = get_cpu_temp()
        update_matrix()
        time.sleep(5)

# -----------------------------
# BUTTON HANDLER
# -----------------------------

def toggle_displays():
    global display_on
    display_on = not display_on
    update_matrix()
    update_oled()

button.when_pressed = toggle_displays

# -----------------------------
# MAIN
# -----------------------------

last_temp = get_cpu_temp()
update_oled()
update_matrix()

thread = threading.Thread(target=display_loop)
thread.daemon = True
thread.start()

pause()
