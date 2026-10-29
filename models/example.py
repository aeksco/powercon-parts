"""Example model: a parametric mounting bracket. Replace with your own part.

Contract (required by scripts/export.py):
  - define `build() -> Part` (or a Compound/Shape) with no side effects
  - keep all dimensions as named constants at the top, in millimetres
"""

from build123d import (
    Align,
    Axis,
    Box,
    BuildPart,
    Cylinder,
    GridLocations,
    Locations,
    Mode,
    Part,
    fillet,
)

# --- Parameters (mm) ---------------------------------------------------------
WIDTH = 60.0
DEPTH = 40.0
THICKNESS = 4.0
WALL_HEIGHT = 25.0
HOLE_DIAMETER = 5.0
HOLE_SPACING_X = 40.0
HOLE_SPACING_Y = 20.0
FILLET_RADIUS = 2.0


def build() -> Part:
    with BuildPart() as part:
        # Base plate
        base = Box(WIDTH, DEPTH, THICKNESS, align=(Align.CENTER, Align.CENTER, Align.MIN))
        # Round the vertical corner edges (do this before adding more geometry)
        fillet(base.edges().filter_by(Axis.Z), radius=FILLET_RADIUS)
        # Back wall
        with Locations((0, -DEPTH / 2 + THICKNESS / 2, 0)):
            Box(
                WIDTH,
                THICKNESS,
                WALL_HEIGHT,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
            )
        # Mounting holes through the base plate
        with GridLocations(HOLE_SPACING_X, HOLE_SPACING_Y, 2, 2):
            Cylinder(
                HOLE_DIAMETER / 2,
                THICKNESS * 3,
                mode=Mode.SUBTRACT,
            )
    return part.part
