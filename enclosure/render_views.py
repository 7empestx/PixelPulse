"""
Multi-view PNG renderer for the PixelPulse enclosure STLs.

Generates schematic-style views (isometric, front, back, side, exploded)
suitable for sharing with a 3D-print designer.

Usage:
    python3 enclosure/render_views.py
"""
import os
import numpy as np
import trimesh
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

HERE = os.path.dirname(os.path.abspath(__file__))
BODY_STL = os.path.join(HERE, "pixelpulse_body.stl")
DIFFUSER_STL = os.path.join(HERE, "pixelpulse_diffuser.stl")

BODY_COLOR = "#2a2a2a"
DIFFUSER_COLOR = "#a8d0e6"
EDGE_COLOR = "#111111"


def load(path):
    m = trimesh.load(path, force="mesh")
    m.fix_normals()
    return m


def setup_axes(ax, meshes, elev, azim, title, pad=8):
    all_v = np.vstack([m.vertices for m in meshes])
    mins = all_v.min(axis=0) - pad
    maxs = all_v.max(axis=0) + pad
    center = (mins + maxs) / 2
    span = (maxs - mins).max() / 2
    ax.set_xlim(center[0] - span, center[0] + span)
    ax.set_ylim(center[1] - span, center[1] + span)
    ax.set_zlim(center[2] - span, center[2] + span)
    ax.set_box_aspect((1, 1, 1))
    ax.view_init(elev=elev, azim=azim)
    ax.set_xlabel("X (mm)", fontsize=8)
    ax.set_ylabel("Y (mm)", fontsize=8)
    ax.set_zlabel("Z (mm)", fontsize=8)
    ax.tick_params(labelsize=7)
    ax.set_title(title, fontsize=11, pad=10)


def draw_mesh(ax, mesh, color, alpha=1.0, edge=True, offset=(0, 0, 0)):
    verts = mesh.vertices + np.array(offset)
    tris = verts[mesh.faces]
    coll = Poly3DCollection(
        tris,
        facecolors=color,
        edgecolors=EDGE_COLOR if edge else "none",
        linewidths=0.05 if edge else 0,
        alpha=alpha,
    )
    ax.add_collection3d(coll)


def annotate(ax, text, fontsize=8):
    ax.text2D(
        0.02, 0.98, text, transform=ax.transAxes,
        fontsize=fontsize, va="top", ha="left",
        bbox=dict(boxstyle="round,pad=0.4", facecolor="white",
                  edgecolor="#999", alpha=0.85),
    )


def render_single(mesh, title, dims_text, out_path):
    """Render one mesh as a 2x2 grid: iso, front, back, side."""
    fig = plt.figure(figsize=(12, 10))
    fig.suptitle(title, fontsize=14, fontweight="bold", y=0.98)

    views = [
        ("Isometric", 25, 35),
        ("Front (LED face)", 0, 0),
        ("Back (connectors)", 0, 180),
        ("Side (cross-section view)", 0, 90),
    ]
    for i, (name, elev, azim) in enumerate(views, start=1):
        ax = fig.add_subplot(2, 2, i, projection="3d")
        draw_mesh(ax, mesh, BODY_COLOR if "body" in title.lower() else DIFFUSER_COLOR)
        setup_axes(ax, [mesh], elev, azim, name)

    fig.text(0.5, 0.02, dims_text, ha="center", fontsize=10, color="#555")
    fig.tight_layout(rect=[0, 0.03, 1, 0.96])
    fig.savefig(out_path, dpi=130, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"  saved: {out_path}")


def render_exploded(body, diffuser, out_path):
    """Show body + diffuser separated along Z (front-back axis)."""
    fig = plt.figure(figsize=(14, 10))
    fig.suptitle("PixelPulse Enclosure — Exploded Assembly",
                 fontsize=14, fontweight="bold", y=0.98)

    body_depth = body.bounding_box.extents[2]
    explode_z = body_depth * 0.5

    views = [
        ("Exploded — Isometric", 22, 40),
        ("Exploded — Side", 0, 90),
    ]
    for i, (name, elev, azim) in enumerate(views, start=1):
        ax = fig.add_subplot(1, 2, i, projection="3d")
        draw_mesh(ax, body, BODY_COLOR)
        draw_mesh(ax, diffuser, DIFFUSER_COLOR, alpha=0.85,
                  offset=(0, 0, explode_z))
        setup_axes(ax, [body, diffuser], elev, azim, name, pad=12)

    legend_handles = [
        Patch(facecolor=BODY_COLOR, edgecolor="black",
              label="Body (Black PETG)"),
        Patch(facecolor=DIFFUSER_COLOR, edgecolor="black",
              label="Diffuser (Transparent PETG)"),
    ]
    fig.legend(handles=legend_handles, loc="lower center",
               ncol=2, fontsize=10, frameon=False)

    note = (
        "Assembly order (front to back):  "
        "Diffuser → 4mm air gap → LED panel (160x80mm) → "
        "Adapter board + ESP32 → Back wall with USB-C / DC / vents"
    )
    fig.text(0.5, 0.03, note, ha="center", fontsize=9,
             color="#555", style="italic")
    fig.tight_layout(rect=[0, 0.06, 1, 0.96])
    fig.savefig(out_path, dpi=130, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"  saved: {out_path}")


def render_cross_section(body, out_path):
    """Cut the body in half along its long axis to show internal geometry.

    Uses trimesh.slice_plane (requires shapely) so the cut face is capped,
    giving a clean filled cross-section.
    """
    center = body.bounding_box.centroid
    sliced = body.slice_plane(
        plane_origin=center,
        plane_normal=[0, 1, 0],
        cap=True,
    )

    fig = plt.figure(figsize=(14, 7))
    fig.suptitle("PixelPulse Body — Cross-Section (cut along centerline)",
                 fontsize=13, fontweight="bold", y=0.96)

    views = [
        ("Cross-section — Isometric", 18, 35),
        ("Cross-section — Side", 0, 90),
    ]
    for i, (name, elev, azim) in enumerate(views, start=1):
        ax = fig.add_subplot(1, 2, i, projection="3d")
        draw_mesh(ax, sliced, BODY_COLOR, edge=True)
        setup_axes(ax, [body], elev, azim, name, pad=8)

    note = (
        "Internal features visible:  "
        "panel mounting ledge with M3 bosses (inner shelf)  ·  "
        "M2.5 standoffs for adapter board (back wall)  ·  "
        "interior depth ~38mm"
    )
    fig.text(0.5, 0.03, note, ha="center", fontsize=9,
             color="#555", style="italic")
    fig.tight_layout(rect=[0, 0.05, 1, 0.94])
    fig.savefig(out_path, dpi=130, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"  saved: {out_path}")


def main():
    print("Loading STL files...")
    body = load(BODY_STL)
    diffuser = load(DIFFUSER_STL)
    print(f"  body:     {body.bounding_box.extents.round(1).tolist()} mm, "
          f"{len(body.faces)} tris")
    print(f"  diffuser: {diffuser.bounding_box.extents.round(1).tolist()} mm, "
          f"{len(diffuser.faces)} tris")

    body_dims = (
        f"Exterior: {body.bounding_box.extents[0]:.1f} × "
        f"{body.bounding_box.extents[1]:.1f} × "
        f"{body.bounding_box.extents[2]:.1f} mm   |   "
        f"Wall thickness: 2.5 mm   |   Material: Black PETG"
    )
    diffuser_dims = (
        f"Plate: {diffuser.bounding_box.extents[0]:.1f} × "
        f"{diffuser.bounding_box.extents[1]:.1f} × "
        f"{diffuser.bounding_box.extents[2]:.1f} mm   |   "
        f"Material: Transparent PETG (textured PEI for frosted finish)"
    )

    print("\nRendering body views...")
    render_single(body, "PixelPulse Body — Multi-View",
                  body_dims, os.path.join(HERE, "views_body.png"))

    print("\nRendering diffuser views...")
    render_single(diffuser, "PixelPulse Diffuser — Multi-View",
                  diffuser_dims, os.path.join(HERE, "views_diffuser.png"))

    print("\nRendering exploded assembly...")
    render_exploded(body, diffuser,
                    os.path.join(HERE, "views_exploded.png"))

    print("\nRendering cross-section...")
    try:
        render_cross_section(body,
                             os.path.join(HERE, "views_cross_section.png"))
    except Exception as e:
        print(f"  cross-section failed: {e}")

    print("\nDone.")


if __name__ == "__main__":
    main()
