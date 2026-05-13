# TYOV Vampire Note Validation Framework

## Architecture Decision

The **Journal section is the source of truth** for which prompts have been resolved. There is no mutable game state file.

```
Validated turn header format:
### Turn x — Prompt y, Entry z
*{Prompt Text}*
```

- Each `### Turn ...` line proves that entry y was reached
- Counting headings by Prompt y tells you which entry of that prompt was used
- The Journal IS the used-prompt tracker — no JSON needed
- `prompts.json` is a **static reference** (the book's prompt text), read-only, never modified

---

## SECTION 1: YAML Frontmatter

### MANDATORY — All required fields present

Every vampire note MUST have a YAML frontmatter block (delimited by `---`) containing:

| Field | Type | Required | Validation |
|-----|--|-|------|
| `tags` | list | ✅ | Must include `tyov`, `vampire`, `rpg` |
| `vampire` | string | ✅ | Non-empty |
| `current_prompt` | int | ✅ | 0–80 (0 = new, pre-roll) |
| `prompts_resolved` | int | ✅ | ≥ 0 |
| `game_over` | bool | ✅ | `true` or `false` |
| `game_over_reason` | string | ✅ | Any string |
| `game_start` | date | ✅ | `YYYY-MM-DD` |
| `game_completed` | date | ✅ | `YYYY-MM-DD` or `""` |
| `diary_exists` | bool | ✅ | `true` or `false` |
| `diary_name` | string | ✅ | Non-empty if `diary_exists: true` |
| `created` | date | ✅ | `YYYY-MM-DD` |
| `modified` | date | ✅ | `YYYY-MM-DD` |
| `show_suggestions` | bool | ✓ optional | `true` or `false` — defaults to `true` if missing |

---

## SECTION 2: Title & Epithet

After frontmatter body:

1. `# {{VampireName}}` — H1, matches frontmatter `vampire`
2. `*A Thousand Year Old Vampire*` — exact subtitle
3. `> *{{epithet}}*` — blockquote

---

## SECTION 3: ⚰ Marks Section

Must contain `## ⚰ Marks`. Each entry:
```
- {{description}} *(concealed: {{how}})*
```

---

## SECTION 4: 🧠 Memories Section

Must contain `## 🧠 Memories`. Each memory:
```
### Memory {{N}} — {{theme}}
1. {{experience 1}}
2. {{experience 2}}
3. {{experience 3}}
```

**Rules:** max 5 memories, max 3 exp each, numbering resets per memory.
Forgotten memories: full strikethrough on header AND all experiences.

---

## SECTION 5: 📖 Diary Section

Must contain `## 📖 Diary`. If `diary_exists: false` → `*No diary yet.*`.

---

## SECTION 6: ⚔ Skills Section

Table with `| Skill | Status |` column. States:
- `✅ unchecked` — available
- `☑ checked` — spent
- ~~`{{struck}}`~~ — `~~lost~~` — gone

**Status values must be exactly one of the above.** No variants, no typos.

---

## SECTION 7: 🏚 Resources Section

Table with `| Resource | Type | Status |` columns. States:
- ✅ active, ~~Name~~ + ~~lost~~ gone
- Type: `portable` or `📍 stationary`

**Type values must be exactly `portable` or `📍 stationary`. Status must be ✅ active or ~~lost~~.**

---

## SECTION 8: 👥 Characters Section

Two subsections: `### Mortals` and `### Immortals`.
Living: `**Name** — desc`. Dead: `~~**Name**~~ — ~~desc~~ *(dust)*`

---

## SECTION 9: 📜 Journal Section (SOURCE OF TRUTH)

Each turn entry:
```
### Turn {{N}} — Prompt {{P}}, Entry {{E}}
*{verified prompt text from prompts.json exactly as written}*

{{player's experience or journal prose}}

**Changes:** {{mechanical summary}}
```

**MANDATORY validation rules:**

| Test | Check |
|------|-----|
| **J-01** | Header line starts with `### Turn` |
| **J-02** | Header contains `Prompt` keyword and number (P ≥ 1) |
| **J-03** | Header contains `Entry` keyword and number (E ≥ 1) |
| **J-04** | `Turn` numbers are in reverse order (newest first, oldest last) |
| **J-05** | `P` (Prompt) matches frontmatter `current_prompt` |
| **J-06** | The italicised prompt text on the first line of each Journal entry matches `prompts.json` for the (P, E) pair exactly (whitespace-normalised). The prompt text in the Journal IS a verified copy of the book's text, not a player paraphrase. |
| **J-07** | `**Changes:**` line present with content |
| **J-08** | Entry separated by `---` before next Turn |
| **J-09** | The top Journal entry must end with either `*Awaiting resolution.*` (unresolved) or **Changes:** content (resolved). |
| **J-10** | If the top Journal entry has `*Awaiting resolution.*`, it is the current unresolved prompt. `current_prompt` frontmatter must match this entry's Prompt number. |
| **J-11** | Every Memory N referenced by name or number in Journal prose must correspond to an active (non-struck) or explicitly struck Memory header. |
| **J-12** | Every Skill or Resource name referenced in a `**Changes:**` line must exist in the correct section (Skills or Resources) with a status consistent with the change described (e.g., "Checked *X*" → Skill X has `☑ checked`). |
| **J-13** | Every Journal entry is a complete triad: (1) italicised prompt line, (2) prose paragraph, (3) `**Changes:**` line. No empty or partial entries. |

---

## SECTION 10: Epitaph (conditional)

If `game_over: true`, `## ⚰ Epitaph` section above Journal.

---

## SECTION 11: Awaiting-Resolution Marker

The topmost Journal entry's last line within the entry block must be one of:
- `*Awaiting resolution.*` — the prompt has been delivered but not yet resolved by the player.
- `---` — the prompt has been resolved; the entry contains full prose and **Changes:**.

A resolved prompt entry never contains `*Awaiting resolution.*`. An unresolved prompt entry never contains `**Changes:**`.

---

## SECTION 12: Trailing Metadata

`*Last played: YYYY-MM-DD*` after last turn.

---

## SECTION 13: Section Ordering (MANDATORY)

Section order must be:
```
1. YAML Frontmatter
2. H1 + subtitle + epithet
3. ⚰ Marks
4. 🧠 Memories
5. 📖 Diary
6. ⚔ Skills
7. 🏚 Resources
8. 👥 Characters
9. ⚰ Epitaph (only if game_over: true)
10. 📜 Journal
```

---

## SECTION 14: CAPACITY LIMITS (MANDATORY)

| Test | Check |
|------|-----|
| **C-01** | Entry limit per prompt: prompts 1–71 may have at most 3 `### Turn` entries; prompts 72–80 have at most 1. |
| **C-02** | Each active (non-struck) Memory section holds at most 3 Experiences. Struck memories follow the same rule but are informational only. |
| **C-03** | The Diary holds at most 4 Memories (counted from `### Memory N —` headers under `## 📖 Diary`). |
| **C-04** | Total memory budget: active (non-struck) memories + diary memories must equal 5 or less. Once all 5 active memories have been created, no new active memories may be added until one is moved to the Diary or struck. |
| **C-05** | Experiences in each active Memory are numbered sequentially 1, 2, 3 — no gaps, no duplicates. Struck memories follow the same rule when intact. |
| **C-06** | Memories in the Diary are numbered sequentially from 1 — no gaps, no duplicates. |
| **C-07** | No duplicate Skill names within the Skills table. |
| **C-08** | No duplicate Resource names within the Resources table. |

---

## SECTION 15: GAME LOGIC RULES

| Test | Check |
|------|-----|
| **G-01** | If any Journal entry has Prompt P ≥ 72, `game_over` must be `true` and `game_completed` must have a date (not `""`). |
| **G-02** | If the note is post-character-creation (has at least one Journal entry with `*Awaiting resolution.*` or `**Changes:**`), Memory 5 must exist as a non-struck header (`### Memory 5 —` without `~~`). |
| **G-03** | If Memory N appears in the Diary section, its header in the active Memories section MUST carry the `*(in diary)*` tag on the same header line (e.g., `### Memory N — theme *(in diary)*`). |
| **G-04** | If Memory N appears in the Diary section, its header in the active Memories section MUST NOT be struck through (no `~~### Memory N~~`). |
| **G-05** | A Memory header's `theme` value must be non-empty in all contexts (active, diary, struck). |
| **G-06** | Each Marks entry must contain both a description AND a concealment method (`*(concealed: ...)*`). No marks without concealment. |
| **G-07** | Each Resource row must have a Type value of exactly `portable` or `📍 stationary`. No empty Type fields. |

---

## CROSS-REFERENCE CHECKS

| Test | Check |
|------|-----|
| **CR-01** | `prompts_resolved` == number of `### Turn` headings in Journal |
| **CR-02** | `current_prompt` == Prompt P of the final turn heading |
| **CR-03** | `diary_exists: true` ↔ Diary section has real content (not "No diary yet") |
| **CR-04** | Memory header numbering has no gaps in active memories |
| **CR-05** | `game_over: true` ↔ `game_completed` has a date (not `""`) |
| **CR-06** | `game_over: false` ↔ `game_completed` is `""` |
| **CR-07** | `modified` ≥ `created` |
| **CR-08** | If the top Journal entry has `*Awaiting resolution.*`, the number of resolved turns (those with `**Changes:**`) matches `prompts_resolved` |
| **CR-09** | If `*(in diary)*` appears on an active Memory header, that Memory N MUST also appear in the Diary section's memory list. |
| **CR-10** | If `*(in diary)*` appears on active Memory N, Memory N must NOT be struck through in the active Memories section (strikethrough on header means forgotten, not diary). |
| **CR-11** | `diary_exists: false` ↔ Diary section shows `*No diary yet.*` or contains zero Memory headers. |

---

## PROMPT TEXT VERIFICATION (against `prompts.json`)

| Test | Check |
|------|-----|
| **P-01** | The italicised prompt text in **every** Journal entry matches `prompts.json` for the (P, E) pair (whitespace-normalised). All Journal entries contain verified prompt text from the JSON. |

**Prompt text matching procedure:**

1. Load `prompts.json`. Navigate `pages[page].prompt_number == P` to find the correct prompt page.
2. Within that page, find `entries[E-1].text` (0-indexed into entries).
3. Normalise both strings: strip leading/trailing whitespace, collapse all consecutive whitespace (including newlines) to a single space.
4. Compare the normalised Journal italicised prompt text with the normalised JSON text. They must be identical.
5. If they differ in any meaningful way (omitted/added words, wrong resource/skill names, altered punctuation that changes meaning), **this is a drift failure**.

---

## VALIDATION PROTOCOL

1. Run **every** test (F-01 through F-15, T-01 through T-03, M-01 through M-02, ME-01 through ME-05, D-01 through D-03, S-01 through S-02, R-01 through R-03, CH-01 through CH-04, C-01 through C-08, G-01 through G-07, J-01 through J-13, E-01 through E-02, O-01, TM-01, CR-01 through CR-11, P-01) — no skipping.
2. Run the deterministic script `scripts/validate_vault.py` for full validation — it exits 0 on all-pass, 1 on any failure.
3. If **all pass** → the note is consistent.
4. If **any fail** → the note is drifted — fix it silently, then re-run the full checklist from the top.
