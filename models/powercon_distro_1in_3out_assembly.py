"""1-in 3-out powerCON distro box with the lid on and all four connectors
fitted, for checking fit and looks. Not a part to print: export
models/powercon_distro_1in_3out.py and models/powercon_distro_1in_3out_lid.py.
"""

from build123d import Compound

from models.powercon_coupler import build_assembly
from models.powercon_distro_1in_3out import PLANE_IN, PLANES_OUT, lid_in_place
from models.powercon_distro_1in_3out import build as build_housing


def build() -> Compound:
    assembly = build_assembly(build_housing(), PLANE_IN, PLANES_OUT)
    return Compound(children=[*assembly.children, lid_in_place()], label=assembly.label)
