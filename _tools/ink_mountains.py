"""Make the ink mountains at the foot of the pages from real Song paintings.

    python _tools/ink_mountains.py

Writes assets/img/mountains-<name>.webp for each painting below: its brushwork
as transparency, with no silk or paper. The stylesheet uses them as masks filled
with the ink colour, so the lines follow light and dark mode. Which painting a
page shows is set by `mountains:` in its front matter (see _config.yml), and the
credit under it comes from _data/mountains.yml. Needs numpy, scipy,
scikit-image and Pillow.

How the ink is found: the tone of the silk or paper is estimated across the
picture (the 75th percentile of lightness over a wide window), and whatever is
darker than that by more than `ink[0]` becomes ink, fully so at `ink[1]`
(differences in L*). Red collectors' seals and specks smaller than `speck`
pixels are dropped, and the picture fades out to the left and into mist below.
"""

import io
import urllib.request
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage as ndi
from skimage import color, morphology

SITE = Path(__file__).resolve().parent.parent
WIDTH = 1120  # px: twice the width the footer shows them at

# Detail photographs from The Met's open access collection (public domain).
# region: the part of the photo the tone is judged over; crop: the part used, within the region.
PAINTINGS = {
    # Summer Mountains, attributed to Qu Ding, about 1050 (1973.120.1): contour and texture strokes
    "summer": dict(
        source="https://images.metmuseum.org/CRDImages/as/original/DP151481.jpg",
        region=(1230, 300, 3850, 1430), crop=(0, 0, 1548, 714),
        ink=(3, 9), grain=1.2, speck=400, fade_left=0.24,
    ),
    # Cloudy Mountains, Mi Youren (1973.121.1): wet ink along a ridge that rises to sharp peaks
    "cloudy": dict(
        source="https://images.metmuseum.org/CRDImages/as/original/DP212993.jpg",
        region=(500, 236, 3307, 900), crop=None,
        ink=(6, 13), grain=2.0, speck=4000, fade_left=0.08,
    ),
}


def extract_ink(rgb, ink_from, ink_full, grain, speck):
    lab = color.rgb2lab(rgb)
    lightness, red = lab[..., 0], lab[..., 1]
    seals = ndi.binary_dilation(red > 14, iterations=6)
    # the tone of the silk or paper: the 75th percentile of lightness in a wide window, at 1/8 scale
    h, w = lightness.shape
    small = np.asarray(Image.fromarray(lightness.astype(np.float32)).resize((w // 8, h // 8), Image.BILINEAR))
    ground = ndi.gaussian_filter(ndi.percentile_filter(small, 75, size=35), 4)
    ground = np.asarray(Image.fromarray(ground.astype(np.float32)).resize((w, h), Image.BILINEAR))
    darker = ndi.gaussian_filter(np.clip(ground - lightness, 0, None), grain)
    alpha = np.clip((darker - ink_from) / (ink_full - ink_from), 0, 1)
    alpha[seals] = 0
    keep = morphology.remove_small_objects(alpha > 0.25, min_size=speck)
    return alpha * ndi.binary_dilation(keep, iterations=2)


def make(name, source, region, crop, ink, grain, speck, fade_left):
    request = urllib.request.Request(source, headers={"User-Agent": "tomatokeftes.github.io"})
    painting = Image.open(io.BytesIO(urllib.request.urlopen(request, timeout=120).read())).convert("RGB")
    alpha = extract_ink(np.asarray(painting.crop(region)).astype(np.float32) / 255, *ink, grain, speck)
    if crop:
        x0, y0, x1, y1 = crop
        alpha = alpha[y0:y1, x0:x1]

    # fade out to the left, and into mist over the lower half
    h, w = alpha.shape
    left = np.clip(np.linspace(0, 1 / fade_left, w), 0, 1)
    bottom = np.ones(h)
    start = int(h * 0.55)
    bottom[start:] = np.linspace(1, 0, h - start) ** 1.5
    alpha = alpha * left[None, :] * bottom[:, None]

    height = round(h * WIDTH / w)
    mask = Image.fromarray((alpha * 255).astype(np.uint8)).resize((WIDTH, height), Image.LANCZOS)
    image = Image.new("RGBA", mask.size, (0, 0, 0, 0))
    image.putalpha(mask)
    out = SITE / "assets" / "img" / ("mountains-%s.webp" % name)
    image.save(out, "WEBP", quality=80, alpha_quality=80, method=6)
    print("Wrote %s (%dx%d, %d KB)" % (out.relative_to(SITE), WIDTH, height, out.stat().st_size // 1024))


def main():
    for name, settings in PAINTINGS.items():
        make(name, **settings)


if __name__ == "__main__":
    main()
