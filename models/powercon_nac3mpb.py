"""Neutrik NAC3MPB-1: grey/white powerCON 20 A power-out chassis receptacle.

Reference geometry for assemblies, not a part to print. Dimensions and the
coordinate frame live in lib/powercon.py (flange rear face on Z=0, +Z toward
the plug).
"""

from build123d import Part

from lib.powercon import Variant, build_powercon_chassis

VARIANT = Variant.B  # grey/white, power-out, side keyway on the right (front view)


def build() -> Part:
    return build_powercon_chassis(VARIANT)
