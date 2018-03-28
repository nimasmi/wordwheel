#!/usr/bin/env python3
from PIL import ImageDraw, ImageFont, Image
import math
import random

IMAGE_SIZE = 400

FONT_FILE = '/Library/Fonts/AppleGothic.ttf'
centre_font_size = int(IMAGE_SIZE/5)
radial_font_size = int(IMAGE_SIZE/6)

radius = 0.9  # as proportion of image size

im = Image.new('RGB', (IMAGE_SIZE,IMAGE_SIZE), (255,255,255))
d = ImageDraw.Draw(im)

def draw_circle(draw_object, image_size, radius, fill, outline):
    border = image_size * (1 - radius) / 2
    draw_object.ellipse(
        [
            (border, border),
            (image_size - border, image_size - border),
        ], fill=fill, outline=outline
    )

# Draw the circles
draw_circle(d, IMAGE_SIZE, radius, (255, 255, 255), 0)  # outer circle
draw_circle(d, IMAGE_SIZE, radius / 3, (200, 200, 200), 0)  # inner circle

radial_fnt = ImageFont.truetype(FONT_FILE, radial_font_size)
centre_fnt = ImageFont.truetype(FONT_FILE, centre_font_size)

def get_corner_coordinates(coordinates, fontsize):
    return [coord - (fontsize / 2) for coord in coordinates]

radial_letter_coordinates = [
    (
        IMAGE_SIZE/2 + (IMAGE_SIZE * radius/3 * math.cos(angle)),
        IMAGE_SIZE/2 + (IMAGE_SIZE * radius/3 * math.sin(angle))
    )
    for angle in 
    [
        math.radians(22.5 * x) for x in  # 22.5° is 1/16th of a turn
        range(1, 16, 2)  # eigths of a turn, shifted by 1/16th of a turn
    ]
]

# get word
with open('wordlist.txt', 'r') as f:
    word = random.choice(f.readlines()).strip()

letters = list(word.upper())
random.shuffle(letters)

# Draw the radial letters
for letter, (x, y) in zip(letters, radial_letter_coordinates):
    d.text(get_corner_coordinates((x, y), radial_font_size), letter, font=radial_fnt, fill=(0,0,0))

# Draw the centre letter
d.text(get_corner_coordinates((IMAGE_SIZE/2, IMAGE_SIZE/2), centre_font_size), letters[-1], font=centre_fnt, fill=(0,0,0))

im.save('ww.png')
