"""Split under-mount coupler: plate half, the shared top half in place, and
both connectors fitted. For fit checks; print the halves separately.
"""

from build123d import Compound

from models.powercon_coupler import build_assembly, top_in_place
from models.powercon_coupler_split_top import build as build_top
from models.powercon_coupler_undermount_split_bottom import build as build_bottom


def build() -> Compound:
    return build_assembly([build_bottom(), top_in_place(build_top())])
