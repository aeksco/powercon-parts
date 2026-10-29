# CLAUDE.md

This is a **build123d starter project** for parametric, 3D-printable parts. The
scaffolding (uv, Makefile, exporter) is done. Your job is usually just to
write or edit a model in `models/`. Don't re-create the scaffolding.

## Quick start

```sh
make setup              # once: uv sync (Python 3.12 venv in .venv)
make                    # export example -> build/{stl,step,obj,png}/example.*
make MODEL=<name>       # export models/<name>.py
make all-models         # export every model
make list               # list models
make clean              # delete build/
make view MODEL=<name>  # push to OCP viewer (optional; needs viewer running)
```

Outputs land in `build/<type>/<name>.<type>` (gitignored), grouped by type:
`build/stl/` for slicers, `build/step/` for CAD, `build/obj/` for mesh tools,
`build/png/` isometric renders. Look at the PNG to check the shape visually.
Every model's outputs depend on all of `models/*.py` and `lib/*.py`, so a
change to a housing also rebuilds the assembly that imports it.

## Layout

```
models/<name>.py     one file per part; must define build() -> Part
lib/<component>.py   shared builders for purchased components (e.g. lib/powercon.py);
                     models and assemblies import these, `make` does not export them
scripts/export.py    generic exporter; imports models.<name>, calls build(), writes STL+STEP+OBJ+PNG
scripts/render.py    shaded isometric PNG render (numpy z-buffer, headless)
Makefile             thin wrapper around the exporter
pyproject.toml       deps managed by uv (build123d, numpy, pillow; ocp-vscode as dev dep)
```

## Making a new part

1. Copy `models/example.py` to `models/<name>.py` (or edit it in place for a one-off).
2. Keep **all dimensions as named constants at the top, in mm**. No magic numbers in geometry code.
3. Keep `build()` pure: no I/O, no `show()`, return the shape (`part.part` for `BuildPart`).
4. Run `make MODEL=<name>`. The exporter fails if the shape is invalid and prints
   volume and bounding box. Check those against what you intended.
5. To rename the project, edit `name` in `pyproject.toml`.

## Component library (lib/)

- `lib/powercon.py`: Neutrik powerCON 20 A chassis receptacles, NAC3MPA-1
  (blue, power-in) and NAC3MPB-1 (grey/white, power-out), dimensioned from
  Neutrik's drawings and STEP files. `build_powercon_chassis(Variant.A|B)`
  returns the connector; `build_powercon_cutout(panel_thickness)` returns the
  D-size cutout and `build_powercon_flange_recess(depth)` a flush pocket for
  the flange, both to subtract from a panel at the connector's location.
  Frame: flange rear face on Z=0, +Z toward the plug, latch window at +Y.
  `models/powercon_nac3mpa.py` and `models/powercon_nac3mpb.py` are the
  exportable wrappers.
- Assemblies: place a connector with `build_powercon_chassis(v).located(plane.location)`
  where `plane` has `z_dir` along the mating axis pointing out of the panel and
  `x_dir` chosen so local +Y (latch) points where you want it. Define the plane
  once in the housing model and reuse it for the cutters and the connector.
  `models/powercon_coupler.py` (printable housing) and
  `models/powercon_coupler_assembly.py` (housing + connectors, a Compound) are
  the pattern to copy. Variants of a housing reuse its `cut_interior_and_openings()`
  and `build_assembly()` rather than duplicating geometry; see
  `models/powercon_coupler_undermount.py`.
- Split variants: `split_bottom()` / `split_top()` / `top_in_place()` in
  `models/powercon_coupler.py` cut a coupler housing at the connector axis
  into two U halves with a lap joint along the side walls, each returned in
  print orientation. `models/powercon_coupler_split_*.py` and
  `models/powercon_coupler_undermount_split_*.py` are the thin wrappers; the
  top half is shared by both.
- `models/m3_nut_cutter.py` is a filleted hex prism the size of an M3 nut.
  The couplers subtract it for their nut pockets, so its constants set the
  pocket size; it also exports on its own as a slicer negative volume.
- Model parts in print orientation (flat face on Z=0) and say in the docstring
  how the part sits in use if that differs.
- These connector models are reference geometry for fit checks and assemblies,
  not parts to print (0.5 mm tabs, 0.8 mm barriers).

## build123d notes and gotchas

- Use the builder API (`with BuildPart() as p:`) and return `p.part`.
- Z is up. Use `Align.MIN` on Z to sit a box on the XY plane.
- `Mode.SUBTRACT` cuts holes; give cutters extra length so they pass fully through.
- Fillet/chamfer **early**, on simple geometry, before unioning more features.
  Filleting edges at junctions of merged solids often raises
  `Failed creating a fillet`; use a smaller radius, `max_fillet()`, or restructure.
- Docs: https://build123d.readthedocs.io
- Verify output programmatically (volume, `bounding_box()`, `is_valid`) rather than assuming.

## 3D-printing defaults to design for (FDM)

- Min wall ~1.2 mm; holes print slightly small, so add ~0.2 mm clearance for fits.
- Avoid overhangs > 45° or orient the part to avoid them; prefer a flat face on the bed.
- Export units are mm.

## Dependencies

Add with `uv add <pkg>`; never use bare `pip`. Python is pinned to 3.12 in
`.python-version` because the OCP (OpenCascade) wheels lag newer Pythons.
