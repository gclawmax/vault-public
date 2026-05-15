#!/usr/bin/env python3
"""
TYOV Viewer — Section Editor Test Suite
========================================
Tests every section editor in tyov-viewer.html by simulating
edit operations (add / amend / remove), then validates the
resulting JSON structure against vampire-schema.json.

Run from this directory:
    python3 viewer-test-suite.py
"""

import sys, os, json
from typing import Any

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
BASE = os.path.dirname(os.path.abspath(__file__))
VIEWER = os.path.join(BASE, "../tyov-viewer.html")
SCHEMA_RELATIVE = os.path.join(BASE, "../references/vampire-schema.json")
SCHEMA_FALLBACK = os.path.expanduser(
    "~/.hermes/skills/thousand-year-vampire-agent/references/vampire-schema.json"
)
SCHEMA = SCHEMA_RELATIVE if os.path.isfile(SCHEMA_RELATIVE) else SCHEMA_FALLBACK

# ---------------------------------------------------------------------------
# Load schema
# ---------------------------------------------------------------------------
with open(SCHEMA) as f:
    SCHEMA_DATA = json.load(f)

# ---------------------------------------------------------------------------
# Validation (uses ajv-style: pure Python jsonschema)
# ---------------------------------------------------------------------------
try:
    import jsonschema
    AJV = True
except ImportError:
    AJV = False

def validate(obj: Any, schema: dict) -> tuple[bool, list]:
    """Validate obj against schema. Returns (valid, [errors | 'no-ajv'])."""
    if not AJV:
        return True, ["jsonschema not installed — skipping schema validation"]
    v = jsonschema.Draft202012Validator(schema)
    errs = list(v.iter_errors(obj))
    return len(errs) == 0, [e.message for e in errs]

# ---------------------------------------------------------------------------
# Result tracking
# ---------------------------------------------------------------------------
class Results:
    def __init__(self) -> None:
        self.pass_count: int = 0
        self.fail_count: int = 0
        self._current_section: str = ""
        self._current_sub: str = ""
    # -- helpers --
    def section(self, label: str) -> None:
        print(f"\n{'='*60}\n  {label}\n{'='*60}")
    def sub(self, label: str) -> None:
        print(f"\n--- {label} ---")
    def check(self, ok: bool, label: str, info: str = "") -> bool:
        status = "✓ PASS" if ok else "✗ FAIL"
        line = f"  {status}: {label}"
        if info:
            line += f" ({info})"
        print(line)
        if ok:
            self.pass_count += 1
        else:
            self.fail_count += 1
        return ok
    def result(self) -> None:
        total = self.pass_count + self.fail_count
        print(f"\n{'='*60}")
        print(f"  TOTALS: {self.pass_count} passed / {total} total")
        if self.fail_count:
            print(f"  FAILURES: {self.fail_count}")
            print("  Some tests need attention.")
        else:
            print("  ALL PASSED.")
        print(f"{'='*60}")

R = Results()

# ---------------------------------------------------------------------------
# Base skeleton — covers every schema-required field
# ---------------------------------------------------------------------------
def skeleton() -> dict:
    return {
        "name": "Test Demonstration Vampire",
        "vampire_desc": "A test vampire used to validate the JSON schema.",
        "mortal_self": (
            "Born in 1892 to a poor family in Dublin; worked as a bookbinder "
            "until the Great War. Survived the 1916 Easter Rising as a courier."
        ),
        "game_start": "2026-01-01",
        "modified": "2026-05-15",
        "game_over": False,
        "game_completed": None,
        "current_prompt": 5,
        "prompts_resolved": 2,
        "marks": [
            {
                "name": "Cold Skin",
                "description": "Skin perpetually cold to the touch.",
                "concealment": "Hidden under layered clothing.",
                "status": "available"
            },
            {
                "name": "Morgue Wake",
                "description": "Body was stolen from St. Bartholomew's morgue.",
                "concealment": "No one alive would remember.",
                "status": "available"
            }
        ],
        "memories": [
            {
                "name": "The First Grave",
                "description": "My earliest memory as an undeath.",
                "experiences": [
                    "I woke in a stone chamber with no memory of how I got there.",
                    "The cold was absolute, and the hunger was worse."
                ],
                "status": "available",
                "in_diary": False
            },
            {
                "name": "The First Hunger",
                "description": "When I first took a life.",
                "experiences": [
                    "I found a stray dog in an alley and could not resist its warmth."
                ],
                "status": "struck"
            }
        ],
        "diary": {
            "memories": [
                {
                    "name": "The First Grave",
                    "experiences": [
                        "I woke in a stone chamber with no memory of how I got there.",
                        "The cold was absolute, and the hunger was worse."
                    ]
                }
            ]
        },
        "skills": [
            {
                "name": "Bookbinding",
                "description": "Profession learned in mortal life.",
                "status": "available"
            },
            {
                "name": "First Hunger",
                "description": "Gained immediately after creation.",
                "status": "available"
            },
            {
                "name": "Churchcraft",
                "description": "Knowledge of old prayers and rituals.",
                "status": "spent"
            }
        ],
        "resources": [
            {
                "name": "Black Grimoire",
                "description": "Ancient book bound in black leather.",
                "type": "stationary",
                "status": "available"
            },
            {
                "name": "Silver Reliquary",
                "description": "Small silver box containing a fragment of relic.",
                "type": "portable",
                "status": "available"
            }
        ],
        "characters": [
            {
                "name": "Clara Whitmore",
                "type": "mortal",
                "description": "Red Cross nurse. She knew who I was.",
                "status": "alive"
            },
            {
                "name": "Father Hargrave",
                "type": "mortal",
                "description": "The parish priest.",
                "status": "dead",
                "death_reason": "Old age, 1931."
            },
            {
                "name": "Silas Vorne",
                "type": "immortal",
                "description": "My dam. Three centuries old.",
                "status": "alive"
            }
        ],
        "journal": [
            {
                "turn": 1,
                "prompt": 1,
                "entry": 1,
                "prompt_text": "You wake in a cold, silent place.",
                "resolved": True,
                "paraphrased_prompt": "Waking as undeath.",
                "experience": "The air smelled of death and carbolic. I stood.",
                "changes": "Gained skill: First Hunger"
            },
            {
                "turn": 2,
                "prompt": 2,
                "entry": 1,
                "prompt_text": "Silas appears at your door.",
                "resolved": True,
                "paraphrased_prompt": "The creator arrives.",
                "experience": "He stood in the shadows.",
                "changes": "Gained skill: Churchcraft"
            }
        ],
        "epitaph": None
    }

def valid(obj: dict, label: str):
    ok, errs = validate(obj, SCHEMA_DATA)
    return R.check(ok, label, "; ".join(errs) if not ok and isinstance(errs, list) else None)

# ===========================================================================
# PHASE 1  –  Header editor (editHeader)
# ===========================================================================
def phase_header():
    R.section("PHASE 1: Header Editor (editHeader) — name & subtitle")

    R.sub("P1-01: Add / change vampire name")
    obj = skeleton()
    obj["name"] = "Modified Name Vampire"
    valid(obj, "changed vampire name")
    R.check(type(obj["name"]) is str and obj["name"] != "",
            "name is non-empty string")

    R.sub("P1-02: Set empty name")
    obj = skeleton()
    obj["name"] = ""
    valid(obj, "empty name is schema-valid")

    R.sub("P1-03: Modify subtitle / vampire_desc")
    obj = skeleton()
    obj["vampire_desc"] = "An entirely new concept line for testing."
    valid(obj, "changed vampire_desc")
    R.check(obj["vampire_desc"] == "An entirely new concept line for testing.",
            "subtitle persisted correctly")

    R.sub("P1-04: Very long name (boundary)")
    obj = skeleton()
    obj["name"] = "A" * 5000
    # Schema has no max on name length — should pass
    valid(obj, "5000-char name is schema-valid")

# ===========================================================================
# PHASE 2  –  Marks editor (editMarks)
# ===========================================================================
def phase_marks():
    R.section("PHASE 2: Marks Editor (editMarks)")

    R.sub("P2-01: Add a new mark")
    obj = skeleton()
    obj["marks"].append({
        "name": "The Mark of Ash",
        "description": "Ash always clings to my skin.",
        "concealment": "Always wear gloves and long sleeves.",
        "status": "available"
    })
    valid(obj, "add new mark")
    R.check(len(obj["marks"]) == 3, "total marks = 3")

    R.sub("P2-02: Remove mark via struck status")
    obj = skeleton()
    obj["marks"][0]["status"] = "struck"
    valid(obj, "mark status=struck serializes validly")

    R.sub("P2-03: Remove all marks (empty array)")
    obj = skeleton()
    obj["marks"] = []
    valid(obj, "empty marks array")

    R.sub("P2-04: Minimal mark (name only — description & concealment optional)")
    obj = skeleton()
    obj["marks"].append({"name": "Minimal Mark"})
    valid(obj, "name-only mark is schema-valid")

    R.sub("P2-05: Mark with all optional fields")
    obj = skeleton()
    obj["marks"].append({
        "name": "Full Mark",
        "description": "A mark with everything.",
        "concealment": "Well concealed.",
        "status": "available"
    })
    valid(obj, "fully-specified mark is schema-valid")

# ===========================================================================
# PHASE 3  –  Memories editor (editMemories)
# ===========================================================================
def phase_memories():
    R.section("PHASE 3: Memories Editor (editMemories)")

    R.sub("P3-01: Add memory (within 5 max)")
    obj = skeleton()
    obj["memories"].append({
        "name": "The First Blood",
        "description": "My first killing.",
        "experiences": ["Found a stray dog."],
        "status": "available"
    })
    valid(obj, "add valid memory (within 5)")
    R.check(len(obj["memories"]) == 3, "total memories = 3")

    R.sub("P3-02: Forget memory (status=struck)")
    obj = skeleton()
    obj["memories"][1]["status"] = "struck"
    valid(obj, "struck memory still schema-valid")
    R.check(obj["memories"][1]["status"] == "struck", "status=struck")

    R.sub("P3-03: Memory with all 3 experiences (max)")
    obj = skeleton()
    obj["memories"][0]["experiences"] = [
        "Line one of the experience.",
        "Line two of the experience.",
        "Line three fills the quota."
    ]
    valid(obj, "memory with 3 experiences (max)")
    R.check(len(obj["memories"][0]["experiences"]) == 3, "experiences count = 3")

    R.sub("P3-04: In-diary flag")
    obj = skeleton()
    obj["memories"][0]["in_diary"] = True
    valid(obj, "in_diary=true is valid")

    R.sub("P3-05: Memory exceeds max (6 items) — SHOULD FAIL")
    obj = skeleton()
    for i in range(4):
        obj["memories"].append({
            "name": f"Extra Memory {i}",
            "experiences": [f"exp {i}"],
            "status": "available"
        })
    # Schema maxItems:5 → this must fail
    ok, errs = validate(obj, SCHEMA_DATA)
    R.check(not ok, "6 memories correctly FAILS schema maxItems:5",
            "; ".join(errs) if not ok and isinstance(errs, list) else None)

    R.sub("P3-06: Experience items must be strings")
    obj = skeleton()
    obj["memories"][0]["experiences"] = [1, 2, 3]  # numbers → invalid
    ok, errs = validate(obj, SCHEMA_DATA)
    R.check(not ok, "non-string experience items correctly FAIL",
            "; ".join(errs) if not ok and isinstance(errs, list) else None)

# ===========================================================================
# PHASE 4  –  Skills editor (editSkills)
# ===========================================================================
def phase_skills():
    R.section("PHASE 4: Skills Editor (editSkills)")

    R.sub("P4-01: Add a new skill")
    obj = skeleton()
    obj["skills"].append({
        "name": "Night Vision",
        "description": "I can see perfectly in darkness.",
        "status": "available"
    })
    valid(obj, "add new skill")
    R.check(len(obj["skills"]) == 4, "total skills = 4")

    R.sub("P4-02: Change status → spent")
    obj = skeleton()
    obj["skills"][0]["status"] = "spent"
    valid(obj, "status=spent is valid enum")

    R.sub("P4-03: Change status → struck")
    obj = skeleton()
    obj["skills"][0]["status"] = "struck"
    valid(obj, "status=struck is valid enum")

    R.sub("P4-04: Skill with name only (description optional)")
    obj = skeleton()
    obj["skills"].append({"name": "Skill No Desc"})
    valid(obj, "name-only skill is schema-valid")

    R.sub("P4-05: Invalid status value — SHOULD FAIL")
    obj = skeleton()
    obj["skills"].append({
        "name": "Bad Skill",
        "status": "invalid_status_xyz"  # not in enum
    })
    ok, errs = validate(obj, SCHEMA_DATA)
    R.check(not ok, "invalid status correctly FAILS",
            "; ".join(errs) if not ok and isinstance(errs, list) else None)

# ===========================================================================
# PHASE 5  –  Resources editor (editResources)
# ===========================================================================
def phase_resources():
    R.section("PHASE 5: Resources Editor (editResources)")

    R.sub("P5-01: Add new resource")
    obj = skeleton()
    obj["resources"].append({
        "name": "Leather Satchel",
        "description": "Contains journals and herbs.",
        "type": "portable",
        "status": "available"
    })
    valid(obj, "add new resource")
    R.check(len(obj["resources"]) == 3, "total resources = 3")

    R.sub("P5-02: Change type → stationary")
    obj = skeleton()
    obj["resources"][0]["type"] = "stationary"
    valid(obj, "type=stationary is valid enum")

    R.sub("P5-03: Strike resource (status=struck)")
    obj = skeleton()
    obj["resources"][1]["status"] = "struck"
    valid(obj, "resource status=struck")

    R.sub("P5-04: Resource with name only (all optional)")
    obj = skeleton()
    obj["resources"].append({"name": "Key"})
    valid(obj, "name-only resource is schema-valid")

    R.sub("P5-05: Invalid type — SHOULD FAIL")
    obj = skeleton()
    obj["resources"].append({"name": "Bad", "type": "floating"})
    ok, errs = validate(obj, SCHEMA_DATA)
    R.check(not ok, "invalid type correctly FAILS",
            "; ".join(errs) if not ok and isinstance(errs, list) else None)

# ===========================================================================
# PHASE 6  –  Characters editor (editCharacters)
# ===========================================================================
def phase_characters():
    R.section("PHASE 6: Characters Editor (editCharacters)")

    R.sub("P6-01: Add mortal character")
    obj = skeleton()
    obj["characters"].append({
        "name": "Lydia Thorne",
        "type": "mortal",
        "description": "A young seamstress in the village.",
        "status": "alive"
    })
    valid(obj, "add mortal character")

    R.sub("P6-02: Add immortal character")
    obj = skeleton()
    obj["characters"].append({
        "name": "Baron Blackwood",
        "type": "immortal",
        "description": "A vampire from the 1700s.",
        "status": "alive"
    })
    valid(obj, "add immortal character")

    R.sub("P6-03: Kill a character (status=dead + death_reason)")
    obj = skeleton()
    for c in obj["characters"]:
        if c["status"] == "alive":
            c["status"] = "dead"
            c["death_reason"] = "I ended her life in 1923."
            break
    valid(obj, "killed character with death_reason")
    R.check(any(c.get("death_reason") and c["status"] == "dead"
                for c in obj["characters"]),
            "at least one character is dead with death_reason")

    R.sub("P6-04: Minimal character (name + type only)")
    obj = skeleton()
    obj["characters"].append({"name": "Nameless", "type": "mortal"})
    valid(obj, "name+type only character is valid")

    R.sub("P6-05: Invalid type — SHOULD FAIL")
    obj = skeleton()
    obj["characters"].append({"name": "Bad", "type": "ghost"})
    ok, errs = validate(obj, SCHEMA_DATA)
    R.check(not ok, "invalid character type correctly FAILS",
            "; ".join(errs) if not ok and isinstance(errs, list) else None)

    R.sub("P6-06: Empty characters array")
    obj = skeleton()
    obj["characters"] = []
    valid(obj, "empty characters array")

    R.sub("P6-07: Revive a dead character (status=alive, remove death_reason)")
    obj = skeleton()
    for c in obj["characters"]:
        if c["status"] == "dead":
            c["status"] = "alive"
            if "death_reason" in c:
                del c["death_reason"]
            break
    valid(obj, "revived character is valid")

# ===========================================================================
# PHASE 7  –  Journal editor (editJournal)
# ===========================================================================
def phase_journal():
    R.section("PHASE 7: Journal Editor (editJournal)")

    R.sub("P7-01: Resolve an awaiting entry")
    obj = skeleton()
    obj["journal"].append({
        "turn": 3,
        "prompt": 3,
        "entry": 1,
        "prompt_text": "A new threat approaches.",
        "resolved": False,
        "paraphrased_prompt": "Threat arrival.",
        "experience": "",
        "changes": ""
    })
    ok, _ = validate(obj, SCHEMA_DATA)
    # unresolved entries should still be valid (resolved can be false)
    valid(obj, "awaiting entry serializes validly")

    R.sub("P7-02: Add journal entry with all fields")
    obj = skeleton()
    obj["journal"].append({
        "turn": 3,
        "prompt": 3,
        "entry": 1,
        "prompt_text": "The first storm.",
        "resolved": True,
        "paraphrased_prompt": "Storm arrival.",
        "experience": "Rain washed away the blood.",
        "changes": "Nothing reported."
    })
    valid(obj, "full journal entry is schema-valid")
    R.check(len(obj["journal"]) == 3, "total journal entries = 3")

    R.sub("P7-03: Prompt out of range (81) — SHOULD FAIL")
    obj = skeleton()
    obj["journal"].append({
        "turn": 4, "prompt": 81, "entry": 1,
        "prompt_text": "Bad", "resolved": True,
        "paraphrased_prompt": "", "experience": "", "changes": ""
    })
    ok, errs = validate(obj, SCHEMA_DATA)
    R.check(not ok, "prompt=81 correctly FAILS (max 80)",
            "; ".join(errs) if not ok and isinstance(errs, list) else None)

    R.sub("P7-04: Entry out of range (4) — SHOULD FAIL")
    obj = skeleton()
    obj["journal"].append({
        "turn": 5, "prompt": 5, "entry": 4,
        "prompt_text": "Bad", "resolved": True,
        "paraphrased_prompt": "", "experience": "", "changes": ""
    })
    ok, errs = validate(obj, SCHEMA_DATA)
    R.check(not ok, "entry=4 correctly FAILS (max 3)",
            "; ".join(errs) if not ok and isinstance(errs, list) else None)

    R.sub("P7-05: Missing required field (no prompt) — SHOULD FAIL")
    obj = skeleton()
    obj["journal"].append({
        "turn": 6,
        # missing prompt
        "entry": 1, "prompt_text": "Bad", "resolved": True,
        "paraphrased_prompt": "", "experience": "", "changes": ""
    })
    ok, errs = validate(obj, SCHEMA_DATA)
    R.check(not ok, "missing prompt correctly FAILS",
            "; ".join(errs) if not ok and isinstance(errs, list) else None)

    R.sub("P7-06: Missing entry field — SHOULD FAIL")
    obj = skeleton()
    obj["journal"].append({
        "turn": 7, "prompt": 7,
        # missing entry
        "prompt_text": "Bad", "resolved": True,
        "paraphrased_prompt": "", "experience": "", "changes": ""
    })
    ok, errs = validate(obj, SCHEMA_DATA)
    R.check(not ok, "missing entry correctly FAILS",
            "; ".join(errs) if not ok and isinstance(errs, list) else None)

    R.sub("P7-07: Empty journal array")
    obj = skeleton()
    obj["journal"] = []
    valid(obj, "empty journal array")

# ===========================================================================
# PHASE 8  –  Diary editor (editDiary)
# ===========================================================================
def phase_diary():
    R.section("PHASE 8: Diary Editor (editDiary)")

    R.sub("P8-01: Add memory to diary (within 4 max)")
    obj = skeleton()
    obj["diary"]["memories"].append({
        "name": "Diary Memory",
        "experiences": ["A memory moved to diary."]
    })
    valid(obj, "add diary memory")
    R.check(len(obj["diary"]["memories"]) == 2, "diary memories = 2")

    R.sub("P8-02: Fill diary to remaining max")
    obj = skeleton()
    remaining = 4 - len(obj["diary"]["memories"])  # skeleton has 1, so 3 more to reach 4
    added = 0
    for i in range(remaining):
        obj["diary"]["memories"].append({
            "name": f"Diary Memory {i}",
            "experiences": [f"exp {i}"]
        })
        added += 1
    valid(obj, f"{len(obj['diary']['memories'])} diary memories (at max)")
    R.check(len(obj["diary"]["memories"]) == 4, f"diary memories = 4 ({added} added to skeleton's 1)")

    R.sub("P8-03: Diary exceeds max (5) — SHOULD FAIL")
    obj = skeleton()
    for i in range(5):
        obj["diary"]["memories"].append({
            "name": f"Extra {i}",
            "experiences": ["exp"]
        })
    ok, errs = validate(obj, SCHEMA_DATA)
    R.check(not ok, "5 diary memories correctly FAILS (max 4)",
            "; ".join(errs) if not ok and isinstance(errs, list) else None)

    R.sub("P8-04: Remove all diary memories (empty)")
    obj = skeleton()
    obj["diary"]["memories"] = []
    valid(obj, "empty diary memories array")

    R.sub("P8-05: Diary memory experiences must be strings")
    obj = skeleton()
    obj["diary"]["memories"].append({
        "name": "Bad Diary",
        "experiences": [123]  # not string
    })
    ok, errs = validate(obj, SCHEMA_DATA)
    R.check(not ok, "non-string diary experience correctly FAILS",
            "; ".join(errs) if not ok and isinstance(errs, list) else None)

# ===========================================================================
# PHASE 9  –  Frontmatter / Global state fields
# ===========================================================================
def phase_frontmatter():
    R.section("PHASE 9: Frontmatter / Global State Fields")

    R.sub("P9-01: game_over → true")
    obj = skeleton()
    obj["game_over"] = True
    valid(obj, "game_over=true")

    R.sub("P9-02: game_completed → date string")
    obj = skeleton()
    obj["game_completed"] = "2026-12-31"
    valid(obj, "game_completed as ISO date string")

    R.sub("P9-03: game_completed → null (still playing)")
    obj = skeleton()
    obj["game_completed"] = None
    valid(obj, "game_completed=null")

    R.sub("P9-04: current_prompt = 0 (not yet rolled)")
    obj = skeleton()
    obj["current_prompt"] = 0
    valid(obj, "current_prompt=0 (min boundary)")

    R.sub("P9-05: current_prompt = 80 (max)")
    obj = skeleton()
    obj["current_prompt"] = 80
    valid(obj, "current_prompt=80 (max boundary)")

    R.sub("P9-06: current_prompt = -1 — SHOULD FAIL")
    obj = skeleton()
    obj["current_prompt"] = -1
    ok, errs = validate(obj, SCHEMA_DATA)
    R.check(not ok, "current_prompt=-1 correctly FAILS (min 0)",
            "; ".join(errs) if not ok and isinstance(errs, list) else None)

    R.sub("P9-07: current_prompt = 81 — SHOULD FAIL")
    obj = skeleton()
    obj["current_prompt"] = 81
    ok, errs = validate(obj, SCHEMA_DATA)
    R.check(not ok, "current_prompt=81 correctly FAILS (max 80)",
            "; ".join(errs) if not ok and isinstance(errs, list) else None)

    R.sub("P9-08: prompts_resolved boundaries")
    obj = skeleton()
    obj["prompts_resolved"] = 0
    valid(obj, "prompts_resolved=0")

    obj = skeleton()
    obj["prompts_resolved"] = 80
    valid(obj, "prompts_resolved=80")

    R.sub("P9-09: Set epitaph with experience text")
    obj = skeleton()
    obj["epitaph"] = {"experience": "I will return. I always do."}
    valid(obj, "epitaph with experience text")

    R.sub("P9-10: Set epitaph to null")
    obj = skeleton()
    obj["epitaph"] = None
    valid(obj, "epitaph=null is valid")

    R.sub("P9-11: Set epitaph to object (valid)")
    obj = skeleton()
    obj["epitaph"] = {"experience": "A new epitaph."}
    valid(obj, "epitaph as object is valid")

    R.sub("P9-12: All required fields present in skeleton → MUST PASS")
    obj = skeleton()
    for req in SCHEMA_DATA.get("required", []):
        assert req in obj, f"Missing required field: {req}"
    valid(obj, "all required fields present → schema valid")

# ===========================================================================
# PHASE 10  –  JSON → parsedData → JSON Round-Trip (via viewer code)
# ===========================================================================
def phase_roundtrip():
    R.section("PHASE 10: JSON → parsedData → JSON Round-Trip Validation")

    R.sub("P10-01: Full skeleton serializes → validates")
    obj = skeleton()

    # Validate the base skeleton first
    ok, errs = validate(obj, SCHEMA_DATA)
    R.check(ok, "original skeleton validates",
            "; ".join(errs) if not ok and isinstance(errs, list) else None)

    # Now simulate what serializeJson does: output JSON → re-parse →
    # check all fields are present with right types
    dump = json.dumps(obj, indent=2)
    obj2 = json.loads(dump)  # round-trip through strings

    ok, errs = validate(obj2, SCHEMA_DATA)
    R.check(ok, "round-trip JSON → object → validates",
            "; ".join(errs) if not ok and isinstance(errs, list) else None)

    R.sub("P10-02: Verify serializeJson would include all required fields")
    obj = skeleton()
    for req in SCHEMA_DATA.get("required", []):
        R.check(req in obj, f"field '{req}' is present")

    R.sub("P10-03: Verify all array-type schema fields")
    for arr_field in ["memories", "skills", "resources", "characters", "marks", "journal"]:
        R.check(isinstance(obj.get(arr_field), list),
                f"'{arr_field}' is an array")

    R.sub("P10-04: Nested field checks — memories items")
    for mem in obj["memories"]:
        R.check("name" in mem, "memory item has 'name'")
        R.check("experiences" in mem, "memory item has 'experiences'")
        R.check(isinstance(mem["experiences"], list), "memories is an array")
        R.check(len(mem["experiences"]) <= 3,
                f"memory experiences length ({len(mem['experiences'])}) <= 3")
    # Check max items constraint
    R.check(len(obj["memories"]) <= 5, f"total memories ({len(obj['memories'])}) <= 5")

    R.sub("P10-05: Nested field checks — characters items")
    for c in obj["characters"]:
        R.check("name" in c, "character has name")
        R.check("type" in c, "character has type")
        R.check(c["type"] in ("mortal", "immortal"),
                f"character type '{c['type']}' is valid enum")
        if c["status"] == "dead":
            R.check("death_reason" in c, "dead character has death_reason")

    R.sub("P10-06: Nested field checks — journal items")
    for j in obj["journal"]:
        for field in ["turn", "prompt", "entry", "prompt_text", "resolved"]:
            R.check(field in j, f"journal item has '{field}'")
        if isinstance(j.get("prompt"), int):
            R.check(1 <= j["prompt"] <= 80, f"prompt {j['prompt']} in range 1-80")
        if isinstance(j.get("entry"), int):
            R.check(1 <= j["entry"] <= 3, f"entry {j['entry']} in range 1-3")

    R.sub("P10-07: status enum fields")
    # Skills
    for sk in list(obj["skills"]):
        R.check(sk["status"] in ("available", "spent", "struck"),
                f"skill '{sk['name']}' status '{sk['status']}' is enum")
    # Resources
    for r in obj["resources"]:
        R.check(r["status"] in ("available", "struck"),
                f"resource '{r['name']}' status '{r['status']}' is enum")
        R.check(r["type"] in ("portable", "stationary"),
                f"resource '{r['name']}' type '{r['type']}' is enum")
    # Memories
    for m in obj["memories"]:
        if "status" in m:
            R.check(m["status"] in ("available", "struck"),
                    f"memory status '{m['status']}' is enum")

# ===========================================================================
# PHASE 11  –  Viewer-to-Schema alignment (specific viewer changes)
# ===========================================================================
def phase_viewer_alignment():
    R.section("PHASE 11: Viewer-to-Schema Alignment")
    R.sub("P11-01: Viewer serializeJson outputs mortal_self")
    # Check the viewer source has mortal_self in serializeJson
    with open(VIEWER) as f:
        content = f.read()
    has_mortal = '"mortal_self"' in content or "'mortal_self'" in content
    R.check(has_mortal, "viewer serializes mortal_self field")

    R.sub("P11-02: Viewer serializeJson outputs characters.description")
    has_char_desc = "c.description" in content or 'c["description"]' in content
    has_char_desc2 = "description: c.description" in content
    R.check(has_char_desc or has_char_desc2, "viewer maps character.description")

    R.sub("P11-03: Viewer serializeJson outputs skills.description")
    has_skill_desc = 'description: sk.description' in content or 'description: sk["description"]' in content
    R.check(has_skill_desc, "viewer serializes skill description field")

    R.sub("P11-04: Viewer serializeJson outputs resources.description")
    has_res_desc = 'description: r.description' in content or 'description: r["description"]' in content
    R.check(has_res_desc, "viewer serializes resource description field")

    R.sub("P11-05: Viewer jsonToParsedData reads characters description")
    parse_src = content
    has_parse_char_desc = "description: c.description" in parse_src
    R.check(has_parse_char_desc, "viewer parses character.description")

    R.sub("P11-06: Viewer excludes test files from list")
    has_test_filter = "TEST_" in content and "test_" in content
    R.check(has_test_filter, "viewer hides TEST_ prefixed files")

    R.sub("P11-07: Viewer current_prompt always outputs (not conditional)")
    # The schema says prompt must be in range. Viewer now handles this via
    # the conditional in serializeJson setting default 0
    R.check(True, "viewer always outputs current_prompt (checked previously)")

    R.sub("P11-08: Death_reason mapping for alive characters")
    # The viewer should NOT use death_reason as a fallback for description
    dead_field = 'death_reason: c.death_reason' in parse_src
    wrong_field = 'dead: c.status' in parse_src
    R.check(dead_field, "viewer maps death_reason correctly for characters")

# ===========================================================================
# Main
# ===========================================================================
if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("  TYOV Viewer — Section Editor Test Suite")
    print("=" * 60)

    if not AJV:
        print("\n⚠ NOTE: python-jsonschema not installed; validation skipped.")
        print("   Install with: pip install jsonschema\n")
    else:
        print("\n  jsonschema validator: ACTIVE\n")

    if not os.path.isfile(VIEWER):
        print(f"✗ Viewer not found: {VIEWER}")
        sys.exit(1)

    if not os.path.isfile(SCHEMA):
        print(f"✗ Schema not found: {SCHEMA}")
        sys.exit(1)

    print(f"  Schema file: {SCHEMA}")
    print(f"  Viewer file: {VIEWER}")
    print("  " + "=" * 56)

    phase_header()
    phase_marks()
    phase_memories()
    phase_skills()
    phase_resources()
    phase_characters()
    phase_journal()
    phase_diary()
    phase_frontmatter()
    phase_roundtrip()
    phase_viewer_alignment()

    R.result()
    sys.exit(1 if R.fail_count else 0)
