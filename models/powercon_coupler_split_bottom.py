"""powerCON in-line coupler, split version: bottom half.

The coupler of models/powercon_coupler.py cut lengthwise through the
connector axis into two U-shaped halves, so each prints open side up with no
bridges or supports and the wiring and nut gluing are done in the open. This
is the lower half: floor, the lower half of each side and end wall, and the
lower connector screw hole and nut pocket at each end. A lip along the outer
half of each side wall rises past the split and seats in the top half's
rebate (models/powercon_coupler_split_top.py). The connector flanges span
both halves and their diagonal screws land one in each, so fitting the
connectors clamps the halves together.
"""

from build123d import Part

from models.powercon_coupler import build as build_housing
from models.powercon_coupler import split_bottom


def build() -> Part:
    return split_bottom(build_housing())
