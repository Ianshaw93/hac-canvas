"""
Generate a synthetic plot plan for the hac-canvas demo.

Outputs: Northgate_Plot_Plan.pdf in the same folder.

The plant is fictional. Coordinates and source IDs match the worked example
in `Smiths/hac-canvas/` notes. Re-run after editing inputs:
    python generate_plot_plan.py
"""

import math
from pathlib import Path

from reportlab.lib.pagesizes import A3, landscape
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas as rl_canvas

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

OUT_PDF = Path(__file__).parent / "Northgate_Plot_Plan.pdf"

PAGE_W, PAGE_H = landscape(A3)        # 420 x 297 mm in pts
SCALE_M_TO_PT = 6.5 * mm              # 1 m drawn as 6.5 mm  -> 1:154 (fits page nicely)

# SW corner of the plant on the page
ORIGIN_X = 35 * mm
ORIGIN_Y = 70 * mm                    # leaves bottom ~55 mm for title block


def x(m): return ORIGIN_X + m * SCALE_M_TO_PT
def y(m): return ORIGIN_Y + m * SCALE_M_TO_PT


# ---------------------------------------------------------------------------
# Drawing helpers
# ---------------------------------------------------------------------------

def _hatch_along_edge(c, x1, y1, x2, y2, tick_len_pt, spacing_m=2):
    """Draw 45° diagonal hatch ticks pointing into the compound.

    Edge must be traversed counter-clockwise around the compound perimeter
    so that rotating the along-edge unit vector +90° yields the inward normal.
    """
    dx, dy = x2 - x1, y2 - y1
    L = math.hypot(dx, dy)
    if L == 0:
        return
    ux, uy = dx / L, dy / L                  # unit along edge
    nx, ny = -uy, ux                         # 90° CCW = inward
    spacing_pt = spacing_m * SCALE_M_TO_PT
    n_ticks = int(L // spacing_pt)
    half = math.sqrt(0.5) * tick_len_pt
    for i in range(n_ticks):
        t = (i + 0.5) * spacing_pt
        bx, by = x1 + ux * t, y1 + uy * t
        ex = bx + ux * half + nx * half
        ey = by + uy * half + ny * half
        c.line(bx, by, ex, ey)


def draw_compound_fence(c):
    c.setLineWidth(1.0)
    c.setStrokeColorRGB(0, 0, 0)
    c.rect(x(0), y(0), 50 * SCALE_M_TO_PT, 30 * SCALE_M_TO_PT,
           stroke=1, fill=0)

    # Uniform diagonal hatching, traversing perimeter counter-clockwise
    c.setLineWidth(0.3)
    tick = 2 * mm
    _hatch_along_edge(c, x(0),  y(0),  x(50), y(0),  tick)   # bottom W→E
    _hatch_along_edge(c, x(50), y(0),  x(50), y(30), tick)   # right  S→N
    _hatch_along_edge(c, x(50), y(30), x(0),  y(30), tick)   # top    E→W
    _hatch_along_edge(c, x(0),  y(30), x(0),  y(0),  tick)   # left   N→S


def equipment_circle(c, cx_m, cy_m, r_m, tag, sub):
    c.setLineWidth(0.8)
    c.setFillColorRGB(0.92, 0.92, 0.92)
    c.setStrokeColorRGB(0, 0, 0)
    c.circle(x(cx_m), y(cy_m), r_m * SCALE_M_TO_PT, stroke=1, fill=1)
    c.setFillColorRGB(0, 0, 0)
    c.setFont("Helvetica-Bold", 7)
    c.drawCentredString(x(cx_m), y(cy_m) - 1.5 * mm, tag)
    c.setFont("Helvetica", 6)
    c.drawCentredString(x(cx_m), y(cy_m) - 4 * mm, sub)


def equipment_rect(c, x_m, y_m, w_m, h_m, tag, sub, fill=(0.95, 0.95, 0.95)):
    c.setLineWidth(0.8)
    c.setFillColorRGB(*fill)
    c.setStrokeColorRGB(0, 0, 0)
    c.rect(x(x_m), y(y_m), w_m * SCALE_M_TO_PT, h_m * SCALE_M_TO_PT,
           stroke=1, fill=1)
    cx, cy = x(x_m + w_m / 2), y(y_m + h_m / 2)
    c.setFillColorRGB(0, 0, 0)
    c.setFont("Helvetica-Bold", 7)
    c.drawCentredString(cx, cy + 1 * mm, tag)
    c.setFont("Helvetica", 6)
    c.drawCentredString(cx, cy - 1.5 * mm, sub)


def source_with_leader(c, src_x_m, src_y_m, label_x_m, label_y_m, label):
    """Marker AT the engineering source location, leader line out to the
    label position in clear space. Standard CAD callout convention."""
    sx, sy = x(src_x_m), y(src_y_m)
    lx, ly = x(label_x_m), y(label_y_m)

    # Leader line (thin, dark red) drawn first so the marker hides its end
    c.setLineWidth(0.4)
    c.setStrokeColorRGB(0.5, 0.10, 0.10)
    c.line(sx, sy, lx, ly)

    # Marker dot at the source itself
    c.setLineWidth(0.5)
    c.setStrokeColorRGB(0, 0, 0)
    c.setFillColorRGB(0.85, 0.10, 0.10)
    c.circle(sx, sy, 1.0 * mm, stroke=1, fill=1)

    # Small white halo behind label so it stays readable over leader/edges
    c.setStrokeColorRGB(1, 1, 1)
    c.setFillColorRGB(1, 1, 1)
    c.rect(lx - 0.5 * mm, ly - 0.5 * mm, 5.0 * mm, 3.0 * mm,
           stroke=0, fill=1)

    # Label text
    c.setFillColorRGB(0.85, 0.10, 0.10)
    c.setFont("Helvetica-Bold", 8)
    c.drawString(lx, ly, label)
    c.setFillColorRGB(0, 0, 0)


def draw_north_arrow(c, cx, cy):
    c.setFillColorRGB(0, 0, 0)
    c.setFont("Helvetica-Bold", 8)
    c.drawCentredString(cx, cy + 7 * mm, "N")
    p = c.beginPath()
    p.moveTo(cx, cy + 5 * mm)
    p.lineTo(cx - 2 * mm, cy - 3 * mm)
    p.lineTo(cx, cy - 1 * mm)
    p.lineTo(cx + 2 * mm, cy - 3 * mm)
    p.close()
    c.drawPath(p, stroke=1, fill=1)


def draw_scale_bar(c, base_x, base_y, length_m=10):
    c.setLineWidth(0.8)
    c.setStrokeColorRGB(0, 0, 0)
    bar_pts = length_m * SCALE_M_TO_PT
    c.line(base_x, base_y, base_x + bar_pts, base_y)
    for tick_m in (0, length_m / 2, length_m):
        c.line(base_x + tick_m * SCALE_M_TO_PT, base_y - 1 * mm,
               base_x + tick_m * SCALE_M_TO_PT, base_y + 1 * mm)
    c.setFont("Helvetica", 6)
    c.drawString(base_x, base_y + 1.5 * mm, "0")
    c.drawCentredString(base_x + bar_pts / 2, base_y + 1.5 * mm,
                        str(int(length_m / 2)))
    c.drawString(base_x + bar_pts - 3 * mm, base_y + 1.5 * mm,
                 f"{int(length_m)} m")


def draw_drawing_border(c):
    c.setLineWidth(1.5)
    c.setStrokeColorRGB(0, 0, 0)
    c.rect(15 * mm, 15 * mm, PAGE_W - 30 * mm, PAGE_H - 30 * mm,
           stroke=1, fill=0)
    # title-block separator
    c.setLineWidth(0.5)
    c.line(15 * mm, 55 * mm, PAGE_W - 15 * mm, 55 * mm)
    c.line(195 * mm, 15 * mm, 195 * mm, 55 * mm)


def draw_title_block(c):
    c.setFillColorRGB(0, 0, 0)

    # Left half: project / drawing info
    c.setFont("Helvetica-Bold", 11)
    c.drawString(20 * mm, 47 * mm, "NORTHGATE BULK STORAGE TERMINAL")
    c.setFont("Helvetica", 9)
    c.drawString(20 * mm, 41 * mm, "Plot plan — release source locations")

    c.setFont("Helvetica", 7)
    c.drawString(20 * mm, 34 * mm,
                 "Drawing: HAC-001     Scale: 1:200     Rev: 0     "
                 "Substances: CH4, C3H8, CH3OH, H2")

    c.setFillColorRGB(0.6, 0, 0)
    c.setFont("Helvetica-Oblique", 7)
    c.drawString(20 * mm, 28 * mm,
                 "FICTIONAL DEMONSTRATION PLANT — not for design or "
                 "compliance use.")
    c.setFillColorRGB(0, 0, 0)
    c.setFont("Helvetica", 6)
    c.drawString(20 * mm, 22 * mm,
                 "Generated for hac-canvas demo  ·  Scaling Smiths YT V2  "
                 "·  python-reportlab")

    # Right half: source legend
    c.setFont("Helvetica-Bold", 8)
    c.drawString(200 * mm, 47 * mm, "RELEASE SOURCES")
    c.setFont("Helvetica", 7)
    c.drawString(200 * mm, 41 * mm,
                 "S1  Tank breather vent (CH4)        primary")
    c.drawString(200 * mm, 36 * mm,
                 "S2  Pump shaft seal (C3H8)          primary")
    c.drawString(200 * mm, 31 * mm,
                 "S3  Open drain (CH3OH)              primary")
    c.drawString(200 * mm, 26 * mm,
                 "S4  Compressor flange (H2)          secondary")
    c.setFont("Helvetica-Oblique", 6)
    c.drawString(200 * mm, 20 * mm,
                 "Zones not shown — computed by hac-canvas tool.")


# ---------------------------------------------------------------------------
# Build the page
# ---------------------------------------------------------------------------

def build():
    c = rl_canvas.Canvas(str(OUT_PDF), pagesize=(PAGE_W, PAGE_H))

    draw_drawing_border(c)
    draw_compound_fence(c)

    # Equipment
    equipment_circle(c, cx_m=10, cy_m=25, r_m=2,
                     tag="T-101", sub="CH4 storage")
    equipment_rect(c,  x_m=22, y_m=16, w_m=6, h_m=4,
                   tag="P-101", sub="C3H8 booster pump")
    equipment_rect(c,  x_m=35, y_m=5,  w_m=6, h_m=6,
                   tag="D-201", sub="CH3OH drain bund",
                   fill=(0.97, 0.97, 0.85))
    equipment_rect(c,  x_m=42, y_m=22, w_m=6, h_m=6,
                   tag="K-301", sub="H2 compressor")

    # Release source markers — at the actual engineering location, with a
    # leader line out to the label in clear space.
    #   S1 = vent rises from tank top         (marker inside tank)
    #   S2 = shaft seal on pump drive end     (marker on pump east edge)
    #   S3 = open drain tundish               (marker just outside bund S wall)
    #   S4 = compressor flange / pipe connection (marker on compressor S edge)
    source_with_leader(c, src_x_m=10,   src_y_m=25.5, label_x_m=15, label_y_m=29,    label="S1")
    source_with_leader(c, src_x_m=28,   src_y_m=18,   label_x_m=32, label_y_m=20,    label="S2")
    source_with_leader(c, src_x_m=38,   src_y_m=4.5,  label_x_m=43, label_y_m=2,     label="S3")
    source_with_leader(c, src_x_m=45,   src_y_m=22,   label_x_m=46, label_y_m=18.5,  label="S4")

    # Annotations
    draw_north_arrow(c, x(50) + 12 * mm, y(28))
    draw_scale_bar(c, x(0), y(0) - 12 * mm, length_m=10)

    draw_title_block(c)

    c.showPage()
    c.save()
    print(f"Wrote {OUT_PDF}")


if __name__ == "__main__":
    build()
