"""powerCON in-line coupler housing: blue power-in on one end, grey power-out
on the other, so a power-in cable can feed a power-out cable.

One printed part, a hollow rectangular bar lying flat on the bed (Z up, long
axis along X). Each end has a shallow recess for the connector flange, the
D-size cutout, and two M3 clearance holes, each with a hex pocket for an M3
nut cut into the inner (cavity) face of the end wall with the cutter from
models/m3_nut_cutter.py, which sets the pocket's size. Nothing retains the
nut: after printing, reach in through the connector hole, seat a nut in each
pocket and fix it with a drop of CA glue, then M3 x 12 countersunk screws
through the connector flange thread into them.
The NAC3MPA-1 (blue, power-in) goes on the -X end, the NAC3MPB-1 (grey,
power-out) on the +X end, both latch windows facing up.

Wiring: at `OUTER_L` = 80 the two connectors' tab tips face each other about
24 mm apart, so straight receptacles on both (each ~12 mm past its tab tip)
would meet head-on. Use receptacles on one connector and solder the other, or
solder both. `CONNECTOR_GAP` is the clear space between the connectors' rear
barrier ribs (which reach ~4 mm past the tab tips) and must stay positive.
Wire the blue connector, push it in from outside, fish the wires out of the
far hole, wire the grey connector and push it in.

See models/powercon_coupler_assembly.py for the housing with both connectors
fitted. Connector dimensions and frame come from lib/powercon.py.
"""

import functools
import operator
from collections.abc import Sequence

from build123d import (
    Align,
    Axis,
    Box,
    BuildPart,
    Color,
    Compound,
    Location,
    Locations,
    Mode,
    Part,
    Plane,
    add,
    fillet,
)

from lib.powercon import (
    FDM_HOLE_CLEARANCE,
    FLANGE_H,
    FLANGE_W,
    HOLE_XY,
    REAR_DEPTH,
    Variant,
    build_powercon_chassis,
    build_powercon_cutout,
    build_powercon_flange_recess,
)
from models import m3_nut_cutter

# --- Parameters (mm) ---------------------------------------------------------
OUTER_L = 80.0  # overall length; CONNECTOR_GAP below must stay positive
WALL_T = 3.0  # side and top/bottom walls
END_WALL_T = 6.0  # under the flange recess; the nut pockets are cut into its inner face
RIM = 3.0  # housing outer face beyond the flange on each side
RECESS_DEPTH = 1.5  # flange sits this deep in the end face
EDGE_R = 2.0  # fillet on the four long outer edges
CUTOUT_CLEARANCE = FDM_HOLE_CLEARANCE
# Connector screws: M3 countersunk through the flange and the end wall into an
# M3 hex nut glued into a pocket on the wall's inner face. The pocket is cut
# with models/m3_nut_cutter.py, which sets its size; it is open to the cavity
# with its flats top and bottom so the horizontal hole prints without steep
# overhangs.
SCREW_CLEARANCE_D = 3.4  # through the end wall (+ CUTOUT_CLEARANCE)

# --- Derived -----------------------------------------------------------------
OUTER_W = FLANGE_W + 2 * RIM  # Y, flange 26 wide sits across the housing
OUTER_H = FLANGE_H + 2 * RIM  # Z, flange 31 tall stands up
INNER_W = OUTER_W - 2 * WALL_T
INNER_H = OUTER_H - 2 * WALL_T
END_PLATE_T = END_WALL_T + RECESS_DEPTH
INNER_L = OUTER_L - 2 * END_PLATE_T
# Each connector's rear end (barrier rib tips) reaches this far past the inner
# face of its end wall; what is left between the two is free for wiring
CONNECTOR_REACH = REAR_DEPTH - END_WALL_T
CONNECTOR_GAP = INNER_L - 2 * CONNECTOR_REACH
AXIS_Z = OUTER_H / 2  # connector axis height above the bed
NUT_POCKET_DEPTH = m3_nut_cutter.HEIGHT  # into the inner face of the end wall
NUT_WALL_T = END_WALL_T - NUT_POCKET_DEPTH  # wall left between recess floor and nut

if CONNECTOR_GAP <= 0:
    raise ValueError(f"OUTER_L={OUTER_L} is too short: the connectors' rear ribs would collide")
if NUT_WALL_T < 2.0:
    raise ValueError("END_WALL_T too thin for the nut pocket plus a wall in front of it")

# --- Split variants: two U halves cut at the connector axis --------------------
# The connector flange spans both halves and its two diagonal screws land one
# in each, so the connectors tie the halves together. A lap joint along the
# side walls registers them sideways: the bottom half's outer wall portion
# rises past the split as a lip, the top half has the matching rebate.
SPLIT_Z = AXIS_Z  # split plane, through the connector axis
LAP_W = WALL_T / 2  # lip width, the outer half of the side wall
LAP_H = 2.0  # lip height above the split plane
LAP_CLEARANCE = 0.2  # rebate is this much wider and deeper than the lip

# Connector frames: origin on the recess floor (flange rear face), local +Z is
# the mating axis pointing out of the housing, local +Y (latch) points up.
PLANE_A = Plane(
    origin=(-OUTER_L / 2 + RECESS_DEPTH, 0, AXIS_Z), x_dir=(0, -1, 0), z_dir=(-1, 0, 0)
)
PLANE_B = Plane(
    origin=(OUTER_L / 2 - RECESS_DEPTH, 0, AXIS_Z), x_dir=(0, 1, 0), z_dir=(1, 0, 0)
)
HOUSING_COLOR = Color(0.25, 0.25, 0.27)


def build_nut_pockets() -> Part:
    """Cutter for the two nut pockets at one end, in the connector's frame.

    Local Z=0 is the recess floor with the end wall at -END_WALL_T <= Z <= 0.
    Each pocket is one M3 nut cutter (models/m3_nut_cutter.py) centred on a
    screw hole and seated in the wall's inner face (Z=-END_WALL_T), with a
    vertex on local +X so the flats are top and bottom. A second copy shifted
    into the cavity keeps the pocket open to it without a coincident face.
    """
    overshoot = 1.0
    cutter = m3_nut_cutter.build()
    cutter = cutter + cutter.moved(Location((0, 0, -overshoot)))
    pockets = [cutter.moved(Location((x, y, -END_WALL_T))) for x, y in HOLE_XY]
    part = functools.reduce(operator.add, pockets)
    part.label = "nut pockets"
    return part


def cut_interior_and_openings() -> None:
    """Inside an active BuildPart: hollow the bar and cut both connector ends.

    Shared by the coupler variants so the interior and the end openings stay
    identical. Call it after all solid material has been added.
    """
    cutout = build_powercon_cutout(
        END_WALL_T, clearance=CUTOUT_CLEARANCE, screw_hole_d=SCREW_CLEARANCE_D
    )
    recess = build_powercon_flange_recess(RECESS_DEPTH)
    nut_pockets = build_nut_pockets()
    with Locations((0, 0, AXIS_Z)):
        Box(INNER_L, INNER_W, INNER_H, mode=Mode.SUBTRACT)
    for plane in (PLANE_A, PLANE_B):
        add(cutout.located(plane.location), mode=Mode.SUBTRACT)
        add(recess.located(plane.location), mode=Mode.SUBTRACT)
        add(nut_pockets.located(plane.location), mode=Mode.SUBTRACT)


def split_bottom(housing: Part) -> Part:
    """Everything below SPLIT_Z plus the lap-joint lips; already in print orientation."""
    with BuildPart() as p:
        add(housing)
        Box(
            OUTER_L + 2, 10 * OUTER_W, SPLIT_Z,
            align=(Align.CENTER, Align.CENTER, Align.MIN), mode=Mode.INTERSECT,
        )
        for side in (-1, 1):
            with Locations((0, side * (OUTER_W / 2 - LAP_W), SPLIT_Z)):
                Box(
                    OUTER_L, LAP_W, LAP_H,
                    align=(Align.CENTER, Align.MIN if side > 0 else Align.MAX, Align.MIN),
                )
    part = p.part
    part.label = f"{housing.label}, split, bottom half"
    part.color = housing.color
    return part


def split_top(housing: Part) -> Part:
    """Everything above SPLIT_Z with the lap-joint rebates, flipped for printing.

    Returned open side up with the housing's top face on Z=0; use
    top_in_place() to put it back onto a bottom half.
    """
    with BuildPart() as p:
        add(housing)
        with Locations((0, 0, SPLIT_Z)):
            Box(
                OUTER_L + 2, 10 * OUTER_W, OUTER_H,
                align=(Align.CENTER, Align.CENTER, Align.MIN), mode=Mode.INTERSECT,
            )
        overshoot = 1.0
        for side in (-1, 1):
            with Locations((0, side * (OUTER_W / 2 - LAP_W - LAP_CLEARANCE), SPLIT_Z - overshoot)):
                Box(
                    OUTER_L + 2, LAP_W + LAP_CLEARANCE + overshoot, LAP_H + LAP_CLEARANCE + overshoot,
                    align=(Align.CENTER, Align.MIN if side > 0 else Align.MAX, Align.MIN),
                    mode=Mode.SUBTRACT,
                )
    part = p.part.rotate(Axis.X, 180).moved(Location((0, 0, OUTER_H)))
    part.label = f"{housing.label}, split, top half"
    part.color = housing.color
    return part


def top_in_place(top: Part) -> Part:
    """Undo split_top()'s print flip: the top half sitting on its bottom half."""
    part = top.rotate(Axis.X, 180).moved(Location((0, 0, OUTER_H)))
    part.label = top.label
    part.color = top.color
    return part


def build_assembly(
    housing: Part | Sequence[Part],
    plane_in: Plane = PLANE_A,
    planes_out: Sequence[Plane] = (PLANE_B,),
) -> Compound:
    """The housing (one part, or the halves of a split one) with one blue input
    and any number of grey outputs fitted."""
    housings = [housing] if isinstance(housing, Part) else list(housing)
    power_in = build_powercon_chassis(Variant.A).located(plane_in.location)
    power_outs = [
        build_powercon_chassis(Variant.B).located(plane.location) for plane in planes_out
    ]
    assembly = Compound(children=[*housings, power_in, *power_outs])
    assembly.label = f"{housings[0].label} assembly"
    return assembly


def build() -> Part:
    with BuildPart() as p:
        bar = Box(OUTER_L, OUTER_W, OUTER_H, align=(Align.CENTER, Align.CENTER, Align.MIN))
        fillet(bar.edges().filter_by(Axis.X), radius=EDGE_R)
        cut_interior_and_openings()

    part = p.part
    part.label = "powerCON coupler housing"
    part.color = HOUSING_COLOR
    return part
