"""M3 nut cutter: a hex prism the size of an M3 nut, for subtracting nut
pockets in a slicer (as a negative volume) or in other CAD.

Sits flat on Z=0 with the hex in the XY plane. The six vertical edges (the
hex's vertices) carry a small fillet so the pocket's corners do not come out
as sharp slits.
"""

import math

from build123d import Axis, BuildPart, BuildSketch, Part, RegularPolygon, extrude, fillet

# --- Parameters (mm) ---------------------------------------------------------
ACROSS_FLATS = 5.55  # flat to flat, not vertex to vertex
HEIGHT = 2.3
VERTEX_R = 0.35  # fillet on each of the six vertical edges

# --- Derived -----------------------------------------------------------------
ACROSS_CORNERS = ACROSS_FLATS / math.cos(math.radians(30))  # 6.41 before the fillets


def build() -> Part:
    with BuildPart() as p:
        with BuildSketch():
            # minor radius = apothem = half the across-flats size
            RegularPolygon(ACROSS_FLATS / 2, 6, major_radius=False)
        extrude(amount=HEIGHT)
        fillet(p.edges().filter_by(Axis.Z), radius=VERTEX_R)

    part = p.part
    part.label = "M3 nut cutter"
    return part
