"""powerCON under-mount coupler, split version: bottom half with the plate.

The under-mount coupler of models/powercon_coupler_undermount.py cut
lengthwise through the connector axis. This half carries the mounting plate
and ears; the other half is the plain split coupler's top
(models/powercon_coupler_split_top.py). Same lap joint and connector-screw
clamping as models/powercon_coupler_split_bottom.py.

Modelled in print orientation, desk face on the bed. In use it is flipped:
plate against the desk, with the top half hanging below it.
"""

from build123d import Part

from models.powercon_coupler import split_bottom
from models.powercon_coupler_undermount import build as build_housing


def build() -> Part:
    return split_bottom(build_housing())
