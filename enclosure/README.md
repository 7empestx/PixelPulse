# PixelPulse Enclosure — 3D Printable

Two-piece snap-fit enclosure for the PixelPulse 64x32 LED matrix display.

## Parts

| Part | File | Material | Description |
|------|------|----------|-------------|
| Main Body | `pixelpulse_body.stl` | Black PETG | Holds LED panel, ESP32, and adapter board |
| Diffuser | `pixelpulse_diffuser.stl` | Transparent PETG | Front panel, snaps into body |

## Bill of Materials

- 1x Waveshare P2.5 64x32 HUB75 LED panel (160x80mm)
- 1x ESP32-DevKitC V4
- 1x RGB Matrix Adapter Board (E) for ESP32
- 4x M3x8mm screws (panel mounting)
- 4x M2.5x6mm screws (adapter board mounting, optional)
- 1x HUB75 IDC ribbon cable (included with adapter board)
- USB-C cable for power

## Print Settings (Bambu Lab P1S)

### Body — Black PETG

| Setting | Value |
|---------|-------|
| Layer height | 0.20mm |
| Nozzle temp | 240°C |
| Bed temp | 80°C |
| Infill | 20% gyroid |
| Walls | 3 perimeters |
| Supports | None |
| Orientation | Back face down |
| Plate | Smooth PEI |

### Diffuser — Transparent PETG

| Setting | Value |
|---------|-------|
| Layer height | 0.12mm |
| Nozzle temp | 235°C |
| Bed temp | 80°C |
| Infill | 100% (solid) |
| Walls | 3 perimeters |
| Supports | None |
| Orientation | Display face down |
| Plate | Textured PEI |

The textured PEI plate imprints a frosted finish on the diffuser's display face — this naturally diffuses the LED light without post-processing.

## Dimensions

| Measurement | Value |
|-------------|-------|
| Body exterior | 166 x 86 x 43.5 mm |
| Body interior | 161 x 81 x 38 mm |
| Diffuser plate | 166 x 86 x 1.6 mm |
| Diffuser total depth | 5.6 mm (plate + insertion lip) |
| Wall thickness | 2.5 mm |

## Hardware Reference Dimensions

Official specs for the hardware this enclosure is designed around. CadQuery parameters in the `.py` scripts are derived from these values (with clearance adjustments for 3D printing).

| Component | Dimension | Value | Source |
|-----------|-----------|-------|--------|
| Waveshare P2.5 64x32 | Face | 160 × 80 mm | [waveshare.com](https://www.waveshare.com/rgb-matrix-p2.5-64x32.htm) |
| Waveshare P2.5 64x32 | Depth | ~14.7 mm | [waveshare.com](https://www.waveshare.com/wiki/RGB-Matrix-P2.5-64x32) |
| Waveshare P2.5 64x32 | Mounting holes | M3, 152 × 72 mm spacing | [waveshare.com](https://www.waveshare.com/wiki/RGB-Matrix-P2.5-64x32) |
| ESP32-DevKitC V4 | PCB | 54.4 × 27.9 mm | [espressif.com](https://docs.espressif.com/projects/esp-dev-kits/en/latest/esp32/esp32-devkitc/user_guide.html) |
| ESP32-DevKitC V4 | Pin pitch | 25.4 mm | [espressif.com](https://docs.espressif.com/projects/esp-dev-kits/en/latest/esp32/esp32-devkitc/user_guide.html) |
| Adapter Board (E) | Board | 70 × 60 mm | User-measured |
| Adapter Board (E) | Mounting | M2.5 holes | [seengreat.com](https://seengreat.com/wiki/186/rgb-matrix-adapter-board-e) |
| Adapter Board (E) | Power | USB-C 5V/4A, DC-044 5V/8A | [seengreat.com](https://seengreat.com/wiki/186/rgb-matrix-adapter-board-e) |

## Assembly

1. **Mount the LED panel** into the body. The panel sits on the internal ledge with LEDs facing the front opening. Secure with 4x M3 screws through the screw bosses.

2. **Connect the adapter board** to the panel via the HUB75 IDC ribbon cable. Optionally secure the adapter board to the standoff posts with M2.5 screws.

3. **Plug the ESP32** into the adapter board headers.

4. **Route the USB-C cable** through the rear cutout for power.

5. **Snap the diffuser** into the front of the body. The insertion lip fits inside the body opening, and the snap tabs click into the side slots.

## Customizing

Both CadQuery scripts (`pixelpulse_body.py`, `pixelpulse_diffuser.py`) have all dimensions as named parameters at the top of the file. To regenerate STLs after editing:

```bash
pip install cadquery  # if not installed
python3 enclosure/pixelpulse_body.py
python3 enclosure/pixelpulse_diffuser.py
```

Key parameters to adjust after test-fitting:
- `fit_clearance` — increase if parts are too tight (default 0.3mm for PETG)
- `wall` — wall thickness (default 2.5mm)
- `diffuser_standoff` — air gap between LED face and diffuser (default 4mm)
- `usbc_y_offset` / `dc_barrel_y_offset` — adjust if connector positions don't align

## Previews

Generate preview images:
```bash
python3 enclosure/render_preview.py enclosure/pixelpulse_body.stl enclosure/preview_body.png
python3 enclosure/render_preview.py enclosure/pixelpulse_diffuser.stl enclosure/preview_diffuser.png
```
