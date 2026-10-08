"""fig:genome -- the genome g = (lambda, psi): one membership bit and five verb programs per layer.
A child differs from its parent in one coordinate: child 1 overrides one verb (summary.route),
child 2 flips one membership bit (skill); the verbatim bit is locked.  True print size.
Build: PYTHONPATH=src python3 src/fig_genome.py && soffice --headless --convert-to pdf --outdir out out/fig_genome.pptx"""
import os, pathlib
from figlib import *
W2, H2 = 7.4, 3.8
prs.slide_width = Emu(int(W2 * CM)); prs.slide_height = Emu(int(H2 * CM))
F = 7.5
LAM0, LAMW = 1.55, 0.44
VX = [2.05, 3.06, 4.07, 5.25, 6.3]; VW = 1.02
ROWS = [('skill', 'Skill'), ('graph', 'Graph'), ('summary', 'Summary'), ('verbatim', 'Raw')]
RY = [0.86, 1.34, 1.82, 2.30]; RH = 0.42
# headers
rect(LAM0, 0.06, LAMW, 0.34, C('EEF0F3'), None, 0, 0.2); text(LAM0, 0.06, LAMW, 0.34, M('λ', 9), PP_ALIGN.CENTER)
rect(VX[0], 0.06, VX[2] + VW - VX[0], 0.34, C('E6F3EA'), None, 0, 0.2)
text(VX[0], 0.06, VX[2] + VW - VX[0], 0.34, [R('in-layer  ', F, True, C('2E6B4A')), M('ψ', 9, C('2E6B4A'))], PP_ALIGN.CENTER)
rect(VX[3], 0.06, VX[4] + VW - VX[3], 0.34, C('EAF1FB'), None, 0, 0.2)
text(VX[3], 0.06, VX[4] + VW - VX[3], 0.34, [R('cross-layer  ', F, True, K_CT), M('ψ', 9, K_CT)], PP_ALIGN.CENTER)
for x, v in zip(VX, ['admit', 'index', 'score', 'propose', 'route']):
    text(x - 0.03, 0.44, VW + 0.06, 0.34, R(v, 7, False, K_FN, False, MONO), PP_ALIGN.CENTER, pad=0)
# rows
for (ic, nm), y in zip(ROWS, RY):
    icon(ic, 0.02, y + 0.06, 0.3); text(0.34, y, 1.1, RH, R(nm, 7.2, True), pad=0.0)
    for x in VX: rect(x, y + 0.03, VW, RH - 0.06, C('F6F4FB'), C('C9C2DE'), 0.6, 0.18)
    # membership bit: a switch, or a lock on the floor
    if nm == 'Raw':
        icon('lock', LAM0 + 0.08, y + 0.06, 0.28)
    else:
        on = nm != 'Skill'
        px, py = LAM0 + 0.04, y + 0.11
        rect(px, py, 0.36, 0.2, C('3E8E7E') if on else C('C3C8D0'), None, 0, 0.5)
        oval(px + (0.26 if on else 0.1), py + 0.1, 0.075, WHITE, C('9AA3B0'), 0.5)
# child 1: summary.route overridden; child 2: the skill bit flipped
ys = RY[2]; rect(VX[4], ys + 0.03, VW, RH - 0.06, HILITE, HILINE, 1.25, 0.18, MSO_LINE_DASH_STYLE.DASH)
rect(LAM0 + 0.01, RY[0] + 0.02, LAMW - 0.02, RH - 0.04, WHITE, HILINE, 1.25, 0.2, MSO_LINE_DASH_STYLE.DASH, nofill=True)
# key
ky = 2.92
rect(0.1, ky + 0.06, 0.3, 0.22, HILITE, HILINE, 1.0, 0.18, MSO_LINE_DASH_STYLE.DASH)
text(0.45, ky, 3.2, 0.34, R('child 1: override one verb', F))
rect(3.85, ky + 0.06, 0.3, 0.22, WHITE, HILINE, 1.0, 0.18, MSO_LINE_DASH_STYLE.DASH)
text(4.2, ky, 3.1, 0.34, R('child 2: flip one bit', F))
icon('lock', 0.12, ky + 0.42, 0.26); text(0.45, ky + 0.4, 3.0, 0.34, R('raw bit locked', F))
for o in sorted(OVER, reverse=True): print('OVERFLOW %.2f cm  %-40s at (%s, %s)' % o)
os.makedirs('out', exist_ok=True); prs.save('out/fig_genome.pptx'); print('written')
