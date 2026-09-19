"""Extract the supplied B20V logo and its repeating grid without redrawing.

Coordinates and colors below are measured from art/B20V-with-grid.png. The
500px grid period is exact; the left margin is free of logo artwork. Alpha
matting against the measured logo palette preserves antialiased edges and the
translucent crimson glow. Fully opaque source colors remain unchanged.
"""

from pathlib import Path

from PIL import Image

ART = Path(__file__).resolve().parents[1] / "art"
PERIOD = 500
PALETTE = ((35, 40, 48), (163, 31, 52), (110, 118, 130), (150, 160, 172))


def foreground(pixel, background):
    if pixel == background:
        return (0, 0, 0, 0)
    if pixel in PALETTE:
        return (*pixel, 255)
    best_error, best_color, best_alpha = float("inf"), pixel, 1.0
    difference = tuple(p - b for p, b in zip(pixel, background))
    for color in PALETTE:
        direction = tuple(c - b for c, b in zip(color, background))
        alpha = min(1.0, max(0.0, sum(d * v for d, v in zip(difference, direction)) / sum(v * v for v in direction)))
        error = sum((d - alpha * v) ** 2 for d, v in zip(difference, direction))
        if error < best_error:
            best_error, best_color, best_alpha = error, color, alpha
    if best_error <= 3:
        return (*best_color, round(best_alpha * 255))
    # Overlapping colored strokes need not match a single palette color.
    return (*pixel, 255)


def extract():
    source = Image.open(ART / "B20V-with-grid.png").convert("RGB")
    if source.size != (1600, 873):
        raise ValueError("This extractor requires the original 1600 × 873 logo")
    pixels = source.load()
    tile = Image.new("RGB", (PERIOD, PERIOD))
    grid = tile.load()
    for y in range(PERIOD):
        for x in range(PERIOD):
            # Sample grid-only margins; skip the decorative horizontal guide.
            grid[x, y] = pixels[x if x < 400 else x + 1000, y + PERIOD if y == 295 else y]
    tile.save(ART / "B20V-grid.png", optimize=True)

    logo = Image.new("RGBA", source.size)
    result = logo.load()
    for y in range(source.height):
        # This clean band also captures the two faint horizontal guides, so
        # those are removed along with the grid from the transparent logo.
        colors, backgrounds = [], []
        for x in range(114, 400):
            color = grid[x, y % PERIOD]
            if color not in colors:
                colors.append(color)
                backgrounds.append(pixels[x, y])
        for x in range(420, 1261):
            background = backgrounds[colors.index(grid[x % PERIOD, y % PERIOD])]
            result[x, y] = foreground(pixels[x, y], background)
    logo.save(ART / "B20V-without-grid.png", optimize=True)
    left, top, right, bottom = logo.getbbox()
    cropped = logo.crop((left - 12, top - 12, right + 12, bottom + 12))
    cropped.save(ART / "B20V-logo.png", optimize=True)
    print(f"Transparent logo: {logo.size}; website crop: {cropped.size}; grid: {tile.size}")


if __name__ == "__main__":
    extract()
