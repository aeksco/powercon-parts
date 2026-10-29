"""powerCON in-line coupler housing with a mounting flange, for screwing to
the underside of a desk or table.

Same block as models/powercon_coupler.py (blue power-in on -X, grey power-out
on +X) with a plate along one long face that extends past both sides as ears.
Each ear has two countersunk holes for #8 / M4 flat-head wood screws.

Modelled in print orientation: the face that goes against the desk lies on
Z=0 (flat on the bed), the ears print flat, and the countersinks open upward
so they print without support. In use the part is flipped: plate against the
desk, screws driven upward, heads recessed in the countersinks, and the
connector latch windows facing down where you can reach them.
"""

from build123d import (
    Align,
    Axis,
    Box,
    BuildPart,
    BuildSketch,
    CounterSinkHole,
    Locations,
    Part,
    RectangleRounded,
    extrude,
    fillet,
)

from models.powercon_coupler import (
    EDGE_R,
    HOUSING_COLOR,
    OUTER_H,
    OUTER_L,
    OUTER_W,
    cut_interior_and_openings,
)

# --- Parameters (mm) ---------------------------------------------------------
EAR_W = 14.0  # each ear extends this far past the housing side
PLATE_T = 5.0  # mounting plate thickness at the ears
PLATE_CORNER_R = 4.0  # plan-view corner radius of the plate
JOIN_R = 2.0  # concave fillet where the housing sides meet the plate; keep it
# under (EAR_W - SCREW_CSK_D) / 2 so it stays clear of the countersinks
SCREW_HOLE_D = 4.5  # clearance for #8 / M4 wood screws
SCREW_CSK_D = 9.0  # countersink diameter for the screw head
SCREW_CSK_ANGLE = 90.0
SCREW_INSET_X = 10.0  # hole centre in from each end of the plate

# --- Derived -----------------------------------------------------------------
PLATE_W = OUTER_W + 2 * EAR_W
SCREW_PITCH_X = OUTER_L - 2 * SCREW_INSET_X  # the two holes on each ear, along the housing
SCREW_Y = OUTER_W / 2 + EAR_W / 2  # centred on each ear
SCREW_XY = tuple(
    (x, y) for x in (-SCREW_PITCH_X / 2, SCREW_PITCH_X / 2) for y in (-SCREW_Y, SCREW_Y)
)


def build() -> Part:
    with BuildPart() as p:
        bar = Box(OUTER_L, OUTER_W, OUTER_H, align=(Align.CENTER, Align.CENTER, Align.MIN))
        # Only the two long edges away from the plate get rounded; the other
        # two meet the plate
        fillet(bar.edges().filter_by(Axis.X).group_by(Axis.Z)[-1], radius=EDGE_R)
        # Mounting plate on the bed face, with the ears
        with BuildSketch():
            RectangleRounded(OUTER_L, PLATE_W, PLATE_CORNER_R)
        extrude(amount=PLATE_T)
        # Blend the inside corner where the housing sides meet the plate: the
        # two long edges at plate height on the housing's side faces
        join_edges = [
            e
            for e in p.edges().filter_by(Axis.X).filter_by_position(
                Axis.Z, PLATE_T - 0.01, PLATE_T + 0.01
            )
            if abs(abs(e.center().Y) - OUTER_W / 2) < 0.01
        ]
        fillet(join_edges, radius=JOIN_R)
        cut_interior_and_openings()
        # Countersunk screw holes through the ears, countersink away from the desk
        with Locations(*[(x, y, PLATE_T) for x, y in SCREW_XY]):
            CounterSinkHole(
                radius=SCREW_HOLE_D / 2,
                counter_sink_radius=SCREW_CSK_D / 2,
                depth=PLATE_T,
                counter_sink_angle=SCREW_CSK_ANGLE,
            )

    part = p.part
    part.label = "powerCON coupler housing, under-mount"
    part.color = HOUSING_COLOR
    return part
