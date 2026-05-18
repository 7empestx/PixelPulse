"""
PixelPulse Enclosure — Main Body (Black PETG)

Print orientation: back face down (Z=0 is the back wall)
No supports needed.

Bambu Lab P1S settings:
  Layer height: 0.20mm
  Nozzle temp: 240°C
  Bed temp: 80°C
  Infill: 20% gyroid
  Walls: 3 perimeters
"""
import cadquery as cq

# ============================================================
# PARAMETERS — Edit these to customize the model
#
# Hardware reference specs:
#   Waveshare P2.5 64x32: 160 × 80 × ~14.7 mm, M3 holes ~4mm inset
#     https://www.waveshare.com/rgb-matrix-p2.5-64x32.htm
#     https://www.waveshare.com/wiki/RGB-Matrix-P2.5-64x32
#   ESP32-DevKitC V4: 54.4 × 27.9 mm, 25.4mm pin pitch
#     https://docs.espressif.com/projects/esp-dev-kits/en/latest/esp32/esp32-devkitc/user_guide.html
#   RGB Matrix Adapter Board (E): 70 × 60 mm (user-measured), M2.5 holes
#     https://seengreat.com/wiki/186/rgb-matrix-adapter-board-e
# ============================================================

# --- LED Panel (Waveshare P2.5 64x32) ---
# Official: 160 × 80 × ~14.7 mm, M3 mounting holes ~4mm inset from edges
# Source: waveshare.com/rgb-matrix-p2.5-64x32.htm
panel_w = 160.0       # mm - panel width (official: 160mm)
panel_h = 80.0        # mm - panel height (official: 80mm)
panel_depth = 14.5    # mm - panel PCB thickness (official: ~14.7mm, reduced for measured fit)
panel_back = 6.0      # mm - back-side component clearance beyond PCB

# Panel mounting holes: M3, inset ~4mm from each edge
# Official: M3 holes at ~152 × 72mm spacing (4mm inset from 160 × 80 edges)
panel_hole_spacing_x = 152.0  # mm - horizontal hole-to-hole (official: ~152mm)
panel_hole_spacing_y = 72.0   # mm - vertical hole-to-hole (official: ~72mm)

# --- ESP32 + Adapter Board stack ---
# ESP32-DevKitC V4: 54.4 × 27.9 mm, 25.4mm pin pitch (espressif.com)
# RGB Matrix Adapter Board (E): 70 × 60 mm (user-measured), M2.5 holes (seengreat.com)
adapter_w = 70.0      # mm - board width (measured: 70mm)
adapter_h = 60.0      # mm - board height (measured: 60mm)
electronics_depth = 16.0  # mm - combined height of adapter + ESP32 + clearance

# --- Enclosure structure ---
wall = 2.5            # mm - wall thickness (PETG structural minimum)
corner_r = 3.0        # mm - outer corner fillet radius

# Diffuser standoff: air gap between panel LED face and front opening
diffuser_standoff = 4.0  # mm - space for diffuser + air gap

# --- Derived overall dimensions ---
# Interior needs to fit: diffuser_standoff + panel + electronics
interior_w = panel_w + 1.0       # mm - 0.5mm clearance per side
interior_h = panel_h + 1.0       # mm - 0.5mm clearance per side
interior_depth = (diffuser_standoff + panel_depth + panel_back
                  + electronics_depth)  # total internal depth

outer_w = interior_w + 2 * wall  # ~165mm
outer_h = interior_h + 2 * wall  # ~85mm
outer_depth = interior_depth + wall  # back wall only (front is open)

# --- Panel ledge ---
# Ledge sits inside the box, diffuser_standoff from the front opening.
# The panel rests on this ledge, LED face toward the front.
ledge_width = 3.0     # mm - how far the ledge protrudes inward
ledge_thickness = 2.0 # mm - ledge shelf thickness

# --- Mounting ---
screw_d = 3.2         # mm - M3 clearance hole diameter (standard M3 clearance)
boss_od = 7.0         # mm - screw boss outer diameter
boss_h = 5.0          # mm - screw boss height (extends from ledge)

# Adapter board standoffs (M2.5)
standoff_d = 2.7      # mm - M2.5 clearance hole (standard M2.5 clearance)
standoff_od = 6.0     # mm - standoff outer diameter
standoff_h = 5.0      # mm - standoff height from back wall

# Adapter standoff positions (relative to center, user-measured from board)
adapter_standoff_positions = [
    (-30.0, -25.0),
    (30.0, -25.0),
    (-30.0, 25.0),
    (30.0, 25.0),
]

# --- Rear cutouts ---
# Adapter Board (E) has USB-C 5V/4A and DC-044 5V/8A power inputs
usbc_w = 12.0         # mm - USB-C opening width (standard USB-C with tolerance)
usbc_h = 7.0          # mm - USB-C opening height (with tolerance)
usbc_y_offset = -20.0 # mm - USB-C position offset from center (toward bottom)

dc_barrel_d = 12.0    # mm - DC barrel jack hole diameter (DC-044 standard)
dc_barrel_y_offset = 20.0  # mm - DC jack offset from center (toward top)

# Ventilation slots
vent_count = 6        # number of vent slots
vent_w = 25.0         # mm - slot length
vent_h = 2.0          # mm - slot width
vent_spacing = 5.0    # mm - center-to-center spacing
vent_x_offset = 20.0  # mm - horizontal offset from center for vent array

# --- Snap-fit slots (for diffuser attachment) ---
snap_slot_w = 8.0     # mm - slot width
snap_slot_h = 2.0     # mm - slot height (depth into wall)
snap_slot_depth = 3.0 # mm - how deep the slot goes into the wall

# --- Feet ---
foot_d = 8.0          # mm - foot diameter
foot_h = 3.0          # mm - foot height
foot_inset = 12.0     # mm - distance from corner to foot center

# --- Tolerances ---
fit_clearance = 0.3   # mm - general fit clearance for PETG

# ============================================================
# MODEL
# ============================================================

# Note: We build the enclosure with the BACK wall at Z=0 (print face down).
# The front opening faces +Z direction.

# Step 1: Outer shell — box with rounded vertical edges
outer = (
    cq.Workplane("XY")
    .box(outer_w, outer_h, outer_depth, centered=(True, True, False))
    .edges("|Z")
    .fillet(corner_r)
)

# Step 2: Hollow out — cut interior from the front (+Z face)
# Leave back wall intact (wall thickness at Z=0)
inner_cut = (
    cq.Workplane("XY")
    .workplane(offset=wall)  # start above back wall
    .box(interior_w, interior_h, interior_depth + 1, centered=(True, True, False))
)
body = outer.cut(inner_cut)

# Step 3: Panel support ledge
# The ledge is at Z = wall + interior_depth - diffuser_standoff - ledge_thickness
# = distance from back wall to where panel LED face sits, minus ledge thickness
ledge_z = wall + electronics_depth + panel_back + panel_depth
# The ledge is a frame around the interior at that Z height
ledge_outer = (
    cq.Workplane("XY")
    .workplane(offset=ledge_z)
    .box(interior_w + 2, interior_h + 2, ledge_thickness,  # +2mm to overlap into walls
         centered=(True, True, False))
)
ledge_inner = (
    cq.Workplane("XY")
    .workplane(offset=ledge_z)
    .box(interior_w - 2 * ledge_width, interior_h - 2 * ledge_width,
         ledge_thickness + 1, centered=(True, True, False))
)
ledge = ledge_outer.cut(ledge_inner)
body = body.union(ledge)

# Step 4: M3 screw bosses for panel mounting
# Bosses extend downward from the ledge into the electronics bay
# Panel holes are at the ledge Z level
boss_z_start = ledge_z - boss_h
for dx in [-panel_hole_spacing_x / 2, panel_hole_spacing_x / 2]:
    for dy in [-panel_hole_spacing_y / 2, panel_hole_spacing_y / 2]:
        boss = (
            cq.Workplane("XY")
            .workplane(offset=boss_z_start)
            .pushPoints([(dx, dy)])
            .circle(boss_od / 2)
            .extrude(boss_h)
        )
        hole = (
            cq.Workplane("XY")
            .workplane(offset=boss_z_start - 1)
            .pushPoints([(dx, dy)])
            .circle(screw_d / 2)
            .extrude(boss_h + ledge_thickness + 2)
        )
        body = body.union(boss).cut(hole)

# Step 5: Adapter board standoff posts on back wall
for pos in adapter_standoff_positions:
    standoff = (
        cq.Workplane("XY")
        .workplane(offset=wall)
        .pushPoints([pos])
        .circle(standoff_od / 2)
        .extrude(standoff_h)
    )
    s_hole = (
        cq.Workplane("XY")
        .workplane(offset=wall - 1)
        .pushPoints([pos])
        .circle(standoff_d / 2)
        .extrude(standoff_h + 2)
    )
    body = body.union(standoff).cut(s_hole)

# Step 6: Rear cutouts (through back wall at Z=0)

# USB-C opening
usbc_cut = (
    cq.Workplane("XY")
    .workplane(offset=-1)
    .pushPoints([(0, usbc_y_offset)])
    .rect(usbc_w, usbc_h)
    .extrude(wall + 2)
)
body = body.cut(usbc_cut)

# DC barrel jack opening
dc_cut = (
    cq.Workplane("XY")
    .workplane(offset=-1)
    .pushPoints([(0, dc_barrel_y_offset)])
    .circle(dc_barrel_d / 2)
    .extrude(wall + 2)
)
body = body.cut(dc_cut)

# Ventilation slots — array on the back wall, offset to one side
vent_start_y = -(vent_count - 1) * vent_spacing / 2
for i in range(vent_count):
    vy = vent_start_y + i * vent_spacing
    vent = (
        cq.Workplane("XY")
        .workplane(offset=-1)
        .pushPoints([(vent_x_offset, vy)])
        .slot2D(vent_w, vent_h)
        .extrude(wall + 2)
    )
    body = body.cut(vent)

# Also add vents on the other side (symmetric)
for i in range(vent_count):
    vy = vent_start_y + i * vent_spacing
    vent = (
        cq.Workplane("XY")
        .workplane(offset=-1)
        .pushPoints([(-vent_x_offset, vy)])
        .slot2D(vent_w, vent_h)
        .extrude(wall + 2)
    )
    body = body.cut(vent)

# Step 7: Snap-fit slots for diffuser (near front opening, in the side walls)
# Two slots on each long side (top and bottom walls)
snap_z = outer_depth - 8.0  # 8mm from front edge
snap_positions_x = [-outer_w / 4, outer_w / 4]  # two per side
snap_positions_y = [-outer_h / 4, outer_h / 4]

# Slots on top and bottom walls (Y-direction walls)
for sx in snap_positions_x:
    for sy_sign in [-1, 1]:
        sy = sy_sign * (outer_h / 2)
        slot = (
            cq.Workplane("XY")
            .workplane(offset=snap_z)
            .pushPoints([(sx, sy)])
            .rect(snap_slot_w, snap_slot_depth * 2)
            .extrude(snap_slot_h)
        )
        body = body.cut(slot)

# Step 8: Feet on back face
foot_positions = [
    (-outer_w / 2 + foot_inset, -outer_h / 2 + foot_inset),
    (outer_w / 2 - foot_inset, -outer_h / 2 + foot_inset),
    (-outer_w / 2 + foot_inset, outer_h / 2 - foot_inset),
    (outer_w / 2 - foot_inset, outer_h / 2 - foot_inset),
]
for fp in foot_positions:
    foot = (
        cq.Workplane("XY")
        .workplane(offset=wall)  # start inside back wall so geometry fuses
        .pushPoints([fp])
        .circle(foot_d / 2)
        .extrude(-(wall + foot_h))  # through back wall + foot height
    )
    body = body.union(foot)

# Step 9: Chamfer bottom edges (easier to print than fillets at bed contact)
# Skip this if it causes issues — chamfers on complex geometry can fail
try:
    body = body.edges(
        cq.selectors.NearestToPointSelector((0, 0, -foot_h))
    ).chamfer(0.5)
except Exception:
    pass  # Skip chamfer if geometry is too complex

# ============================================================
# FUSE — Merge all solids into one manifold mesh
# CadQuery .union() on tangent faces can silently produce
# a compound of separate solids. Force-fuse them here.
# ============================================================
solids = body.solids().vals()
if len(solids) > 1:
    print(f"Fusing {len(solids)} separate solids into one...")
    fused = solids[0]
    for s in solids[1:]:
        fused = fused.fuse(s)
    body = cq.Workplane("XY").newObject([fused])

# ============================================================
# EXPORT
# ============================================================
result = body

cq.exporters.export(result, "enclosure/pixelpulse_body.stl")
print(f"Exported: enclosure/pixelpulse_body.stl")
print(f"Outer dimensions: {outer_w:.1f} x {outer_h:.1f} x {outer_depth:.1f} mm")
print(f"Interior: {interior_w:.1f} x {interior_h:.1f} x {interior_depth:.1f} mm")
