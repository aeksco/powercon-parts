"""Render a shape to a shaded isometric PNG.

A tiny z-buffer rasterizer in numpy: no OpenGL or display needed, so it works
headless and in CI. Lighting is two-sided, so face orientation doesn't matter.
"""

from pathlib import Path

import numpy as np
from PIL import Image

TOLERANCE = 0.05  # mm, tessellation chord deviation
ANGULAR_TOLERANCE = 0.2  # rad
IMAGE_SIZE = 800  # px, output width and height
SUPERSAMPLE = 3  # render at this multiple, then downscale for anti-aliasing
MARGIN = 0.08  # fraction of the image left blank on each side
BASE_COLOR = np.array([92, 148, 217], dtype=float)
EDGE_COLOR = np.array([30, 45, 70], dtype=float)
BACKGROUND = (255, 255, 255)
AMBIENT = 0.35
EDGE_ANGLE_DEG = 30.0  # normal change across a pixel that counts as an edge

# True isometric: camera looks from (1, -1, 1) toward the origin (front-right-top)
VIEW_DIR = np.array([1.0, -1.0, 1.0]) / np.sqrt(3)
LIGHT_DIR = np.array([0.3, -0.8, 1.0]) / np.linalg.norm([0.3, -0.8, 1.0])


def _camera_basis() -> np.ndarray:
    """Rows: screen-right, screen-up, toward-camera."""
    right = np.cross([0.0, 0.0, 1.0], VIEW_DIR)
    right /= np.linalg.norm(right)
    up = np.cross(VIEW_DIR, right)
    return np.stack([right, up, VIEW_DIR])


def render_isometric(shape, path: Path) -> None:
    verts, tris = shape.tessellate(TOLERANCE, ANGULAR_TOLERANCE)
    pts = np.array([(v.X, v.Y, v.Z) for v in verts])
    faces = pts[np.array(tris)]

    # Two-sided Lambert shading: flip normals that point away from the camera
    normals = np.cross(faces[:, 1] - faces[:, 0], faces[:, 2] - faces[:, 0])
    normals /= np.linalg.norm(normals, axis=1, keepdims=True) + 1e-12
    normals *= np.where(normals @ VIEW_DIR < 0, -1.0, 1.0)[:, None]
    shade = AMBIENT + (1 - AMBIENT) * np.clip(normals @ LIGHT_DIR, 0.0, 1.0)

    # Project to pixel coordinates; depth grows toward the camera
    size = IMAGE_SIZE * SUPERSAMPLE
    cam = faces @ _camera_basis().T
    lo = cam[..., :2].reshape(-1, 2).min(axis=0)
    hi = cam[..., :2].reshape(-1, 2).max(axis=0)
    scale = size * (1 - 2 * MARGIN) / (hi - lo).max()
    offset = size / 2 - (lo + hi) / 2 * scale
    xy = cam[..., :2] * scale + offset
    xy[..., 1] = size - xy[..., 1]  # image rows grow downward
    depth = cam[..., 2]

    zbuf = np.full((size, size), -np.inf)
    face_id = np.full((size, size), -1)
    for i in range(len(faces)):
        (x0, y0), (x1, y1), (x2, y2) = xy[i]
        area = (x1 - x0) * (y2 - y0) - (x2 - x0) * (y1 - y0)
        if abs(area) < 1e-9:
            continue
        cmin = max(int(np.floor(min(x0, x1, x2))), 0)
        cmax = min(int(np.ceil(max(x0, x1, x2))), size - 1)
        rmin = max(int(np.floor(min(y0, y1, y2))), 0)
        rmax = min(int(np.ceil(max(y0, y1, y2))), size - 1)
        if cmin > cmax or rmin > rmax:
            continue
        px, py = np.meshgrid(
            np.arange(cmin, cmax + 1) + 0.5, np.arange(rmin, rmax + 1) + 0.5
        )
        w0 = ((x1 - px) * (y2 - py) - (x2 - px) * (y1 - py)) / area
        w1 = ((x2 - px) * (y0 - py) - (x0 - px) * (y2 - py)) / area
        w2 = 1 - w0 - w1
        inside = (w0 >= 0) & (w1 >= 0) & (w2 >= 0)
        z = w0 * depth[i, 0] + w1 * depth[i, 1] + w2 * depth[i, 2]
        region = zbuf[rmin : rmax + 1, cmin : cmax + 1]
        closer = inside & (z > region)
        region[closer] = z[closer]
        face_id[rmin : rmax + 1, cmin : cmax + 1][closer] = i

    covered = face_id >= 0
    img = np.empty((size, size, 3))
    img[:] = BACKGROUND
    img[covered] = shade[face_id[covered], None] * BASE_COLOR

    # Outline silhouettes and sharp creases where neighbouring pixels' normals differ
    n = np.zeros((size, size, 3))
    n[covered] = normals[face_id[covered]]
    cos_limit = np.cos(np.radians(EDGE_ANGLE_DEG))
    edge = np.zeros((size, size), dtype=bool)
    for axis in (0, 1):
        a = [slice(None)] * 2
        b = [slice(None)] * 2
        a[axis], b[axis] = slice(1, None), slice(None, -1)
        a, b = tuple(a), tuple(b)
        diff = (covered[a] != covered[b]) | (
            covered[a] & covered[b] & ((n[a] * n[b]).sum(axis=-1) < cos_limit)
        )
        edge[a] |= diff
        edge[b] |= diff
    img[edge] = EDGE_COLOR

    image = Image.fromarray(img.clip(0, 255).astype(np.uint8))
    image.resize((IMAGE_SIZE, IMAGE_SIZE), Image.LANCZOS).save(path)
