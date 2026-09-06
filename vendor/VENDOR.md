# Vendored third-party skills (reference material for ai-film-studio)

These are kept for study and for extracting craft into `reference/directing.md`. They are **not** installed as
active Claude Code skills (their triggers overlap ai-film-studio's and would fight its routing). Read them; do not
run them. All three were scanned on 2026-09-06 before vendoring: markdown/JSON only, no scripts, no executables, no
hidden Unicode, no network/credential/deletion instructions, no prompt-injection phrasing.

| Folder | Upstream | Commit | License | Author | What to learn from it |
|---|---|---|---|---|---|
| `DirectorSKILL/` | https://github.com/wuwangzhang1216/DirectorSKILL | c65ae0d | MIT | wangzhang-wu | 13-step pipeline; **identity string** (30–50 words, pasted verbatim into every prompt); 15 continuity axes; **failure codes F1–F19 + cost ladder L1–L7**; three-strike rule; 20 director-style overlays |
| `visual-skills/` | https://github.com/smixs/visual-skills | 3c55471 | CC BY 4.0 (credit Serge Shima; keep `NOTICE`) | Serge Shima | **Scene formula** (desire + obstacle + geometry + gaze + rhythm); three-detail rule; three-jobs rule; Murch's Rule of Six; blocking as desire; motivated camera; three-layer storyboard; Seedance 2.5 / Kling / Veo syntax |
| `_local-only/hoodini-director/` | https://github.com/hoodini/ai-agents-skills (skills/director) | f7a43d8 | **no license file upstream** → kept out of git (`.gitignore`), local study only | Yuval Avidani | **Gated development**: kill shot → 2–3 concepts with tests → timed beat sheet with value shifts and setup/payoff ledger → shot list → only then pixels; Pixar's 22 rules; want/need, wound, stakes, turn; "but/therefore, never and-then"; 28-chapter bible in `references/` |

Attribution: anything in `reference/directing.md` derived from visual-skills carries the CC BY 4.0 credit line.
To refresh a vendored copy: re-clone upstream into a scratch dir, re-run the contamination scan, then rsync.
