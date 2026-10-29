"""Lid for the 1-in 3-out powerCON distro box, printed outer face up.

Four M3 flat-head screws (M3x12) through the countersinks into the housing's
corner bosses. Geometry lives in models/powercon_distro_1in_3out.py.
"""

from build123d import Part

from models.powercon_distro_1in_3out import build_lid


def build() -> Part:
    return build_lid()
