"""Neutrik powerCON 20 A chassis connectors with the standard D-size mounting.

Covers the two keyed variants:
  - NAC3MPA-1  blue,  "A" type, power-in  (mates with NAC3FCA cable connector)
  - NAC3MPB-1  grey/white, "B" type, power-out (mates with NAC3FCB)
Neutrik calls these "male" (pins inside); they are the panel receptacles.

Dimensions come from Neutrik drawings ST-NAC3MPA-1 and 20001218 (NAC3MPB-1)
and the official STEP files. Where the drawing and STEP disagree by 0.1-0.2 mm
the drawing wins. The two variants are geometrically identical except for the
side keyway in the mating cavity: A has it on the left, B on the right, as
seen from the front with the latch window at 12 o'clock.

Coordinate frame (same as Neutrik's STEP):
  - Z is the mating axis. +Z points out of the panel toward the cable plug.
  - The flange's rear face (the face that touches the panel) lies on Z=0, so a
    panel of thickness t occupies -t <= Z <= 0 when the part is front-mounted.
  - X is right and Y is up when looking at the front of the connector with the
    latch window at the top. The two mounting holes are top-left and
    bottom-right in that view.

All dimensions in mm.
"""

from enum import Enum

from build123d import (
    Align,
    BuildPart,
    BuildSketch,
    Circle,
    Color,
    CounterSinkHole,
    Cylinder,
    Locations,
    Mode,
    Part,
    Plane,
    Rectangle,
    RectangleRounded,
    extrude,
)

# --- D-size flange ----------------------------------------------------------
FLANGE_W = 26.0  # X
FLANGE_H = 31.0  # Y
FLANGE_T = 4.5  # Z, rear face at Z=0, front face at Z=FLANGE_T
FLANGE_CORNER_R = 3.5
HOLE_PITCH_X = 19.0  # mounting hole pattern
HOLE_PITCH_Y = 24.0
HOLE_D = 3.4  # M3 clearance, countersunk from the front
HOLE_CSK_D = 6.0  # countersink diameter at the front face
HOLE_CSK_ANGLE = 90.0
# Only two of the four corners have holes: top-left and bottom-right (front view).
HOLE_XY = ((-HOLE_PITCH_X / 2, HOLE_PITCH_Y / 2), (HOLE_PITCH_X / 2, -HOLE_PITCH_Y / 2))

# --- Round body: front collar in front of the flange, body through the panel --
COLLAR_D = 23.6
COLLAR_H = 2.5  # proud of the flange front face
BODY_D = 23.6  # passes through the panel cutout; Neutrik gives 23.6 (0/-0.3)
BODY_L = 19.1  # from the flange rear face to the back of the round body
FRONT_Z = FLANGE_T + COLLAR_H  # Z of the front face
OVERALL_L = 37.3  # drawing: 37.2 (A) / 37.3 (B)
REAR_DEPTH = OVERALL_L - COLLAR_H - FLANGE_T  # 30.3, everything behind the panel face

# --- Mating cavity (where the cable connector's nose goes) --------------------
CAVITY_D = 17.8  # outer wall of the annular cavity
BOSS_D = 12.3  # centre insulator boss carrying the contacts
BOSS_HOLE_D = 5.7  # bore in the centre of the boss
CAVITY_FLOOR_Z = -16.0  # cavity floor, below the flange rear face
GROOVE_D = 20.0  # the latch and key grooves reach out to this diameter
LATCH_GROOVE_W = 4.2  # latch window at 12 o'clock (+Y), both variants
KEY_GROOVE_W = 3.3  # side keyway, -X for A, +X for B

# --- Rear: insulating barriers and 3/16" flat-tab terminals ----------------
REAR_Z = -BODY_L  # back face of the round body; everything below hangs off it
BARRIER_L = OVERALL_L - COLLAR_H - FLANGE_T - BODY_L  # 11.2
BARRIER_T = 0.8
BARRIER_WALL_X = 3.65  # the two walls of the "H", centre X
BARRIER_WALL_H = 17.5  # Y extent of the walls
BARRIER_BAR_Y = 4.15  # four short bars sticking out sideways from the walls
BARRIER_BAR_X0 = 4.05  # bars run from the wall's outer face...
BARRIER_BAR_X1 = 8.75  # ...to here
TAB_W = 4.8  # 3/16" FASTON tab
TAB_T = 0.5
TAB_L = 7.3
TAB_LN_X = 5.6  # L at +X, N at -X (Neutrik rear view: L left, N right), blade width along Y
TAB_PE_Y = -3.55  # PE tab, bottom centre, blade width along X
TAB_TIP_DEPTH = BODY_L + TAB_L  # 26.4, tab tips measured from the panel face

# --- Panel cutout (Neutrik "panel cut out, rear side") ----------------------
CUTOUT_D = 24.0  # Neutrik: >= 23.8 for NAC3MP*-1, 24 +/-0.1 for powerCON XX
CUTOUT_SCREW_D = 3.2  # >= 3.2 clearance for M3
FDM_HOLE_CLEARANCE = 0.2  # printed holes come out small; add this by default
RECESS_CLEARANCE = 0.3  # per side, for a flange recess in a printed panel

BLUE = Color(0.10, 0.33, 0.72)
GREY = Color(0.78, 0.78, 0.76)


class Variant(Enum):
    """powerCON keying. The value is the X direction of the side keyway."""

    A = -1  # blue, power-in, NAC3MPA-1
    B = +1  # grey/white, power-out, NAC3MPB-1

    @property
    def part_number(self) -> str:
        return {Variant.A: "NAC3MPA-1", Variant.B: "NAC3MPB-1"}[self]

    @property
    def color(self) -> Color:
        return {Variant.A: BLUE, Variant.B: GREY}[self]


def build_powercon_chassis(variant: Variant) -> Part:
    """Chassis connector in the frame described in the module docstring."""
    key_x = variant.value
    cavity_depth = FRONT_Z - CAVITY_FLOOR_Z

    with BuildPart() as p:
        # Flange, rear face on Z=0
        with BuildSketch():
            RectangleRounded(FLANGE_W, FLANGE_H, FLANGE_CORNER_R)
        extrude(amount=FLANGE_T)

        # Collar proud of the flange, and the body going back through the panel
        with BuildSketch(Plane.XY.offset(FLANGE_T)):
            Circle(COLLAR_D / 2)
        extrude(amount=COLLAR_H)
        with BuildSketch():
            Circle(BODY_D / 2)
        extrude(amount=-BODY_L)

        # Countersunk mounting holes, drilled from the front face of the flange
        with Locations(*[(x, y, FLANGE_T) for x, y in HOLE_XY]):
            CounterSinkHole(
                radius=HOLE_D / 2,
                counter_sink_radius=HOLE_CSK_D / 2,
                depth=FLANGE_T,
                counter_sink_angle=HOLE_CSK_ANGLE,
            )

        # Annular mating cavity with the latch window (+Y) and the side keyway,
        # leaving the centre boss standing
        with BuildSketch(Plane.XY.offset(FRONT_Z)):
            Circle(CAVITY_D / 2)
            Rectangle(LATCH_GROOVE_W, GROOVE_D / 2, align=(Align.CENTER, Align.MIN))
            Rectangle(
                GROOVE_D / 2,
                KEY_GROOVE_W,
                align=(Align.MIN if key_x > 0 else Align.MAX, Align.CENTER),
            )
            Circle(GROOVE_D / 2, mode=Mode.INTERSECT)
            Circle(BOSS_D / 2, mode=Mode.SUBTRACT)
        extrude(amount=-cavity_depth, mode=Mode.SUBTRACT)

        # Bore down the centre of the boss
        with Locations((0, 0, FRONT_Z)):
            Cylinder(
                BOSS_HOLE_D / 2,
                cavity_depth,
                align=(Align.CENTER, Align.CENTER, Align.MAX),
                mode=Mode.SUBTRACT,
            )

        # Rear insulating barriers: an "H" with four short side bars
        with BuildSketch(Plane.XY.offset(REAR_Z)):
            with Locations((BARRIER_WALL_X, 0), (-BARRIER_WALL_X, 0)):
                Rectangle(BARRIER_T, BARRIER_WALL_H)
            Rectangle(2 * BARRIER_BAR_X0, BARRIER_T)
            bar_x = (BARRIER_BAR_X0 + BARRIER_BAR_X1) / 2
            with Locations(
                (bar_x, BARRIER_BAR_Y),
                (bar_x, -BARRIER_BAR_Y),
                (-bar_x, BARRIER_BAR_Y),
                (-bar_x, -BARRIER_BAR_Y),
            ):
                Rectangle(BARRIER_BAR_X1 - BARRIER_BAR_X0, BARRIER_T)
        extrude(amount=-BARRIER_L)

        # Flat-tab terminals: L and N at the sides, PE at the bottom
        with BuildSketch(Plane.XY.offset(REAR_Z)):
            with Locations((TAB_LN_X, 0), (-TAB_LN_X, 0)):
                Rectangle(TAB_T, TAB_W)
            with Locations((0, TAB_PE_Y)):
                Rectangle(TAB_W, TAB_T)
        extrude(amount=-TAB_L)

    part = p.part
    part.label = variant.part_number
    part.color = variant.color
    return part


def build_powercon_cutout(
    panel_thickness: float,
    clearance: float = FDM_HOLE_CLEARANCE,
    screw_hole_d: float = CUTOUT_SCREW_D,
    all_four_holes: bool = False,
) -> Part:
    """Cutter for the D-size panel opening, in the connector's frame.

    Subtract it from a panel that occupies -panel_thickness <= Z <= 0 at the
    connector's location. `clearance` is added to every hole diameter (0.2 mm
    suits FDM; use 0 for machined panels). The connector only uses two
    diagonal holes; `all_four_holes` drills the other diagonal too so the
    connector can be fitted either way up.
    """
    overshoot = 1.0  # cutter passes clear of both panel faces
    length = panel_thickness + 2 * overshoot
    holes = HOLE_XY
    if all_four_holes:
        holes = holes + tuple((-x, y) for x, y in HOLE_XY)
    with BuildPart() as p:
        with Locations((0, 0, overshoot)):
            Cylinder(
                (CUTOUT_D + clearance) / 2,
                length,
                align=(Align.CENTER, Align.CENTER, Align.MAX),
            )
        with Locations(*[(x, y, overshoot) for x, y in holes]):
            Cylinder(
                (screw_hole_d + clearance) / 2,
                length,
                align=(Align.CENTER, Align.CENTER, Align.MAX),
            )
    part = p.part
    part.label = "powerCON D-size cutout"
    return part


def build_powercon_flange_recess(depth: float, clearance: float = RECESS_CLEARANCE) -> Part:
    """Cutter for a shallow pocket that locates the flange flush in a panel face.

    In the connector's frame the pocket occupies 0 <= Z <= depth, i.e. the
    panel's outer face is at Z=depth and the flange's rear face lands on Z=0.
    Subtract it together with `build_powercon_cutout` from the same location.
    """
    overshoot = 1.0
    with BuildPart() as p:
        with BuildSketch():
            RectangleRounded(
                FLANGE_W + 2 * clearance,
                FLANGE_H + 2 * clearance,
                FLANGE_CORNER_R + clearance,
            )
        extrude(amount=depth + overshoot)
    part = p.part
    part.label = "powerCON flange recess"
    return part
