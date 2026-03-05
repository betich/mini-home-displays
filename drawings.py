def draw_pacman(draw):
    # Body — open mouth facing right
    draw.pieslice((36, 4, 92, 60), start=30, end=330, fill="white")
    # Eye
    draw.ellipse((55, 14, 63, 22), fill="black")


def draw_smiley(draw):
    draw.ellipse((36, 4, 92, 60), outline="white")
    draw.ellipse((49, 18, 57, 26), fill="white")  # left eye
    draw.ellipse((71, 18, 79, 26), fill="white")  # right eye
    draw.arc((50, 24, 78, 52), start=25, end=155, fill="white")
