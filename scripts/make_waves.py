#!/usr/bin/env python3
"""Generate assets/waves.svg: the flowing line ribbon used in BIM Farers proposals.

Optional asset script (standard library only). The output is committed, so the
site build does not run this. Each line is c(x) + cos(phase) * a(x), sampled
and smoothed with Catmull-Rom curves; where a(x) crosses zero the lines pinch.
"""
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WIDTH, HEIGHT, LINES, STEP = 1600, 640, 22, 100


def centre(x):
    return 330 + 110 * math.sin(x / 270 + 0.5)


def spread(x):
    return 170 * math.sin(x / 330 + 0.15)


def path(points):
    """Catmull-Rom through the points, written as cubic Bezier segments."""
    d = [f'M{points[0][0]:.0f} {points[0][1]:.0f}']
    for i in range(len(points) - 1):
        p0, p1, p2 = points[max(i - 1, 0)], points[i], points[i + 1]
        p3 = points[min(i + 2, len(points) - 1)]
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        d.append(f'C{c1[0]:.0f} {c1[1]:.0f} {c2[0]:.0f} {c2[1]:.0f} {p2[0]:.0f} {p2[1]:.0f}')
    return ''.join(d)


def build():
    paths = []
    for i in range(LINES):
        # The phase drifts along x, so the ribbon twists like folded silk.
        points = [(x, centre(x) + math.cos(math.pi * i / (LINES - 1) + x / 560) * spread(x))
                  for x in range(-100, WIDTH + 101, STEP)]
        paths.append(f'<path d="{path(points)}"/>')
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {WIDTH} {HEIGHT}" '
           f'preserveAspectRatio="xMidYMid slice"><g fill="none" stroke="#6767bd" '
           f'stroke-width="1.1" stroke-opacity=".7">{"".join(paths)}</g></svg>\n')
    (ROOT / 'assets/waves.svg').write_text(svg)
    print(f'assets/waves.svg: {len(svg)} bytes')


if __name__ == '__main__':
    build()
