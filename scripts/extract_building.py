"""Mask the original MIT Building 20 illustration without redrawing its pixels."""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

ART = Path(__file__).resolve().parents[1] / "art"
# Traced at the source's native 1800 × 1080 resolution. The upper contour
# includes the antennas; the lower contour follows the walls at ground level.
OUTLINE = (
    (0, 591), (17, 585), (18, 558), (72, 526), (73, 478),
    (458, 389), (459, 369), (870, 273), (870, 175), (931, 175),
    (939, 256), (1005, 240), (1005, 215), (1052, 205),
    (1052, 128), (1088, 128), (1088, 190), (1118, 190),
    (1118, 200), (1154, 214), (1278, 186), (1469, 234),
    (1469, 227), (1517, 211), (1548, 217), (1567, 213),
    (1599, 221), (1599, 238), (1609, 241), (1609, 255),
    (1600, 259), (1657, 242), (1688, 251),
    (1689, 286), (1776, 309), (1777, 440), (1741, 463),
    (1634, 429), (1634, 487), (1519, 558), (1484, 577),
    (1454, 589), (1425, 578), (1381, 554), (1369, 558),
    (1330, 582), (1267, 621), (1233, 635), (1233, 762),
    (1211, 782), (1173, 794), (1150, 805), (1121, 823),
    (1082, 848), (1050, 872), (1012, 896), (982, 884),
    (649, 681), (644, 658), (492, 565), (194, 656),
    (181, 640), (106, 654), (73, 640), (57, 650), (28, 649),
    (0, 642),
)


def extract():
    source = Image.open(ART / "Serendipity_turning-points-serendipity.webp").convert("RGBA")
    if source.size != (1800, 1080):
        raise ValueError("This mask requires the original 1800 × 1080 illustration")
    mask = Image.new("L", source.size)
    ImageDraw.Draw(mask).polygon(OUTLINE, fill=255)
    # Remove the flat sky between the antenna struts and around their outlines.
    pixels, alpha = source.load(), mask.load()
    sky = pixels[0, 0][:3]
    for y in range(300):
        for x in range(860, 1160):
            if alpha[x, y] and max(abs(pixels[x, y][c] - sky[c]) for c in range(3)) < 14:
                alpha[x, y] = 0
    source.putalpha(mask.filter(ImageFilter.GaussianBlur(0.45)))
    source.save(ART / "Building-20-transparent.png", optimize=True)


if __name__ == "__main__":
    extract()
