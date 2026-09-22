#!/usr/bin/env python3
"""Overlap and alignment audit for a one-slide figure deck.

Reports every pair of shapes whose bounding boxes intersect, skipping the pairs that are meant to
(a container and what it holds, a label centred on its own box), and reports groups of shapes that
are nearly aligned but not exactly, which is what makes a figure look hand-placed.
Usage: python3 audit.py deck.pptx [--tol 0.02]
"""
import sys
from pptx import Presentation
from pptx.util import Emu

EMU = 914400.0

def rects(slide):
    out = []
    for i, sh in enumerate(slide.shapes):
        t = ""
        if sh.has_text_frame:
            t = sh.text_frame.text.strip().replace("\n", " ")[:22]
        out.append({"i": i, "name": sh.shape_type, "t": t,
                    "x": sh.left / EMU, "y": sh.top / EMU,
                    "w": sh.width / EMU, "h": sh.height / EMU})
    return out

def inter(a, b):
    dx = min(a["x"] + a["w"], b["x"] + b["w"]) - max(a["x"], b["x"])
    dy = min(a["y"] + a["h"], b["y"] + b["h"]) - max(a["y"], b["y"])
    return (dx, dy) if dx > 0 and dy > 0 else None

def contains(a, b, pad=0.004):
    return (a["x"] - pad <= b["x"] and a["y"] - pad <= b["y"]
            and a["x"] + a["w"] + pad >= b["x"] + b["w"]
            and a["y"] + a["h"] + pad >= b["y"] + b["h"])

def main(path, tol=0.02, area_floor=0.0004):
    prs = Presentation(path)
    sl = prs.slides[0]
    R = rects(sl)
    W, H = prs.slide_width / EMU, prs.slide_height / EMU
    print(f"{path}  {W:.2f} x {H:.2f} in, {len(R)} shapes")

    print("\n-- off-slide --")
    off = [r for r in R if r["x"] < -0.01 or r["y"] < -0.01
           or r["x"] + r["w"] > W + 0.01 or r["y"] + r["h"] > H + 0.01]
    for r in off:
        print(f"   #{r['i']:<3} {r['t']!r:<26} x {r['x']:.2f}..{r['x']+r['w']:.2f} "
              f"y {r['y']:.2f}..{r['y']+r['h']:.2f}")
    if not off:
        print("   none")

    print("\n-- text over text or over a box it does not belong to --")
    bad = 0
    for i in range(len(R)):
        for j in range(i + 1, len(R)):
            a, b = R[i], R[j]
            if not (a["t"] or b["t"]):
                continue                                   # two blank shapes may touch
            ov = inter(a, b)
            if not ov or ov[0] * ov[1] < area_floor:
                continue
            if contains(a, b) or contains(b, a):
                continue                                   # a label inside its own box
            bad += 1
            print(f"   #{a['i']:<3} {a['t']!r:<24} x #{b['i']:<3} {b['t']!r:<24} "
                  f"overlap {ov[0]:.3f} x {ov[1]:.3f} in")
    if not bad:
        print("   none")

    print("\n-- near misses in alignment (same edge within tol, not equal) --")
    near = 0
    for key in ("x", "y"):
        vals = sorted({round(r[key], 4) for r in R})
        for u, v in zip(vals, vals[1:]):
            if 1e-6 < v - u <= tol:
                a = [r["t"] or f"#{r['i']}" for r in R if round(r[key], 4) == u][:3]
                b = [r["t"] or f"#{r['i']}" for r in R if round(r[key], 4) == v][:3]
                near += 1
                print(f"   {key}={u:.3f} {a}  vs  {key}={v:.3f} {b}")
    if not near:
        print("   none")

if __name__ == "__main__":
    tol = 0.02
    if "--tol" in sys.argv:
        tol = float(sys.argv[sys.argv.index("--tol") + 1])
    main(sys.argv[1], tol)
