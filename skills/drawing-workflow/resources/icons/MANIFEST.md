# Icon set for the MemDGM figures (icons2)

One family for every concept: **Icons8 Fluency** (API platform code `fluent`), colourful flat glyphs with soft gradients. No concept needed the `color` fallback, so nothing here is off-family.
All files are 256x256 RGBA PNGs with a transparent background (checked with PIL: PNG magic bytes, mode RGBA, alpha min 0).
Source URL pattern: `https://img.icons8.com/?id=<ID>&format=png&size=256`. SVG is unavailable: `get_icon_svg` returned "Your Icons8 account does not have MCP API access", so the PNGs are the assets. At 256 px they stay sharp at the ~0.5 to 1 cm sizes the figure uses.
Licence: Icons8 icons need either a link to icons8.com in the paper/acknowledgements or a paid Icons8 licence. Most of these icons do not carry the free-set flag.

The Task Agent icon was chosen so it does not match the agent icons in the author's other papers or the ones the current figure already uses. The exclusion list is in `scratchpad/wf2/exclusion.md`. Robot heads, humanoid busts, heads with brains, and circuit brains were ruled out.

| concept | file | icon name (commonName) | id | style | source URL | glyph |
|---|---|---|---|---|---|---|
| task_agent | `task_agent.png` | Sparkles (`sparkles`) | `zAkA21sxGwue` | fluency | https://img.icons8.com/?id=zAkA21sxGwue&format=png&size=256 | Large blue four-point sparkle with a small companion sparkle; the generic "AI" mark, no face, no robot, no brain |
| benchmark_arena | `benchmark_arena.png` | Trophy (`trophy`) | `kPENNmiEJv3b` | fluency | https://img.icons8.com/?id=kPENNmiEJv3b&format=png&size=256 | Gold cup trophy with two handles on a short stem |
| accuracy | `accuracy.png` | Goal (`goal`) | `Yt084riMRP1m` | fluency | https://img.icons8.com/?id=Yt084riMRP1m&format=png&size=256 | Red-and-white bullseye with an arrow in the centre |
| tokens | `tokens.png` | Stack of Coins (`stack-of-coins`) | `aCwmf28BGlPc` | fluency | https://img.icons8.com/?id=aCwmf28BGlPc&format=png&size=256 | Two stacks of gold coins, tall and short |
| latency | `latency.png` | Stopwatch (`stopwatch`) | `YJRLDGN3QPEn` | fluency | https://img.icons8.com/?id=YJRLDGN3QPEn&format=png&size=256 | Grey stopwatch with crown button and a single hand |
| feedback | `feedback.png` | Synchronize (`synchronize`) | `KhfdumHglzRO` | fluency | https://img.icons8.com/?id=KhfdumHglzRO&format=png&size=256 | Two orange-red curved arrows chasing each other in a loop |
| query | `query.png` | Ask Question (`ask-question`) | `YSdQbX213JrZ` | fluency | https://img.icons8.com/?id=YSdQbX213JrZ&format=png&size=256 | Blue square speech bubble with a white question mark |
| answer | `answer.png` | Speaker Notes (`speaker-notes`) | `89HH4vYS3hP3` | fluency | https://img.icons8.com/?id=89HH4vYS3hP3&format=png&size=256 | Blue square speech bubble (same shape as query) holding a bulleted list; pairs with query as Q then A |
| nl_interface | `nl_interface.png` | Document (`document`) | `Ygov9LJC2LzE` | fluency | https://img.icons8.com/?id=Ygov9LJC2LzE&format=png&size=256 | Cyan page with a folded corner and text lines |
| latent_interface | `latent_interface.png` | Thumbnails (`thumbnails`) | `IzaAjUZfZt1E` | fluency | https://img.icons8.com/?id=IzaAjUZfZt1E&format=png&size=256 | 3x3 grid of solid blue squares; reads as a matrix / tensor block |
| attention | `attention.png` | Eye (`visible`) | `CWkCzh9aKpqb` | fluency | https://img.icons8.com/?id=CWkCzh9aKpqb&format=png&size=256 | Large blue iris eye on a grey eyeball |
| terminal | `terminal.png` | Console (`console`) | `WbRVMGxHh74X` | fluency | https://img.icons8.com/?id=WbRVMGxHh74X&format=png&size=256 | Dark window with a title bar, a ">" prompt and a cursor bar |
| python_code | `python_code.png` | Python (`python`) | `l75OEUJkPAk4` | fluency | https://img.icons8.com/?id=l75OEUJkPAk4&format=png&size=256 | Python blue-and-yellow twin-snake logo (brand glyph, used because the concept is literally Python code) |
| archive_tree | `archive_tree.png` | Code Fork (`code-fork`) | `o5M0qsDZdWP3` | fluency | https://img.icons8.com/?id=o5M0qsDZdWP3&format=png&size=256 | Git-style branch: one trunk node splitting to two blue nodes |
| select_parent | `select_parent.png` | Hand Cursor (`hand-cursor`) | `0DZVqi4HKP6A` | fluency | https://img.icons8.com/?id=0DZVqi4HKP6A&format=png&size=256 | Yellow pointing hand cursor |
| evaluate | `evaluate.png` | Test Tube (`test-tube`) | `XO5nRSypAbfH` | fluency | https://img.icons8.com/?id=XO5nRSypAbfH&format=png&size=256 | Conical lab flask with green liquid and bubbles |
| paired_test | `paired_test.png` | Scales (`scales`) | `szZDhO4hzAsa` | fluency | https://img.icons8.com/?id=szZDhO4hzAsa&format=png&size=256 | Gold balance scale with two pans |
| accept | `accept.png` | Checkmark (`checked`) | `pIPl8tqh3igN` | fluency | https://img.icons8.com/?id=pIPl8tqh3igN&format=png&size=256 | Green circle with a dark check |
| reject | `reject.png` | Cancel (`cancel`) | `fYgQxDaH069W` | fluency | https://img.icons8.com/?id=fYgQxDaH069W&format=png&size=256 | Red circle with a white X |
| skill | `skill.png` | Toolbox (`toolbox`) | `2sWu6PtiXHWx` | fluency | https://img.icons8.com/?id=2sWu6PtiXHWx&format=png&size=256 | Red toolbox with a handle |
| graph | `graph.png` | Mind Map (`mind-map`) | `Tc3kCFjWVdkR` | fluency | https://img.icons8.com/?id=Tc3kCFjWVdkR&format=png&size=256 | Light-blue hub node linked to five dark-blue nodes |
| summary | `summary.png` | Note (`note`) | `EQ81mUwjgToc` | fluency | https://img.icons8.com/?id=EQ81mUwjgToc&format=png&size=256 | Yellow sticky note with lines and a dark folded corner |
| verbatim | `verbatim.png` | Discussion Forum (`comment-discussion`) | `PCur9YsRJIMS` | fluency | https://img.icons8.com/?id=PCur9YsRJIMS&format=png&size=256 | Three stacked blue chat bars offset left and right, a chat transcript |
| layers_stack | `layers_stack.png` | Layers (`layers`) | `wJVDOwCZqokW` | fluency | https://img.icons8.com/?id=wJVDOwCZqokW&format=png&size=256 | Three stacked planes: green on top, blue, grey |
| promote | `promote.png` | Scroll Up (`circled-up-2`) | `yqqH8yVA7lVp` | fluency | https://img.icons8.com/?id=yqqH8yVA7lVp&format=png&size=256 | Blue circle with a white up arrow (pairs with demote) |
| demote | `demote.png` | Scroll Down (`circled-down-2`) | `oWNmXOb2HARO` | fluency | https://img.icons8.com/?id=oWNmXOb2HARO&format=png&size=256 | Blue circle with a white down arrow (pairs with promote) |
| route | `route.png` | Signpost (`signpost`) | `a7jswSXp7fdU` | fluency | https://img.icons8.com/?id=a7jswSXp7fdU&format=png&size=256 | Yellow two-arm signpost on a red post, arms pointing opposite ways |
| support_link | `support_link.png` | Link (`link`) | `n9d0Hm43JCPK` | fluency | https://img.icons8.com/?id=n9d0Hm43JCPK&format=png&size=256 | Two interlocked blue chain links |
| evolution | `evolution.png` | Biotech (`biotech`) | `mRoJr3l2IK7g` | fluency | https://img.icons8.com/?id=mRoJr3l2IK7g&format=png&size=256 | Purple DNA double helix |
| zoom | `zoom.png` | Zoom In (`zoom-in`) | `EdWowxx2Bj85` | fluency | https://img.icons8.com/?id=EdWowxx2Bj85&format=png&size=256 | Light-blue magnifier with a plus sign |
| rewriter | `rewriter.png` | Edit Pencil (`edit`) | `OWRPl8fxkRvG` | fluency | https://img.icons8.com/?id=OWRPl8fxkRvG&format=png&size=256 | Yellow pencil with a red eraser, drawn diagonally |
| budget | `budget.png` | Coin Wallet (`coin-wallet`) | `WpfQ7DvG8Z3W` | fluency | https://img.icons8.com/?id=WpfQ7DvG8Z3W&format=png&size=256 | Red-orange wallet with a gold coin tucked in the top |
| focus_set | `focus_set.png` | Filter (`filter--v2`) | `UT0KFoaguV2Z` | fluency | https://img.icons8.com/?id=UT0KFoaguV2Z&format=png&size=256 | Orange funnel |

## Alternates considered (same family)

- task_agent: `ai-computer` (D6hQU99a4yc6), a monitor with sparkles. Rejected because a second screen would compete with the terminal icon. `ai-chip` (VMAmthbSYf7P), a dark chip with sparkles. Rejected because its dark rectangle reads like the console at small size. `ai-component` (ywKOa8qNRVyK), a purple chip with an antenna and legs. Rejected because at a glance it reads like a creature or robot. Also rejected: `ai-agent`, `ai-using`, `critical-thinking` (head silhouettes, too close to HarnessRL's head-with-brain), `artificial-intelligence` and `electronic-brain` (circuit brains, too close to HarnessRL's pk_artificial-intelligence), and `bot` and `ai-robot*` (robot heads, excluded).
- latent_interface: `heat-map` (oKyyU1jj8IJ2), a dot matrix with axes. Rejected because it reads as a scatter chart. `squared-menu` (7aC2RvApnWLR) is a lighter 3x3 grid if the darker one is too heavy.
- answer: Fluency has no speech bubble with a check. `speaker-notes` pairs with `ask-question` because the bubble shape is the same and only the contents change. `speech-bubble` (hByk2bcP4aZ5, plain green) is the other option.
- python_code: `code-file` (mXRsZ8Xy4xvM), a blue file with `</>`, if a brand logo is unwanted.
- focus_set: the blue `filter` (HjFb6s4aXAL2) is the exact icon Mem-Pi's Figure 1 uses, so the orange `filter--v2` was taken instead.
- evaluate: `inspection` (3Be2L1fYzyak), a clipboard with a blue check. archive_tree: `tree-structure` (E43SDB7hSZLx), a box hierarchy.

`contact_sheet.png` shows every icon at 96 px with its concept name.

| judge | judge.png | Law (gavel) | Njg6Q8UV6MHS | fluency | https://img.icons8.com/?id=Njg6Q8UV6MHS&format=png&size=256 | gavel on block |
| lock | lock.png | Lock | EHyUO6ZGSRkX | fluency | https://img.icons8.com/?id=EHyUO6ZGSRkX&format=png&size=256 | yellow padlock |
| diagnosis | diagnosis.png | System Diagnostic | NZX0btBOVRd6 | fluency | https://img.icons8.com/?id=NZX0btBOVRd6&format=png&size=256 | stethoscope on cyan tile |
| run | run.png | Circled Play Button | KQ5qZwOlaNdR | fluency | https://img.icons8.com/?id=KQ5qZwOlaNdR&format=png&size=256 | blue play disc |
| code_edit | code_edit.png | Code | keI1M862UTP2 | fluency | https://img.icons8.com/?id=keI1M862UTP2&format=png&size=256 | window with </> |
| contract | contract.png | Security Shield | FbRY9JkBrjiX | fluency | https://img.icons8.com/?id=FbRY9JkBrjiX&format=png&size=256 | green shield |
| log | log.png | Logbook | 4brDa8Wu96MT | fluency | https://img.icons8.com/?id=4brDa8Wu96MT&format=png&size=256 | logbook |
| latent_purple | latent_purple.png | latent_interface recoloured to #7B5EA7 | - | fluency (recoloured) | derived | purple 3x3 grid |
| stop | stop.png | Stop Sign | Zrc20nIaPRtZ | fluency | https://img.icons8.com/?id=Zrc20nIaPRtZ&format=png&size=256 | red octagon stop sign |
| database | database.png | Database | KZHjwwenS7oK | fluency | https://img.icons8.com/?id=KZHjwwenS7oK&format=png&size=256 | blue cylinder stack (data sources) |
| plugin | plugin.png | Plugin | LV1toaPaA7ia | fluency | https://img.icons8.com/?id=LV1toaPaA7ia&format=png&size=256 | violet brick (adapter, dataset interface) |
| api | api.png | API | RlIXjuTUrwoX | fluency | https://img.icons8.com/?id=RlIXjuTUrwoX&format=png&size=256 | blue API tile (system interface) |
| piece_evidence | piece_evidence.png | Piece Of Evidence | qTUv38Pw3E8m | fluency | https://img.icons8.com/?id=qTUv38Pw3E8m&format=png&size=256 | fingerprint in magnifier (evidence recall) |
| chat | chat.png | Chat | GzN4ltD52jcA | fluency | https://img.icons8.com/?id=GzN4ltD52jcA&format=png&size=256 | two speech bubbles (a dialogue record) |
| write_pen | write_pen.png | Edit Pencil | OWRPl8fxkRvG | fluency | https://img.icons8.com/?id=OWRPl8fxkRvG&format=png&size=256 | pencil (write call) |
| document | document.png | Document | Ygov9LJC2LzE | fluency | https://img.icons8.com/?id=Ygov9LJC2LzE&format=png&size=256 | cyan page (read call) |
