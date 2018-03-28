#!/usr/bin/env python3
import math
import random

from PIL import Image, ImageDraw, ImageFont

IMAGE_SIZE = 400

FONT_FILE = '/Library/Fonts/AppleGothic.ttf'
centre_font_size = int(IMAGE_SIZE/5)
radial_font_size = int(IMAGE_SIZE/6)

diameter = 0.9  # as proportion of image size


def draw_circle(draw_object, image_size, diameter, fill, outline):
    border = image_size * (1 - diameter) / 2
    draw_object.ellipse(
        [
            (border, border),
            (image_size - border, image_size - border),
        ], fill=fill, outline=outline
    )


def draw_centred_text(draw_object, coordinates, text, font):
    x, y = coordinates
    w, h = draw_object.textsize(text, font=font)
    draw_object.text((x - w / 2, y - h / 2), text, font=font, fill="black")


im = Image.new('RGB', (IMAGE_SIZE, IMAGE_SIZE), (255, 255, 255))
d = ImageDraw.Draw(im)

# Draw the circles
draw_circle(d, IMAGE_SIZE, diameter, (255, 255, 255), 0)  # outer circle
draw_circle(d, IMAGE_SIZE, diameter / 3, (200, 200, 200), 0)  # inner circle

# Draw the spokes
spoke_end_coordinates = [
    (
        (IMAGE_SIZE/2 + (IMAGE_SIZE * diameter/6 * math.cos(angle)),
         IMAGE_SIZE/2 + (IMAGE_SIZE * diameter/6 * math.sin(angle))),
        (IMAGE_SIZE/2 + (IMAGE_SIZE * diameter/2 * math.cos(angle)),
         IMAGE_SIZE/2 + (IMAGE_SIZE * diameter/2 * math.sin(angle)))
    )
    for angle in [math.radians(45 * x) for x in range(8)]
]

for ((x1, y1), (x2, y2)) in spoke_end_coordinates:
    d.line(((x1, y1), (x2, y2)), fill="black")

radial_font = ImageFont.truetype(FONT_FILE, radial_font_size)
centre_font = ImageFont.truetype(FONT_FILE, centre_font_size)

# Get centre coordinates of the outer letters
radial_letter_coordinates = [
    (
        IMAGE_SIZE/2 + (IMAGE_SIZE * diameter/3 * math.cos(angle)),
        IMAGE_SIZE/2 + (IMAGE_SIZE * diameter/3 * math.sin(angle))
    )
    for angle in
    [
        math.radians(22.5 * x) for x in  # 22.5° is 1/16th of a turn
        range(1, 16, 2)  # eigths of a turn, shifted by 1/16th of a turn
    ]
]

# Get a word
with open('wordlist.txt', 'r') as f:
    word = random.choice(f.readlines()).strip()

letters = list(word.upper())
random.shuffle(letters)

# Draw the radial letters
for letter, (x, y) in zip(letters, radial_letter_coordinates):
    draw_centred_text(d, (x, y), letter, radial_font)

# Draw the centre letter
draw_centred_text(d, (IMAGE_SIZE / 2, IMAGE_SIZE / 2), letters[-1], font=centre_font)

im.save('ww.png')
