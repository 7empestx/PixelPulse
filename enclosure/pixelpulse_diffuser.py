"""
PixelPulse Enclosure — Diffuser Front Panel (Transparent PETG)

Print orientation: display face DOWN on textured PEI plate.
The bed-contact surface becomes the optical diffuser surface —
the texture creates a natural frosted finish.

Bambu Lab P1S settings:
  Layer height: 0.12mm
  Nozzle temp: 235°C
  Bed temp: 80°C
  Infill: 100% (solid — this is an optical part)
  Walls: 3 perimeters
  Print face down for smooth optical surface
"""
import cadquery as cq

# ============================================================
# PARAMETERS — Must match pixelpulse_body.py dimensions
#
# These dimensions are derived from the body enclosure, which is sized
# around the Waveshare P2.5 64x32 LED panel (160 × 80 mm).
# See pixelpulse_body.py for hardware reference specs and sources.
# ============================================================

# --- Enclosure opening dimensions (from body script) ---
wall = 2.5            # mm - body wall thickness
interior_w = 161.0    # mm - body interior width
interior_h = 81.0     # mm - body interior height
outer_w = 166.0       # mm - body outer width
outer_h = 86.0        # mm - body outer height

# --- Diffuser dimensions ---
plate_thickness = 1.6 # mm - main plate thickness (100% solid)
lip_depth = 4.0       # mm - how far the lip inserts into the body
lip_thickness = 1.6   # mm - lip wall thickness

# The lip sits inside the body opening
# lip outer dimensions = interior dimensions minus clearance
fit_clearance = 0.3   # mm - clearance per side for PETG
lip_w = interior_w - 2 * fit_clearance  # mm
lip_h = interior_h - 2 * fit_clearance  # mm

# --- Snap-fit tabs ---
# Must align with snap_slot positions in body script
snap_tab_w = 7.5      # mm - slightly smaller than 8mm slot
snap_tab_h = 1.8      # mm - tab protrusion from lip surface
snap_tab_thickness = 1.5  # mm - tab thickness (Z direction)

# Tab positions: match body's snap_positions_x and snap_z
# Body has slots at Y = ±outer_h/4, X = ±outer_w/4, at Z = outer_depth - 8mm
# On the diffuser, tabs are on the lip, at matching relative positions
tab_positions_x = [-outer_w / 4, outer_w / 4]

# Corner radius (match body)
corner_r = 3.0        # mm

# ============================================================
# MODEL
# ============================================================

# Build the diffuser with the optical face at Z=0 (printed face-down).
# The lip extends in +Z direction (away from print bed).

# Step 1: Main flat plate — full outer dimensions
# This is the visible diffuser surface
plate = (
    cq.Workplane("XY")
    .box(outer_w, outer_h, plate_thickness, centered=(True, True, False))
    .edges("|Z")
    .fillet(corner_r)
)

# Step 2: Insertion lip — extends from the back of the plate
# This is a hollow frame that fits inside the body opening
lip_outer = (
    cq.Workplane("XY")
    .workplane(offset=plate_thickness)
    .box(lip_w, lip_h, lip_depth, centered=(True, True, False))
)
lip_inner = (
    cq.Workplane("XY")
    .workplane(offset=plate_thickness - 1)
    .box(lip_w - 2 * lip_thickness, lip_h - 2 * lip_thickness,
         lip_depth + 2, centered=(True, True, False))
)
lip = lip_outer.cut(lip_inner)
diffuser = plate.union(lip)

# Step 3: Snap-fit tabs on the lip sides (top and bottom Y-direction)
# Tabs protrude outward from the lip to engage with body slots
for tx in tab_positions_x:
    for ty_sign in [-1, 1]:
        # Tab on the Y-face of the lip
        ty = ty_sign * (lip_h / 2)
        tab = (
            cq.Workplane("XY")
            .workplane(offset=plate_thickness + lip_depth - snap_tab_thickness - 1.0)
            .pushPoints([(tx, ty)])
            .rect(snap_tab_w, snap_tab_h * 2)
            .extrude(snap_tab_thickness)
        )
        diffuser = diffuser.union(tab)

# Step 4: Add a small lead-in chamfer on the lip edges for easier insertion
# This helps guide the diffuser into the body opening
try:
    diffuser = (
        diffuser.edges(
            cq.selectors.NearestToPointSelector(
                (0, 0, plate_thickness + lip_depth)
            )
        ).chamfer(0.4)
    )
except Exception:
    pass  # Skip if geometry is too complex for chamfer

# ============================================================
# EXPORT
# ============================================================
result = diffuser

cq.exporters.export(result, "enclosure/pixelpulse_diffuser.stl")
print(f"Exported: enclosure/pixelpulse_diffuser.stl")
print(f"Plate: {outer_w:.1f} x {outer_h:.1f} x {plate_thickness:.1f} mm")
print(f"Lip: {lip_w:.1f} x {lip_h:.1f} x {lip_depth:.1f} mm")
print(f"Total depth: {plate_thickness + lip_depth:.1f} mm")
