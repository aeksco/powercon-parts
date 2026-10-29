"""powerCON coupler with both connectors fitted, for checking fit and looks.

Not a part to print: export models/powercon_coupler.py for the housing. The
STEP written from this model carries the housing and the two connectors as
separate coloured solids.
"""

from build123d import Compound

from models.powercon_coupler import build as build_housing
from models.powercon_coupler import build_assembly


def build() -> Compound:
    return build_assembly(build_housing())
