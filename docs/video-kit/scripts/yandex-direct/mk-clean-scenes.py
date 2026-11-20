#!/usr/bin/env python3
"""Concept E: props removed from the left (text) zone of Mira/Lera/Kira scenes (image edit of the kit scene,
same framing, expert unchanged). Upscale + portrait mask like scene/src/mask1.py.
Run with /home/box/rembg-venv/bin/python. Input: scenes/<id>-clean-src.jpg  ->  scenes/<id>-16x9-up.jpg + -mask.png"""
import sys
from pathlib import Path
from PIL import Image, ImageFilter
from rembg import remove, new_session
D = Path(__file__).resolve().parent / 'scenes'; s = new_session('birefnet-portrait')
for e in sys.argv[1:] or ['mira', 'lera', 'kira']:
    im = Image.open(D / f'{e}-clean-src.jpg').convert('RGB')
    im.resize((1920, 1080), Image.LANCZOS).filter(ImageFilter.UnsharpMask(radius=1.2, percent=40, threshold=2)).save(D / f'{e}-16x9-up.jpg', quality=95)
    remove(im, session=s, only_mask=True).resize((1920, 1080), Image.BILINEAR).save(D / f'{e}-16x9-mask.png'); print(e, flush=True)
