"""powerCON distribution box: one blue power-in on the +X end feeding three
grey power-out receptacles in a row on the top face, with a screw-on lid on
the bottom for wiring and service.

Two printed parts: this housing (open on the bottom) and the lid in
models/powercon_distro_1in_3out_lid.py. Both lie flat on the bed. The housing
prints open side down, so its top wall bridges the cavity; the lid prints
with its outer face up so the countersinks need no support.

The input sits in a recess on the end exactly as in the coupler. The outputs
sit in recesses on the top face with their latch windows toward -Y; the top
wall is thickened inside by a pad over the output zone so their screws get
6 mm of plastic. Four corner bosses take M3 screws for the lid. The -X end is
closed. If this later gets the under-desk ear plate on the lid, the outputs
face down in use.

Wiring, done with the lid off: flag (90 degree) fastons on all four
connectors. The input's L and N tabs face the side channels, so their wires
run down the sides of the box past the output rears; PE drops to the floor.
Daisy-chain L, N and PE along the row of outputs.
"""

from build123d import (
    Align,
    Axis,
    Box,
    BuildPart,
    CounterSinkHole,
    Cylinder,
    Locations,
    Mode,
    Part,
    Plane,
    add,
    fillet,
)

from lib.powercon import (
    BARRIER_WALL_H,
    BODY_D,
    FLANGE_H,
    FLANGE_W,
    RECESS_CLEARANCE,
    TAB_TIP_DEPTH,
    build_powercon_cutout,
    build_powercon_flange_recess,
)
from models.powercon_coupler import (
    CUTOUT_CLEARANCE,
    EDGE_R,
    END_PLATE_T,
    END_WALL_T,
    HOUSING_COLOR,
    RECESS_DEPTH,
    RIM,
    WALL_T,
)

# --- Parameters (mm) ---------------------------------------------------------
SCREW_PILOT_D = 2.5  # connector screws: M3 self-taps into this (+FDM clearance)
N_OUT = 3
OUTPUT_PITCH = 31.0  # centre to centre along the box; flanges are 26 wide here
INPUT_TERMINAL_L = 4.0  # flag terminal beyond the input's tab tips, along the box
OUTPUT_TERMINAL_L = 5.0  # flag terminal beyond the outputs' tab tips, toward the lid
OUTPUT_CLEARANCE = 3.0  # between those terminals and the lid
WIRE_GAP = 4.0  # input's terminal ends to the first output's body
WIRE_CHANNEL = 8.0  # free width beside the output rears, each side, for wiring
END_RIM = 3.0  # closed end wall, also the rim past the last output recess
PAD_MARGIN = 2.0  # pad extends this far past the output recesses
LID_T = WALL_T  # lid plate thickness; it replaces the bottom wall
BOSS = 6.0  # square corner bosses the lid screws go into
BOSS_H = 10.0  # boss height above the lid; stays below the connector bodies
LID_SCREW_D = 3.4  # M3 clearance through the lid
LID_SCREW_CSK_D = 6.0  # countersink in the lid's outer face, 90 degrees
LID_SCREW_PILOT_D = 2.5  # M3 self-taps into this (+FDM clearance) in the bosses

# --- Derived -----------------------------------------------------------------
INNER_W = BARRIER_WALL_H + 2 * WIRE_CHANNEL
OUTER_W = max(INNER_W + 2 * WALL_T, FLANGE_H + 2 * RECESS_CLEARANCE + 2 * RIM)
INNER_W = OUTER_W - 2 * WALL_T
INPUT_REACH = TAB_TIP_DEPTH - END_WALL_T + INPUT_TERMINAL_L  # past the end wall
OUTPUT_DEPTH = TAB_TIP_DEPTH - END_WALL_T + OUTPUT_TERMINAL_L  # below the pad
OUTER_H = max(FLANGE_H + 2 * RIM, END_PLATE_T + OUTPUT_DEPTH + OUTPUT_CLEARANCE + LID_T)
AXIS_Z = OUTER_H / 2  # input axis, centred in the cavity
PAD_T = END_PLATE_T - WALL_T

OUTER_L = (
    END_PLATE_T
    + INPUT_REACH
    + WIRE_GAP
    + BODY_D / 2
    + (N_OUT - 1) * OUTPUT_PITCH
    + FLANGE_W / 2
    + RECESS_CLEARANCE
    + END_RIM
)
CAVITY_X0 = -OUTER_L / 2 + END_RIM  # closed end, inner face
CAVITY_X1 = OUTER_L / 2 - END_PLATE_T  # input end, inner face
INNER_L = CAVITY_X1 - CAVITY_X0
CAVITY_X = (CAVITY_X0 + CAVITY_X1) / 2
# Outputs counted from the input end
FIRST_OUT_X = CAVITY_X1 - INPUT_REACH - WIRE_GAP - BODY_D / 2
OUTPUT_XS = tuple(FIRST_OUT_X - i * OUTPUT_PITCH for i in range(N_OUT))
PAD_HALF_L = FLANGE_W / 2 + RECESS_CLEARANCE + PAD_MARGIN
PAD_L = OUTPUT_XS[0] - OUTPUT_XS[-1] + 2 * PAD_HALF_L
PAD_X = (OUTPUT_XS[0] + OUTPUT_XS[-1]) / 2
# Lid screw bosses in the four inside corners of the cavity
BOSS_XY = tuple(
    (x, y)
    for x in (CAVITY_X0 + BOSS / 2, CAVITY_X1 - BOSS / 2)
    for y in (-(INNER_W / 2 - BOSS / 2), INNER_W / 2 - BOSS / 2)
)

# Connector frames: origin on the recess floor, local +Z is the mating axis
# pointing out of the housing, local +Y is the latch window
PLANE_IN = Plane(
    origin=(OUTER_L / 2 - RECESS_DEPTH, 0, AXIS_Z), x_dir=(0, 1, 0), z_dir=(1, 0, 0)
)  # latch up
PLANES_OUT = tuple(
    Plane(origin=(x, 0, OUTER_H - RECESS_DEPTH), x_dir=(-1, 0, 0), z_dir=(0, 0, 1))
    for x in OUTPUT_XS
)  # latch toward -Y


def build() -> Part:
    """The housing: everything above the lid plane at Z=LID_T, open underneath."""
    cutout = build_powercon_cutout(
        END_WALL_T, clearance=CUTOUT_CLEARANCE, screw_hole_d=SCREW_PILOT_D
    )
    recess = build_powercon_flange_recess(RECESS_DEPTH)
    overshoot = 1.0

    with BuildPart() as p:
        with Locations((0, 0, LID_T)):
            body = Box(
                OUTER_L, OUTER_W, OUTER_H - LID_T, align=(Align.CENTER, Align.CENTER, Align.MIN)
            )
        fillet(body.edges().filter_by(Axis.X).group_by(Axis.Z)[-1], radius=EDGE_R)
        # Cavity, open at the bottom
        with Locations((CAVITY_X, 0, LID_T - overshoot)):
            Box(
                INNER_L,
                INNER_W,
                OUTER_H - WALL_T - LID_T + overshoot,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
                mode=Mode.SUBTRACT,
            )
        # Pad under the top wall over the output zone, for the screws to bite into
        with Locations((PAD_X, 0, OUTER_H - WALL_T - PAD_T / 2)):
            Box(PAD_L, INNER_W, PAD_T)
        # Lid screw bosses with blind pilot holes
        with Locations(*[(x, y, LID_T) for x, y in BOSS_XY]):
            Box(BOSS, BOSS, BOSS_H, align=(Align.CENTER, Align.CENTER, Align.MIN))
        with Locations(*[(x, y, LID_T - overshoot) for x, y in BOSS_XY]):
            Cylinder(
                (LID_SCREW_PILOT_D + CUTOUT_CLEARANCE) / 2,
                BOSS_H,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
                mode=Mode.SUBTRACT,
            )
        for plane in (PLANE_IN, *PLANES_OUT):
            add(cutout.located(plane.location), mode=Mode.SUBTRACT)
            add(recess.located(plane.location), mode=Mode.SUBTRACT)

    part = p.part
    part.label = "powerCON 1-in 3-out distro housing"
    part.color = HOUSING_COLOR
    return part


def build_lid() -> Part:
    """The lid in its print orientation: outer face up, countersinks on top."""
    with BuildPart() as p:
        plate = Box(OUTER_L, OUTER_W, LID_T, align=(Align.CENTER, Align.CENTER, Align.MIN))
        fillet(plate.edges().filter_by(Axis.X).group_by(Axis.Z)[-1], radius=EDGE_R)
        with Locations(*[(x, y, LID_T) for x, y in BOSS_XY]):
            CounterSinkHole(
                radius=LID_SCREW_D / 2,
                counter_sink_radius=LID_SCREW_CSK_D / 2,
                depth=LID_T,
                counter_sink_angle=90,
            )
    part = p.part
    part.label = "powerCON 1-in 3-out distro lid"
    part.color = HOUSING_COLOR
    return part


def lid_in_place() -> Part:
    """The lid flipped onto the housing: outer face on Z=0, screws into the bosses."""
    from build123d import Location

    return build_lid().rotate(Axis.X, 180).moved(Location((0, 0, LID_T)))
