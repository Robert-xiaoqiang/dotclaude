"""fig:arena -- MemArena, four panels left to right at true print size (13.97 cm, \\textwidth):
(a) heterogeneous sources, seven corpora and an ellipsis; (b) the dataset interface, adapters that map
each source into one episode schema e=(R,Q): a record of timestamped, speaker-tagged sessions and a
query tuple; (c) the system interface, write(chunk) / read(q) with the memory systems behind it;
(d) the metric suite.  Build: PYTHONPATH=src python3 src/fig_arena.py"""
import os
from figlib import *
W2, H2 = 13.97, 3.95
prs.slide_width = Emu(int(W2 * CM)); prs.slide_height = Emu(int(H2 * CM))
F = 7.5; FT2 = 9
COL = dict(src=C('2E6E8E'), dsi=C('B8752A'), sys=C('6A55A5'), met=C('3E8E6B'))
FILL = dict(src=C('EAF1FA'), dsi=C('FFF6E6'), sys=C('F3F0FA'), met=C('E9F5EE'))
Y0, PH = 0.03, H2 - 0.06
def pnl(x, w, key, ic, title):
    rect(x, Y0, w, PH, FILL[key], C('C9CED6'), 0.75, 0.04)
    icon(ic, x + 0.1, Y0 + 0.1, 0.36); text(x + 0.52, Y0 + 0.06, w - 0.6, 0.44, R(title, FT2, True, COL[key]))
def arrow(x1, x2, y, lab=None):
    seg(x1 + 0.03, y, x2 - 0.03, y, INK, 1.0, head=True)
    if lab: text(x1 - 0.1, y - 0.46, x2 - x1 + 0.2, 0.4, lab, PP_ALIGN.CENTER, pad=0)

# ------------------------------------------------------------------ (a) sources
xa, wa = 0.02, 2.75
pnl(xa, wa, 'src', 'database', 'Sources')
SRC = ['LoCoMo', 'LongMemEval', 'MemoryAgentBench', 'PersonaMem-V2', 'InMind', 'PerLTQA', 'LifelongAgentBench', '…']
for k, n in enumerate(SRC):
    chip(xa + 0.15, 0.58 + k * 0.405, wa - 0.3, 0.34, R(n, 7, n == '…'), WHITE, GREY, 0.6, rad=0.25)

# ------------------------------------------------------------------ (b) dataset interface
xb, wb = xa + wa + 0.36, 3.2
arrow(xa + wa, xb, 2.05)
icon('plugin', xa + wa + 0.02, 2.2, 0.3)
pnl(xb, wb, 'dsi', 'plugin', 'Dataset interface')
text(xb + 0.12, 0.56, wb - 0.2, 0.4, [R('episode  ', F, True), M('e = (R, ', 9), S('\U0001D4AC', 10), R('e', 9, False, INK, True, SERIF, True), M(')', 9)])
# the record R: three sessions of timestamped turns
rect(xb + 0.15, 1.0, wb - 0.3, 1.52, WHITE, GREY, 0.6, 0.06)
icon('chat', xb + 0.24, 1.07, 0.3); text(xb + 0.6, 1.02, 1.6, 0.36, [R('record  ', F, True), M('R', 9)])
for s in range(3):
    y = 1.46 + s * 0.34
    text(xb + 0.22, y - 0.02, 0.62, 0.3, R('t' + str(s + 1), 6.5, False, GREY, False, MONO), pad=0)
    for k in range(6 - (s % 2)):
        col = C('D9E8F5') if k % 2 == 0 else C('FCE9D6')
        rect(xb + 0.6 + k * 0.38, y, 0.3, 0.24, col, GREY, 0.5, 0.12)
# the query tuple
rect(xb + 0.15, 2.66, wb - 0.3, 1.1, WHITE, GREY, 0.6, 0.06)
icon('query', xb + 0.24, 2.73, 0.3); text(xb + 0.6, 2.68, 2.0, 0.36, [R('queries  ', F, True), S('\U0001D4AC', 10), R('e', 9, False, INK, True, SERIF, True)])
text(xb + 0.2, 3.1, wb - 0.4, 0.5, [M('(q, a', 9), R('⋆', 7, False, INK, False, FREE), M(', G(q), τ, t', 9), R('q', 9, False, INK, True, SERIF, True), M(')', 9)], PP_ALIGN.CENTER)

# ------------------------------------------------------------------ (c) system interface
xc, wc = xb + wb + 0.36, 3.9
arrow(xb + wb, xc, 2.05, [M('e', 9)])
pnl(xc, wc, 'sys', 'api', 'System interface')
for k, (fn, arg, ret) in enumerate([('write', 'chunk', ''), ('read', 'q', ' → C')]):
    y = 0.6 + k * 0.46
    rect(xc + 0.15, y, wc - 0.3, 0.38, WHITE, INK, 0.75, 0.1)
    icon('write_pen' if k == 0 else 'document', xc + 0.22, y + 0.04, 0.3)
    text(xc + 0.6, y, wc - 0.8, 0.38, [R(fn, 7.5, True, C('6F42C1'), False, MONO), R('(' + arg + ')' + ret, 7.5, False, INK, False, MONO)])
SYS = ['MemGPT', 'Mem0', 'A-Mem', 'MemoryOS', 'HMO', 'Mem-α', 'AutoMem', 'MemEvolve', 'MemPro', '…']
cw = (wc - 0.3 - 0.08 * 2) / 3
for k, n in enumerate(SYS):
    x = xc + 0.15 + (k % 3) * (cw + 0.08); y = 1.62 + (k // 3) * 0.42
    chip(x, y, cw, 0.34, R(n, 6.2, n == '…'), WHITE, GREY, 0.6, rad=0.25)
# the paper's own system, full width, accent
chip(xc + 0.15 + (cw + 0.08), 1.62 + 3 * 0.42, 2 * cw + 0.08, 0.34, R('MemCodex', 7, True, WHITE, False, MONO), C('B4472F'), C('8C3522'), 0.75, rad=0.25)

# ------------------------------------------------------------------ (d) metric suite
xd = xc + wc + 0.66; wd = W2 - 0.02 - xd
arrow(xc + wc, xd, 2.05, [M('a, C', 9)])
pnl(xd, wd, 'met', 'judge', 'Metric suite')
MET = [('accuracy', 'Task success', 'Acc'), ('piece_evidence', 'Memory quality', 'Rec'), ('tokens', 'Context cost', 'Tok/q'), ('latency', 'Inference time', 'Lat')]
for k, (ic, nm, sym) in enumerate(MET):
    y = 0.62 + k * 0.8
    rect(xd + 0.12, y, wd - 0.24, 0.66, WHITE, GREY, 0.6, 0.08)
    icon(ic, xd + 0.2, y + 0.14, 0.38)
    text(xd + 0.66, y + 0.02, wd - 0.8, 0.32, R(nm, 7.2, True))
    text(xd + 0.66, y + 0.31, wd - 0.8, 0.32, R(sym, 7, False, GREY, False, MONO))

out = os.path.join(os.path.dirname(__file__), '..', 'out', 'fig_arena.pptx')
prs.save(out); print('written', out)
for o in sorted(OVER, reverse=True): print('OVERFLOW %.2f cm  %-40s at (%s, %s)' % o)
