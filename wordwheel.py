#!/usr/bin/env python3
import argparse
import datetime
import math
import random

from PIL import Image, ImageDraw, ImageFont

DEFAULT_OUTPUT_SIZE = 500
SUPERSAMPLING_RATIO = 8  # for antialiasing
BORDER = 0.1  # as proportion of image size
INNER_CIRCLE_DIAMETER = 0.37  # as proportion of circle diameter
DEFAULT_FONT_FILE = 'leaguespartan-bold.ttf'
CENTRE_FONT_SIZE = 0.22  # as proportion of image size
OUTER_FONT_SIZE = 0.145  # as proportion of image size
LETTER_POSITION = 0.5  # as a proportion of the length of the spokes, inside to outside
LINE_WIDTH = 0.012  # as proportion of image size



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


def make_image(letters, verbatim=False, output_size=DEFAULT_OUTPUT_SIZE,
               font_file=DEFAULT_FONT_FILE):
    """ Do something """

    image_size = output_size * SUPERSAMPLING_RATIO
    im = Image.new('RGB', (image_size, image_size), (255, 255, 255))
    d = ImageDraw.Draw(im)

    diameter = 1 - BORDER
    inner_circle_diameter = diameter * INNER_CIRCLE_DIAMETER
    line_width = int(image_size * LINE_WIDTH)

    # Draw the circles
    draw_circle(d, image_size, diameter, (255, 255, 255), 0, line_width)  # outer circle
    draw_circle(d, image_size, inner_circle_diameter, (200, 200, 200), 0, line_width)  # inner circle

    # Draw the spokes
    spoke_end_coordinates = [
        (
            (image_size / 2 + (image_size * inner_circle_diameter / 2 * math.cos(angle)),
             image_size / 2 + (image_size * inner_circle_diameter / 2 * math.sin(angle))),
            (image_size / 2 + (image_size * diameter / 2 * math.cos(angle)),
             image_size / 2 + (image_size * diameter / 2 * math.sin(angle)))
        )
        for angle in [math.radians(45 * x) for x in range(8)]
    ]

    for ((x1, y1), (x2, y2)) in spoke_end_coordinates:
        d.line(((x1, y1), (x2, y2)), fill="black", width=line_width)

    # Get centre coordinates of the outer letters
    letter_radius = image_size / 2 * (inner_circle_diameter + LETTER_POSITION * (diameter - inner_circle_diameter))
    radial_letter_coordinates = [
        (
            image_size / 2 + letter_radius * math.cos(angle),  # x
            image_size / 2 + letter_radius * math.sin(angle)  # y
        )
        for angle in
        [
            math.radians(22.5 * x) for x in  # 22.5° is 1/16th of a turn
            range(1, 16, 2)  # eigths of a turn, shifted by 1/16th of a turn
        ]
    ]

    # Draw the radial letters
    outer_font_size = int(image_size * OUTER_FONT_SIZE)
    outer_font = ImageFont.truetype(font_file, outer_font_size)
    for letter, (x, y) in zip(letters, radial_letter_coordinates):
        draw_centred_text(d, (x, y), letter, outer_font)

    # Draw the centre letter
    centre_font_size = int(image_size * CENTRE_FONT_SIZE)
    centre_font = ImageFont.truetype(font_file, centre_font_size)
    draw_centred_text(d, (image_size / 2, image_size / 2), letters[-1], font=centre_font)

    im.thumbnail((output_size, output_size), Image.ANTIALIAS)

    return im


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="generate an anagram puzzle image")
    parser.add_argument('word', nargs='?', default=None, help='Use a specified input word')
    parser.add_argument('--verbatim', help="use the letters in the order given, clockwise from 3 o'clock, followed by centre",
                        action="store_true")
    parser.add_argument('-o', '--outfile', help="output filename")
    parser.add_argument('-s', '--size', type=int, default=DEFAULT_OUTPUT_SIZE, help="size of the output image")
    parser.add_argument('-f', '--fontfile', default=DEFAULT_FONT_FILE, help="path to a font file")

    args = parser.parse_args()

    # Get a word
    word = args.word
    if not word:
        with open('wordlist.txt', 'r') as f:
            word = random.choice(f.readlines()).strip()

    letters = list(word.upper())
    if not args.verbatim:
        random.shuffle(letters)

    im = make_image(letters, output_size=args.size,
                    font_file=args.fontfile)

    outfile = args.outfile
    if not outfile:
        outfile = datetime.date.today().strftime("%Y%m%d") + '.png'

    im.save(outfile)
    print(f'{outfile} saved.')
    print('Done!')
