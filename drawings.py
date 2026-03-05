import time
from luma.core.render import canvas

# ---- Static drawings ----

def draw_pacman(draw):
    draw.pieslice((36, 4, 92, 60), start=30, end=330, fill="white")
    draw.ellipse((55, 14, 63, 22), fill="black")


def draw_smiley(draw):
    draw.ellipse((36, 4, 92, 60), outline="white")
    draw.ellipse((49, 18, 57, 26), fill="white")  # left eye
    draw.ellipse((71, 18, 79, 26), fill="white")  # right eye
    draw.arc((50, 24, 78, 52), start=25, end=155, fill="white")


# ---- Animated Pacman ----

_SIZE = 20          # pacman diameter
_TOP = 22           # top of bounding box → center at y=32
_PELLET_Y = 32
_PELLET_XS = list(range(30, 120, 12))


def _draw_pacman_at(draw, x, mouth_open):
    bot = _TOP + _SIZE
    right = x + _SIZE
    if mouth_open:
        draw.pieslice((x, _TOP, right, bot), start=30, end=330, fill="white")
    else:
        draw.ellipse((x, _TOP, right, bot), fill="white")
    # Eye
    ex, ey = x + 6, _TOP + 4
    draw.ellipse((ex, ey, ex + 3, ey + 3), fill="black")


def _draw_pellets(draw, positions):
    for px in positions:
        draw.ellipse((px - 1, _PELLET_Y - 1, px + 1, _PELLET_Y + 1), fill="white")


def animate_pacman(oled, is_active):
    """Continuously animate pacman eating pellets across the OLED.
    is_active: callable returning bool — pauses and clears when False.
    """
    x = -_SIZE
    frame = 0
    pellets = list(_PELLET_XS)
    was_active = True

    while True:
        active = is_active()

        if not active:
            if was_active:
                oled.clear()
                was_active = False
            time.sleep(0.1)
            continue

        if not was_active:
            x, frame, pellets = -_SIZE, 0, list(_PELLET_XS)
            was_active = True

        mouth_open = (frame // 3) % 2 == 0
        center_x = x + _SIZE // 2
        pellets = [p for p in pellets if p > center_x]

        with canvas(oled) as draw:
            _draw_pellets(draw, pellets)
            _draw_pacman_at(draw, x, mouth_open)

        x += 2
        frame += 1

        if x > 128:
            x, pellets = -_SIZE, list(_PELLET_XS)

        time.sleep(0.05)


# ---- Bad Apple ----

_BA_W, _BA_H = 128, 64
_BA_FPS = 30


def animate_video(oled, is_active, npy_path="videos/badapple.npy"):
    """Play a video from a packed numpy file produced by convert_video.py.
    is_active: callable returning bool — pauses and clears when False.
    """
    import numpy as np
    from PIL import Image as PILImage

    try:
        data = np.load(npy_path)      # shape: (n_frames, 1024)
    except FileNotFoundError:
        print(f"[animate_video] {npy_path} not found — run convert_video.py first. Falling back to pacman.")
        return animate_pacman(oled, is_active)  # fallback
    n = len(data)
    if n == 0:
        print(f"[animate_video] {npy_path} has 0 frames — re-run convert_video.py. Falling back to pacman.")
        return animate_pacman(oled, is_active)  # fallback
    frame_delay = 1.0 / _BA_FPS
    i = 0
    was_active = True

    while True:
        active = is_active()

        if not active:
            if was_active:
                oled.clear()
                was_active = False
            time.sleep(0.1)
            continue

        if not was_active:
            i = 0
            was_active = True

        t0 = time.monotonic()

        pixels = np.unpackbits(data[i]).reshape(_BA_H, _BA_W)
        img = PILImage.fromarray(pixels * 255).convert("1")
        oled.display(img)

        i = (i + 1) % n

        dt = time.monotonic() - t0
        sleep = frame_delay - dt
        if sleep > 0:
            time.sleep(sleep)
