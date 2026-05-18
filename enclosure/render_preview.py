"""
Simple STL preview renderer using trimesh only (no pyrender/OpenGL needed).
Generates multi-view PNG previews using trimesh's built-in scene rendering.
"""
import sys
import os
import numpy as np
import trimesh
from PIL import Image, ImageDraw, ImageFont


def load_mesh(path):
    tm = trimesh.load(path, force="mesh")
    if not hasattr(tm, "vertices") or len(tm.vertices) == 0:
        print(f"ERROR: STL file contains no geometry: {path}")
        sys.exit(1)
    tm.fix_normals()
    return tm


def render_view(tm, resolution=(800, 800), angles=(np.pi/6, -np.pi/4)):
    """Render a mesh from given angles using trimesh's scene rendering."""
    scene = trimesh.Scene(tm)

    # Create a PNG in memory using trimesh's built-in renderer
    try:
        png_data = scene.save_image(resolution=resolution, visible=False)
        from io import BytesIO
        img = Image.open(BytesIO(png_data))
        return img
    except Exception as e:
        print(f"Warning: trimesh scene render failed ({e}), using projection fallback")
        return render_projection(tm, resolution)


def render_projection(tm, resolution=(800, 800)):
    """Fallback: render orthographic projection as a simple line drawing."""
    w, h = resolution
    img = Image.new("RGB", (w, h), "white")
    draw = ImageDraw.Draw(img)

    bounds = tm.bounds
    extent = bounds[1] - bounds[0]
    center = (bounds[0] + bounds[1]) / 2

    # Scale to fit
    scale = min(w, h) * 0.8 / max(extent[0], extent[1])

    # Project vertices (isometric-ish: rotate 30 degrees)
    verts = tm.vertices - center
    cos30 = np.cos(np.pi / 6)
    sin30 = np.sin(np.pi / 6)

    # Simple isometric projection
    px = verts[:, 0] * cos30 - verts[:, 1] * sin30
    py = -verts[:, 2] + (verts[:, 0] * sin30 + verts[:, 1] * cos30) * 0.5

    px = px * scale + w / 2
    py = py * scale + h / 2

    # Draw edges
    edges = tm.edges_unique
    for e in edges[:5000]:  # limit for performance
        x0, y0 = px[e[0]], py[e[0]]
        x1, y1 = px[e[1]], py[e[1]]
        draw.line([(x0, y0), (x1, y1)], fill="#4470a0", width=1)

    return img


def get_font(size=14):
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/TTF/DejaVuSans.ttf",
    ]
    for path in candidates:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                continue
    return ImageFont.load_default()


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 render_preview.py <stl_file> [output.png]")
        sys.exit(1)

    stl_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else stl_path.replace(".stl", "_preview.png")

    tm = load_mesh(stl_path)
    extents = tm.bounding_box.extents
    print(f"Model: {stl_path}")
    print(f"Bounding box: {extents[0]:.1f} x {extents[1]:.1f} x {extents[2]:.1f} mm")
    print(f"Triangles: {len(tm.faces)}")
    print(f"Watertight: {tm.is_watertight}")

    img = render_view(tm, resolution=(900, 750))

    # Add title and dimensions footer
    canvas = Image.new("RGB", (img.width, img.height + 80), "white")
    canvas.paste(img, (0, 40))
    draw = ImageDraw.Draw(canvas)

    title_font = get_font(18)
    info_font = get_font(13)

    title = os.path.splitext(os.path.basename(stl_path))[0].replace("_", " ").title()
    draw.text((canvas.width // 2, 12), title, fill="black", font=title_font, anchor="mt")

    info = f"Bounding box: {extents[0]:.1f} x {extents[1]:.1f} x {extents[2]:.1f} mm"
    try:
        vol = abs(tm.volume)
        info += f"  |  Volume: ~{vol:.0f} mm\u00b3"
    except Exception:
        pass
    draw.text((canvas.width // 2, canvas.height - 12), info, fill="gray", font=info_font, anchor="mb")

    canvas.save(output_path)
    print(f"Preview saved: {output_path} ({os.path.getsize(output_path)} bytes)")


if __name__ == "__main__":
    main()
