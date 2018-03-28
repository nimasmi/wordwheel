#!/usr/bin/env python3
import argparse
import math
import random

from PIL import Image, ImageDraw, ImageFont

IMAGE_SIZE = 4000

FONT_FILE = 'leaguespartan-bold.ttf'
centre_font_size = int(IMAGE_SIZE/6)
radial_font_size = int(IMAGE_SIZE/7)
line_width = int(IMAGE_SIZE/100)

diameter = 0.9  # as proportion of image size


parser = argparse.ArgumentParser(description="generate an anagram puzzle image")
parser.add_argument('word', nargs='?', default=None, help='Use a specified input word')
parser.add_argument('--verbatim', help="Use the letters in the order given, anticlockwise from 3 o'clock, followed by centre",
                    action="store_true")

args = parser.parse_args()


def draw_circle(draw_object, image_size, diameter, fill, outline, thickness=1):
    border = image_size * (1 - diameter) / 2
    draw_object.ellipse(
        [
            (border, border),
            (image_size - border, image_size - border),
        ], fill=outline, outline=outline
    )
    draw_object.ellipse(
        [
            (border + thickness, border + thickness),
            (image_size - border - thickness, image_size - border - thickness),
        ], fill=fill, outline=outline
    )


def draw_centred_text(draw_object, coordinates, text, font):
    x, y = coordinates
    w, h = draw_object.textsize(text, font=font)
    draw_object.text((x - w / 2, y - h / 2), text, font=font, fill="black")


im = Image.new('RGB', (IMAGE_SIZE, IMAGE_SIZE), (255, 255, 255))
d = ImageDraw.Draw(im)

# Draw the circles
draw_circle(d, IMAGE_SIZE, diameter, (255, 255, 255), 0, line_width)  # outer circle
draw_circle(d, IMAGE_SIZE, diameter / 3, (200, 200, 200), 0, line_width)  # inner circle

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
    d.line(((x1, y1), (x2, y2)), fill="black", width=line_width)

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
word = args.word
if not word:
    with open('wordlist.txt', 'r') as f:
        word = random.choice(f.readlines()).strip()

letters = list(word.upper())
if not args.verbatim:
    random.shuffle(letters)

# Draw the radial letters
radial_font = ImageFont.truetype(FONT_FILE, radial_font_size)
for letter, (x, y) in zip(letters, radial_letter_coordinates):
    draw_centred_text(d, (x, y), letter, radial_font)

# Draw the centre letter
centre_font = ImageFont.truetype(FONT_FILE, centre_font_size)
draw_centred_text(d, (IMAGE_SIZE / 2, IMAGE_SIZE / 2), letters[-1], font=centre_font)

im.thumbnail((500, 500), Image.ANTIALIAS)
im.save('ww.png')
