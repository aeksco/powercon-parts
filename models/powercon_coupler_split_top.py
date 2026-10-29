"""powerCON in-line coupler, split version: top half.

The upper half of models/powercon_coupler.py with the lap-joint rebates that
take the bottom half's lips. Shared by the plain split coupler
(models/powercon_coupler_split_bottom.py) and the under-mount split coupler
(models/powercon_coupler_undermount_split_bottom.py).

Modelled in print orientation: open side up with the housing's top face on
the bed. In use it is flipped onto the bottom half.
"""

from build123d import Part

from models.powercon_coupler import build as build_housing
from models.powercon_coupler import split_top


def build() -> Part:
    return split_top(build_housing())
