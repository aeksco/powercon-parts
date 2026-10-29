"""Under-mount powerCON coupler with both connectors fitted, for checking fit
and looks. Not a part to print: export models/powercon_coupler_undermount.py.
"""

from build123d import Compound

from models.powercon_coupler import build_assembly
from models.powercon_coupler_undermount import build as build_housing


def build() -> Compound:
    return build_assembly(build_housing())
