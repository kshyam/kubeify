#!/usr/bin/env python3
"""Create Kubeify-branded 1200x630 blog images using Pillow."""
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont


def generate(title, path):
    image = Image.new('RGB', (1200, 630), '#101c42')
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, 20, 630), fill='#3c58cd')
    for x in range(770, 1200, 80):
        for y in range(40, 600, 80):
            draw.ellipse((x, y, x + 5, y + 5), fill='#29407a')
    regular = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
    bold = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
    draw.text((75, 65), 'KUBEIFY  /  DEVOPS & AI', font=ImageFont.truetype(bold, 23), fill='#27c1a5')
    for size in range(54, 23, -2):
        font = ImageFont.truetype(bold, size)
        lines = []
        line = ''
        for word in title.split():
            candidate = (line + ' ' + word).strip()
            if draw.textlength(candidate, font=font) > 980 and line:
                lines.append(line)
                line = word
            else:
                line = candidate
        if line:
            lines.append(line)
        if len(lines) * (size + 18) <= 325 and all(draw.textlength(item, font=font) <= 980 for item in lines):
            break
    else:
        raise ValueError('Title is too long for the banner')
    for i, line in enumerate(lines):
        draw.text((75, 145 + i * (size + 18)), line, font=font, fill='white')
    draw.rectangle((75, 520, 190, 525), fill='#27c1a5')
    draw.text((75, 552), 'kubeify.com', font=ImageFont.truetype(regular, 22), fill='#ccd8f4')
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    image.save(path, 'WEBP', quality=88)


if __name__ == '__main__':
    generate(sys.argv[1], sys.argv[2])
