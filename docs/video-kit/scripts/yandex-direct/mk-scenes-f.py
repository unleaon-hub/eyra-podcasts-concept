#!/usr/bin/env python3
"""Concept F: two-zone scenes (light sunlit wall left | deep wall + art, plant, prop behind the expert).
scenes-f/<id>-src.jpg = image edit of the kit scene (same framing, expert unchanged; faces checked in previews/F-faces.jpg).
Upscale to 1920x1080 + portrait mask. Run one expert per call with /home/box/rembg-venv/bin/python (RAM)."""
import sys
from pathlib import Path
from PIL import Image, ImageFilter
from rembg import remove, new_session
D = Path(__file__).resolve().parent / 'scenes-f'; s = new_session('birefnet-portrait')
for e in sys.argv[1:]:
    im = Image.open(D / f'{e}-src.jpg').convert('RGB')
    im.resize((1920, 1080), Image.LANCZOS).filter(ImageFilter.UnsharpMask(radius=1.2, percent=40, threshold=2)).save(D / f'{e}-16x9-up.jpg', quality=95)
    remove(im, session=s, only_mask=True).resize((1920, 1080), Image.BILINEAR).save(D / f'{e}-16x9-mask.png'); print(e, flush=True)
