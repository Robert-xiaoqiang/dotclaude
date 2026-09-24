"""fig:channels -- the same derived item x spent through the content channel (its text enters the
context C) and through the routing channel (its support supp(x) forwards the gold leaf into C).
True print size (13.97 cm wide), so type is the printed size.  Icons8 Fluency via figlib.
Build: python3 src/fig_channels.py && soffice --headless --convert-to pdf --outdir out out/fig_channels.pptx"""
import os, pathlib
from figlib import *
W2, H2 = 13.97, 3.55
prs.slide_width = Emu(int(W2 * CM)); prs.slide_height = Emu(int(H2 * CM))
F = 8.5; FT2 = 9
CT, RT, GOLD = C('2E6E8E'), C('B4472F'), C('F2C23E')
def panel2(x0, title, sym, col, route):
    rect(x0, 0.02, 6.85, H2 - 0.04, WHITE, C('C9CED6'), 0.75, 0.03)
    tw = width_cm([R(title + '  ', FT2, True, col)])
    text(x0 + 0.12, 0.06, 6.0, 0.42, [R(title + '  ', FT2, True, col), R('C', FT2 + 1, False, col, False, SANS)])
    text(x0 + 0.12 + tw + 0.22, 0.2, 1.0, 0.35, R(sym, 7, False, col), pad=0)
    # the derived item x
    rect(x0 + 0.15, 0.6, 2.7, 0.92, WHITE, INK, 0.8, 0.12); icon('summary', x0 + 0.24, 0.72, 0.42)
    text(x0 + 0.72, 0.62, 1.85, 0.42, [M('x', 10), R('  summary', F, True)])
    tcol = C('A0A7B2') if route else INK
    text(x0 + 0.62, 1.02, 2.22, 0.42, R('“plans to move”', 7.2, False, tcol, True, SERIF))
    if route: seg(x0 + 0.66, 1.24, x0 + 2.8, 1.24, C('A0A7B2'), 0.75)        # text never read
    # verbatim leaves, the gold one starred, supp(x) = leaves 2..4
    lx = [x0 + 0.22 + 0.34 * k for k in range(7)]; ly = 2.68
    for k, x in enumerate(lx):
        insupp = 2 <= k <= 4
        fill = GOLD if k == 3 else (HILITE if (route and insupp) else WHITE)
        rect(x, ly, 0.26, 0.26, fill, (HILINE if (route and insupp) else GREY), 0.75, 0.1)
    text(lx[3] - 0.05, ly - 0.02, 0.36, 0.3, R('★', 7, False, INK, False, FREE), PP_ALIGN.CENTER, pad=0)
    text(x0 + 0.1, ly + 0.28, 2.6, 0.4, [R('verbatim leaves  ', 7.5, False, GREY), S('\U0001D4B1', 9, GREY)])
    fan = C('B4472F') if route else C('C3C8D0')
    for k in (2, 3, 4): seg(x0 + 1.25 + 0.06 * (k - 3), 1.52, lx[k] + 0.13, ly, fan, 0.8, MSO_LINE_DASH_STYLE.DASH)
    text(x0 + 1.62, 1.92, 1.3, 0.4, [R('supp', 7.5, False, fan), R('(', 7.5, False, fan), M('x', 9, fan), R(')', 7.5, False, fan)])
    # context C and the reader
    cx, cy, cw, ch = x0 + 3.35, 1.62, 2.0, 0.56
    text(cx, cy - 0.42, cw, 0.4, M('C', 10), PP_ALIGN.CENTER)
    rect(cx, cy, cw, ch, WHITE, GREY, 0.75, 0.12)
    if route:
        for k in range(3): rect(cx + 0.35 + k * 0.45, cy + 0.14, 0.28, 0.28, GOLD if k == 1 else HILITE, HILINE, 0.75, 0.1)
        text(cx + 0.35 + 0.45 - 0.04, cy + 0.12, 0.36, 0.3, R('★', 7, False, INK, False, FREE), PP_ALIGN.CENTER, pad=0)
        path([(lx[-1] + 0.3, ly + 0.13), (x0 + 3.05, ly + 0.13), (x0 + 3.05, cy + ch / 2), (cx, cy + ch / 2)], col=RT, w=1.0)
    else:
        chip(cx + 0.15, cy + 0.1, cw - 0.3, 0.36, [R('text', 7.5, False, CT), R('(', 7.5, False, CT), M('x', 9, CT), R(')', 7.5, False, CT)], C('EAF3FA'), CT, 0.6)
        path([(x0 + 2.85, 1.06), (x0 + 3.05, 1.06), (x0 + 3.05, cy + ch / 2), (cx, cy + ch / 2)], col=CT, w=1.0)
    seg(cx + cw, cy + ch / 2, x0 + 5.72, cy + ch / 2, INK, 1.0, head=True)
    icon('task_agent', x0 + 5.8, cy - 0.12, 0.62); text(x0 + 5.55, cy + 0.52, 1.2, 0.35, R('reader', 7.5, False, GREY), PP_ALIGN.CENTER)
    icon('accept' if route else 'reject', x0 + 6.28, cy - 0.2, 0.3)
    # the measured consequence: gold mass
    chip(x0 + 3.55, 2.62, 2.9, 0.44, [M('μ', 10), R('(', F), M('G', 10), R(')  ', F), R('raised' if route else 'unchanged', F, True, RT if route else GREY)],
         C('FBEFEA') if route else C('F3F4F6'), RT if route else GREY, 0.6)
panel2(0.02, 'Content channel', 'txt', CT, False)
panel2(7.1, 'Routing channel', 'route', RT, True)
for o in sorted(OVER, reverse=True): print('OVERFLOW %.2f cm  %-40s at (%s, %s)' % o)
os.makedirs('out', exist_ok=True); prs.save('out/fig_channels.pptx'); print('written')
