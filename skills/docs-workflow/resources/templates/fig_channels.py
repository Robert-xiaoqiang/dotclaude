"""fig:channels -- one case, two channels.  Query: which city is Caroline moving to?  The summary x
says only that she plans to move; the raw turn in its source leaves says Paris.  Content channel:
the summary text enters the context and the reader answers 'unknown'.  Routing channel: the text is
never read, the retrieval mass on x is forwarded to src(x), the raw turn enters the context and the
reader answers 'Paris'.  True print size.  Build: PYTHONPATH=src python3 src/fig_channels.py"""
import os
from figlib import *
W2, H2 = 13.97, 4.5
prs.slide_width = Emu(int(W2 * CM)); prs.slide_height = Emu(int(H2 * CM))
F = 8; CT, RT, GOLD = C('2E6E8E'), C('B4472F'), C('F2C23E')
def panel2(x0, title, sym, col, route):
    rect(x0, 0.02, 6.85, H2 - 0.04, WHITE, C('C9CED6'), 0.75, 0.03)
    tw = width_cm([R(title + '  ', 9, True, col)])
    text(x0 + 0.12, 0.06, 6.0, 0.42, [R(title + '  ', 9, True, col), R('C', 10, False, col, False, SANS)])
    text(x0 + 0.12 + tw + 0.22, 0.2, 1.0, 0.35, R(sym, 7, False, col), pad=0)
    # the query
    icon('query', x0 + 0.15, 0.55, 0.3); text(x0 + 0.5, 0.5, 6.2, 0.4, [M('q', 9), R(':  Which city is Caroline moving to?', 7.5, False, INK, True, SANS)])
    # the derived item x
    rect(x0 + 0.15, 1.0, 2.75, 0.86, WHITE, INK, 0.8, 0.12); icon('summary', x0 + 0.24, 1.1, 0.36)
    text(x0 + 0.66, 1.0, 2.2, 0.4, [M('x', 9), R('  summary', F, True)])
    tcol = C('A0A7B2') if route else INK
    text(x0 + 0.24, 1.38, 2.62, 0.4, R('“Caroline plans to move.”', 6.8, False, tcol, True, SERIF))
    if route: seg(x0 + 0.3, 1.6, x0 + 2.8, 1.6, C('A0A7B2'), 0.75)
    # raw leaves, the gold one starred; src(x) = leaves 2..4
    lx = [x0 + 0.22 + 0.34 * k for k in range(7)]; ly = 3.0
    for k, x in enumerate(lx):
        ins = 2 <= k <= 4
        rect(x, ly, 0.26, 0.26, GOLD if k == 3 else (HILITE if (route and ins) else WHITE), (HILINE if (route and ins) else GREY), 0.75, 0.1)
    text(lx[3] - 0.05, ly - 0.02, 0.36, 0.3, R('★', 7, False, INK, False, FREE), PP_ALIGN.CENTER, pad=0)
    fan = RT if route else C('C3C8D0')
    for k in (2, 3, 4): seg(x0 + 1.4 + 0.06 * (k - 3), 1.86, lx[k] + 0.13, ly, fan, 0.8, MSO_LINE_DASH_STYLE.DASH)
    text(x0 + 1.72, 2.2, 1.3, 0.4, [R('src', 7.5, False, fan), R('(', 7.5, False, fan), M('x', 9, fan), R(')', 7.5, False, fan)])
    # the gold raw turn, called out under its leaf
    seg(lx[3] + 0.13, ly + 0.26, lx[3] + 0.13, 3.55, GOLD if route else C('C3C8D0'), 0.75)
    rect(x0 + 0.1, 3.55, 3.05, 0.42, C('FFF7DC') if route else C('F6F7F9'), C('D4A72C') if route else C('C3C8D0'), 0.6, 0.18)
    text(x0 + 0.12, 3.55, 3.01, 0.42, R('“I’m moving to Paris in May.”', 6.8, False, INK if route else C('8A94A6'), True, SERIF), PP_ALIGN.CENTER)
    text(x0 + 0.15, 4.0, 2.9, 0.38, [R('raw turn in  ', 7, False, GREY), S('\U0001D4B1', 8, GREY)], PP_ALIGN.CENTER)
    # the context C, the reader, the answer
    cx, cy, cw, ch = x0 + 3.3, 1.45, 2.15, 0.86
    text(cx, cy - 0.42, cw, 0.4, M('C', 10), PP_ALIGN.CENTER)
    rect(cx, cy, cw, ch, WHITE, GREY, 0.75, 0.12)
    if route:
        rect(cx + 0.08, cy + 0.1, cw - 0.16, ch - 0.2, C('FFF7DC'), C('D4A72C'), 0.6, 0.2)
        text(cx + 0.1, cy + 0.1, cw - 0.2, ch - 0.2, [[R('“…moving to', 7, False, INK, True, SERIF)], [R('Paris in May.”', 7, False, INK, True, SERIF)]], PP_ALIGN.CENTER)
        path([(lx[-1] + 0.3, ly + 0.13), (x0 + 3.05, ly + 0.13), (x0 + 3.05, cy + ch / 2), (cx, cy + ch / 2)], col=RT, w=1.0)
    else:
        rect(cx + 0.08, cy + 0.1, cw - 0.16, ch - 0.2, C('EAF3FA'), CT, 0.6, 0.2)
        text(cx + 0.1, cy + 0.1, cw - 0.2, ch - 0.2, [[R('“Caroline plans', 7, False, INK, True, SERIF)], [R('to move.”', 7, False, INK, True, SERIF)]], PP_ALIGN.CENTER)
        path([(x0 + 2.9, 1.43), (x0 + 3.05, 1.43), (x0 + 3.05, cy + ch / 2), (cx, cy + ch / 2)], col=CT, w=1.0)
    seg(cx + cw, cy + ch / 2, x0 + 5.8, cy + ch / 2, INK, 1.0, head=True)
    icon('task_agent', x0 + 5.86, cy + 0.06, 0.58); text(x0 + 5.6, cy + 0.66, 1.2, 0.33, R('reader', 7, False, GREY), PP_ALIGN.CENTER)
    ans = R('Paris', F, True, C('1A7F37')) if route else R('unknown', F, True, C('CF222E'))
    rect(x0 + 3.55, 2.55, 3.15, 0.46, WHITE, C('1A7F37') if route else C('CF222E'), 0.75, 0.25)
    icon('accept' if route else 'reject', x0 + 3.63, 2.62, 0.32)
    text(x0 + 4.0, 2.55, 2.6, 0.46, [M('a', 9), R(':  ', F), ans])
    # the measured consequence: gold mass
    chip(x0 + 3.55, 3.3, 3.15, 0.46, [M('μ', 10), R('(', F), M('G', 10), R('(', F), M('q', 10), R('))', F), R(' = ', F), R('1' if route else '0', F, True, RT if route else GREY)],
         C('FBEFEA') if route else C('F3F4F6'), RT if route else GREY, 0.6)
panel2(0.02, 'Content channel', 'txt', CT, False)
panel2(7.1, 'Routing channel', 'route', RT, True)
for o in sorted(OVER, reverse=True): print('OVERFLOW %.2f cm  %-40s at (%s, %s)' % o)
os.makedirs('out', exist_ok=True); prs.save('out/fig_channels.pptx'); print('written')
