#!/usr/bin/env python3
"""
MAX7219 Dual Panel (8x16) LED Dot Matrix - RPi CPU Temperature Display
Static display, no scrolling. Shows xx.xC in TINY_FONT.

Wiring:
  MAX7219 VCC  -> RPi 5V   (pin 2)
  MAX7219 GND  -> RPi GND  (pin 6)
  MAX7219 DIN  -> GPIO 10  MOSI (pin 19)
  MAX7219 CS   -> GPIO 8   CE0  (pin 24)
  MAX7219 CLK  -> GPIO 11  SCLK (pin 23)

Install:
  pip install luma.led_matrix luma.core pillow --break-system-packages
  sudo raspi-config -> Interface Options -> SPI -> Enable
"""

import time
import subprocess
from luma.led_matrix.device import max7219
from luma.core.interface.serial import spi, noop
from luma.core.render import canvas
from luma.core.legacy import text
from luma.core.legacy.font import proportional, TINY_FONT


def get_cpu_temp() -> float:
    try:
        with open("/sys/class/thermal/thermal_zone0/temp") as f:
            return round(int(f.read()) / 1000.0, 1)
    except FileNotFoundError:
        result = subprocess.run(["vcgencmd", "measure_temp"], capture_output=True, text=True)
        return float(result.stdout.strip().replace("temp=", "").replace("'C", ""))


def setup_device(cascaded: int = 2, brightness: int = 8) -> max7219:
    serial = spi(port=0, device=0, gpio=noop())
    device = max7219(
        serial,
        cascaded=cascaded,
        width=cascaded * 8,
        height=8,
        block_orientation=-90,
        rotate=2,
        blocks_arranged_in_reverse_order=False,
    )
    device.contrast(brightness * 16)
    return device


def show_temp(device: max7219, temp: float):
    msg = f"{temp:.1f}C"
    # TINY_FONT is 4px wide per char — "xx.xC" = 5 chars fits 16px wide display
    with canvas(device) as draw:
        text(draw, (0, 1), msg, fill="white", font=proportional(TINY_FONT))


def main():
    print("=== MAX7219 Static Temp Display ===")
    print("Press Ctrl+C to quit.\n")

    device = setup_device(cascaded=2, brightness=8)
    update_interval = 5  # seconds

    try:
        while True:
            temp = get_cpu_temp()
            print(f"CPU Temp: {temp}°C")
            show_temp(device, temp)
            time.sleep(update_interval)
    except KeyboardInterrupt:
        print("\n[EXIT] Clearing display.")
        device.clear()


if __name__ == "__main__":
    main()
