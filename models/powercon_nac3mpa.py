"""Neutrik NAC3MPA-1: blue powerCON 20 A power-in chassis receptacle.

Reference geometry for assemblies, not a part to print. Dimensions and the
coordinate frame live in lib/powercon.py (flange rear face on Z=0, +Z toward
the plug).
"""

from build123d import Part

from lib.powercon import Variant, build_powercon_chassis

VARIANT = Variant.A  # blue, power-in, side keyway on the left (front view)


def build() -> Part:
    return build_powercon_chassis(VARIANT)
