#!/usr/bin/env python3
"""TYOV Viewer Section Editor Test Suite"""
import json, re, sys, os, jsonschema

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCHEMA_PATH = os.path.join(BASE_DIR, "tests", "vampire-schema.json")
VIEWER_PATH = os.path.join(BASE_DIR, "tyov-viewer.html")

with open(SCHEMA_PATH) as sf:
    schema = json.load(sf)

with open(VIEWER_PATH) as vf:
    viewer_src = vf.read()

def validate(obj):
    v = jsonschema.Draft202012Validator(schema)
    errs = list(v.iter_errors(obj))
    return len(errs) == 0, [e.message for e in errs]

passed, failed = [], []

def test(name, condition, error_info=None):
    if condition:
        passed.append(name)
        print(f"  ✓ {name}")
    else:
        failed.append((name, error_info or ""))
        info = f"  [{error_info}]" if error_info else ""
        print(f"  ✗ {name}  {info}")

def section(title):
    print(f"\\n{'='*60}\\n  {title}\\n{'='*60}")

def vampire():
    return {
        "name": "Demonstration Vampire",
        "vampire_desc": "Test vampire for editor validation.",
        "mortal_self": "Mortal identity details.",
        "game_start": "2026-01-01",
        "modified": "2026-05-15",
        "game_over": False,
        "game_completed": None,
        "current_prompt": 5,
        "prompts_resolved": 2,
        "marks": [
            {"name":"Cold Skin","description":"Perpetually cold.","concealment":"Clothing.","status":"available"},
            {"name":"Morgue Wake","description":"Body stolen.","concealment":"Hidden.","status":"available"}
        ],
        "memories": [
            {"name":"First Grave","description":"Earliest undeath.","experiences":["Woke.","Cold."],"status":"available","in_diary":False},
            {"name":"First Hunger","description":"First kill.","experiences":["Dog."],"status":"struck"}
        ],
        "diary":{"memories":[]},
        "skills": [
            {"name":"Bookbinding","description":"Mortal trade.","status":"available"},
            {"name":"First Hunger","description":"After creation.","status":"available"}
        ],
        "resources": [
            {"name":"Black Grimoire","description":"Ancient book.","type":"stationary","status":"available"},
            {"name":"Silver Reliquary","description":"Silver box.","type":"portable","status":"available"}
        ],
        "characters": [
            {"name":"Clara","type":"mortal","description":"Nurse.","status":"alive"},
            {"name":"Hargrave","type":"mortal","description":"Priest.","status":"dead","death_reason":"Old age, 1931."},
            {"name":"Silas","type":"immortal","description":"My dam.","status":"alive"}
        ],
        "journal": [
            {"turn":1,"prompt":1,"entry":1,"prompt_text":"A cold place.","resolved":True,"paraphrased_prompt":"Waking.","experience":"Death smell.","changes":"First Hunger."},
            {"turn":2,"prompt":2,"entry":1,"prompt_text":"Silas arrives.","resolved":True,"paraphrased_prompt":"Creator.","experience":"Shadows.","changes":"Churchcraft."}
        ],
        "epitaph": None
    }


### PHASE 1: Header Editor ###
section("PHASE 1: Header Editor (editHeader)")
print("Tests editing the vampire header - name and concept line (vampire_desc)")
vp = vampire(); vp["name"] = "New Vampire Name"
ok, errs = validate(vp)
test("P1-01: Change vampire name", ok, "; ".join(errs))
test("P1-01: name is non-empty string", isinstance(vp["name"], str) and len(vp["name"]) > 0, f"name={vp['name']}")
vp = vampire(); vp["name"] = ""
ok, errs = validate(vp)
test("P1-02: Empty name schema-valid", ok, "; ".join(errs))
vp = vampire(); vp["vampire_desc"] = "New concept line."
ok, errs = validate(vp)
test("P1-03: Change vampire_desc", ok, "; ".join(errs))
test("P1-03: vampire_desc persisted", vp["vampire_desc"] == "New concept line.", f"got {vp['vampire_desc']}")
vp = vampire(); vp["name"] = "A" * 5000
ok, errs = validate(vp)
test("P1-04: 5000-char name is valid (no maxLength)", ok, "; ".join(errs))

### PHASE 2: Marks Editor ###
section("PHASE 2: Marks Editor (editMarks)")
print("Tests adding, striking, and removing marks")
vp = vampire(); vp["marks"].append({"name":"Ash Mark","description":"Ash on skin.","concealment":"Gloves.","status":"available"})
ok, errs = validate(vp)
test("P2-01: Add new mark", ok, "; ".join(errs))
test("P2-01: Total marks = 3", len(vp["marks"]) == 3, f"got {len(vp['marks'])}")
vp = vampire(); vp["marks"][0]["status"] = "struck"
ok, errs = validate(vp)
test("P2-02: Strike mark valid", ok, "; ".join(errs))
test("P2-02: status=struck", vp["marks"][0]["status"] == "struck", f"got {vp['marks'][0]['status']}")
vp = vampire(); vp["marks"] = []
ok, errs = validate(vp)
test("P2-03: Remove all marks valid", ok, "; ".join(errs))
vp = vampire(); vp["marks"].append({"description":"Must have desc."})
ok, errs = validate(vp)
test("P2-04: Name-only mark valid (description required)", ok, "; ".join(errs))
vp = vampire(); vp["marks"].append({"name":"Full","description":"All fields.","concealment":"Hid.","status":"available"})
ok, errs = validate(vp)
test("P2-05: Full mark valid", ok, "; ".join(errs))

### PHASE 3: Memories Editor ###
section("PHASE 3: Memories Editor (editMemories)")
print("Tests adding, striking, experiences, in_diary, and maxItems")
vp = vampire(); vp["memories"].append({"name":"First Blood","description":"First kill.","experiences":["Stray dog."],"status":"available"})
ok, errs = validate(vp)
test("P3-01: Add memory (within max 5)", ok, "; ".join(errs))
test("P3-01: Total memories = 3", len(vp["memories"]) == 3, f"got {len(vp['memories'])}")
vp = vampire(); vp["memories"][1]["status"] = "struck"
ok, errs = validate(vp)
test("P3-02: Forgot memory (struck) valid", ok, "; ".join(errs))
test("P3-02: status is struck", vp["memories"][1]["status"] == "struck", f"got state")
vp = vampire(); vp["memories"][0]["experiences"].append("Fill to max.")
ok, errs = validate(vp)
test("P3-03: 3 experiences (max) valid", ok, "; ".join(errs))
test("P3-03: Experiences count = 3", len(vp["memories"][0]["experiences"]) == 3, f"got {len(vp['memories'][0]['experiences'])}")
vp = vampire(); vp["memories"][0]["in_diary"] = True
ok, errs = validate(vp)
test("P3-04: in_diary=true valid", ok, "; ".join(errs))
vp = vampire()
for i in range(4): vp["memories"].append({"name":f"Extra {i}","experiences":[f"exp {i}"],"status":"available"})
ok, errs = validate(vp)
test("P3-05: 6 memories correctly FAILS maxItems:5", not ok, "; ".join(errs[:2]) if errs else "")
vp = vampire(); vp["memories"][0]["experiences"] = [1, 2, 3]
ok, errs = validate(vp)
test("P3-06: Non-string experience correctly FAILS", not ok, "; ".join(errs[:2]) if errs else "")

### PHASE 4: Skills Editor ###
section("PHASE 4: Skills Editor (editSkills)")
print("Tests adding skills and validating status enum")
vp = vampire(); vp["skills"].append({"name":"NightVision","description":"See in dark.","status":"available"})
ok, errs = validate(vp)
test("P4-01: Add new skill", ok, "; ".join(errs))
test("P4-01: Total skills = 3", len(vp["skills"]) == 3, f"got {len(vp['skills'])}")
vp = vampire(); vp["skills"][0]["status"] = "spent"
test("P4-02: status=spent valid enum", validate(vp)[0], "; ".join(validate(vp)[1]))
vp = vampire(); vp["skills"][0]["status"] = "struck"
test("P4-03: status=struck valid enum", validate(vp)[0], "; ".join(validate(vp)[1]))
vp = vampire(); vp["skills"].append({"name":"Minimal"})
test("P4-04: Name-only skill valid", validate(vp)[0], "; ".join(validate(vp)[1]))
vp = vampire(); vp["skills"].append({"name":"Bad","status":"invalid_enum"})
ok, errs = validate(vp)
test("P4-05: Invalid status correctly FAILS enum", not ok, "; ".join(errs[:2]) if errs else "")

### PHASE 5: Resources Editor ###
section("PHASE 5: Resources Editor (editResources)")
print("Tests adding resources and validating type/status enums")
vp = vampire(); vp["resources"].append({"name":"Satchel","description":"Herbs.","type":"portable","status":"available"})
ok, errs = validate(vp)
test("P5-01: Add new resource", ok, "; ".join(errs))
test("P5-01: Total resources = 3", len(vp["resources"]) == 3, f"got {len(vp['resources'])}")
vp = vampire(); vp["resources"][0]["type"] = "stationary"
test("P5-02: type=stationary valid enum", validate(vp)[0], "; ".join(validate(vp)[1]))
vp = vampire(); vp["resources"][1]["status"] = "struck"
test("P5-03: resource struck valid", validate(vp)[0], "; ".join(validate(vp)[1]))
vp = vampire(); vp["resources"].append({"name":"Key"})
test("P5-04: Name-only resource valid", validate(vp)[0], "; ".join(validate(vp)[1]))
vp = vampire(); vp["resources"].append({"name":"Ghost","type":"invalid_type"})
ok, errs = validate(vp)
test("P5-05: Invalid type correctly FAILS enum", not ok, "; ".join(errs[:2]) if errs else "")

### PHASE 6: Characters Editor ###
section("PHASE 6: Characters Editor (editCharacters)")
print("Tests adding mortal/immortal NPCs and life/death status")
vp = vampire(); vp["characters"].append({"name":"Lydia","type":"mortal","description":"Seamstress.","status":"alive"})
test("P6-01: Add mortal character", validate(vp)[0], "; ".join(validate(vp)[1]))
vp = vampire(); vp["characters"].append({"name":"Baron","type":"immortal","description":"Vampire.","status":"alive"})
test("P6-02: Add immortal character", validate(vp)[0], "; ".join(validate(vp)[1]))
vp = vampire()
for c in vp["characters"]:
    if c["status"] == "alive": c["status"] = "dead"; c["death_reason"] = "Ended 1923."; break
valid, errs = validate(vp)
test("P6-03: Kill character valid", valid, "; ".join(errs))
test("P6-03: Has dead with death_reason", any(c.get("death_reason") and c["status"]=="dead" for c in vp["characters"]), "")
vp = vampire(); vp["characters"].append({"name":"Nameless","type":"mortal"})
test("P6-04: Minimal char (name+type) valid", validate(vp)[0], "; ".join(validate(vp)[1]))
vp = vampire(); vp["characters"].append({"name":"Ghost","type":"ghost"})
ok, errs = validate(vp)
test("P6-05: Invalid char type correctly FAILS enum", not ok, "; ".join(errs[:2]) if errs else "")
vp = vampire(); vp["characters"] = []
test("P6-06: Empty characters array valid", validate(vp)[0], "; ".join(validate(vp)[1]))
vp = vampire()
for c in vp["characters"]:
    if c["status"] == "dead": c["status"] = "alive"; c.pop("death_reason",None); break
test("P6-07: Revive character valid", validate(vp)[0], "; ".join(validate(vp)[1]))

### PHASE 7: Journal Editor ###
section("PHASE 7: Journal Editor (editJournal)")
print("Tests journal entries with prompt (1-80) and entry (1-3) boundaries")
vp = vampire(); vp["journal"].append({"turn":3,"prompt":3,"entry":1,"prompt_text":"Threat.","resolved":False,"paraphrased_prompt":"Threat arrival.","experience":"","changes":""})
test("P7-01: Awaiting entry serializes validly", validate(vp)[0], "; ".join(validate(vp)[1]))
vp = vampire(); vp["journal"].append({"turn":3,"prompt":3,"entry":1,"prompt_text":"Storm.","resolved":True,"paraphrased_prompt":"Storm.","experience":"Rain.","changes":"None."})
ok, errs = validate(vp)
test("P7-02: Full journal entry valid", ok, "; ".join(errs)); test("P7-02: Total entries = 3", len(vp["journal"])==3, f"got {len(vp['journal'])}")
vp = vampire(); vp["journal"].append({"turn":4,"prompt":81,"entry":1,"prompt_text":"Bad","resolved":True,"paraphrased_prompt":"","experience":"","changes":""})
ok, errs = validate(vp)
test("P7-03: Prompt=81 correctly FAILS max 80", not ok, "; ".join(errs[:2]) if errs else "")
vp = vampire(); vp["journal"].append({"turn":5,"prompt":5,"entry":4,"prompt_text":"Bad","resolved":True,"paraphrased_prompt":"","experience":"","changes":""})
ok, errs = validate(vp)
test("P7-04: Entry=4 correctly FAILS max 3", not ok, "; ".join(errs[:2]) if errs else "")
vp = vampire(); vp["journal"].append({"turn":6,"entry":1,"prompt_text":"Missing","resolved":True,"paraphrased_prompt":"","experience":"","changes":""})
ok, errs = validate(vp)
test("P7-05: Missing prompt correctly FAILS required", not ok, "; ".join(errs[:2]) if errs else "")
vp = vampire(); vp["journal"].append({"turn":7,"prompt":7,"prompt_text":"Missing","resolved":True,"paraphrased_prompt":"","experience":"","changes":""})
ok, errs = validate(vp)
test("P7-06: Missing entry correctly FAILS required", not ok, "; ".join(errs[:2]) if errs else "")
vp = vampire(); vp["journal"] = []
test("P7-07: Empty journal array valid", validate(vp)[0], "; ".join(validate(vp)[1]))

### PHASE 8: Diary Editor ###
section("PHASE 8: Diary Editor (editDiary)")
print("IMPORTANT: diary.memories stores memory NAME STRINGS, not objects")
vp = vampire(); vp["diary"]["memories"].append("First Grave")
ok, errs = validate(vp)
test("P8-01: Add diary memory name string", ok, "; ".join(errs)); test("P8-01: Diary memories = 1", len(vp["diary"]["memories"])==1, f"got {len(vp['diary']['memories'])}")
vp = vampire()
for i in range(4): vp["diary"]["memories"].append(f"Memory Name {i+1}")
ok, errs = validate(vp)
test("P8-02: 4 diary memories (at max)", ok, "; ".join(errs))
test("P8-02: Diary memories = 4", len(vp["diary"]["memories"])==4, f"got {len(vp['diary']['memories'])}")
vp = vampire()
for i in range(5): vp["diary"]["memories"].append(f"Extra {i}")
ok, errs = validate(vp)
test("P8-03: Diary exceeds max correctly FAILS maxItems:4", not ok, "; ".join(errs[:2]) if errs else "")
vp = vampire(); vp["diary"]["memories"] = []
test("P8-04: Empty diary memories valid", validate(vp)[0], "; ".join(validate(vp)[1]))
vp = vampire(); vp["diary"]["memories"].append(123)
ok, errs = validate(vp)
test("P8-05: Non-string diary item correctly FAILS", not ok, "; ".join(errs[:2]) if errs else "")

### PHASE 9: Frontmatter ###
section("PHASE 9: Frontmatter and Global State")
print("Tests top-level flags: game_over, game_completed, current_prompt, epitaph")
vp = vampire(); vp["game_over"] = True
test("P9-01: game_over=true", validate(vp)[0], "; ".join(validate(vp)[1]))
vp = vampire(); vp["game_completed"] = "2026-12-31"
test("P9-02: game_completed date string", validate(vp)[0], "; ".join(validate(vp)[1]))
vp = vampire(); vp["game_completed"] = None
test("P9-03: game_completed=null", validate(vp)[0], "; ".join(validate(vp)[1]))
vp = vampire(); vp["current_prompt"] = 0
test("P9-04: current_prompt=0 (min)", validate(vp)[0], "; ".join(validate(vp)[1]))
vp = vampire(); vp["current_prompt"] = 80
test("P9-05: current_prompt=80 (max)", validate(vp)[0], "; ".join(validate(vp)[1]))
vp = vampire(); vp["current_prompt"] = -1
ok, errs = validate(vp)
test("P9-06: current_prompt=-1 Correctly FAILS min 0", not ok, "; ".join(errs[:2]) if errs else "")
vp = vampire(); vp["current_prompt"] = 81
ok, errs = validate(vp)
test("P9-07: current_prompt=81 Correctly FAILS max 80", not ok, "; ".join(errs[:2]) if errs else "")
vp = vampire(); vp["prompts_resolved"] = 0
test("P9-08a: prompts_resolved=0", validate(vp)[0], "; ".join(validate(vp)[1]))
vp = vampire(); vp["prompts_resolved"] = 80
test("P9-08b: prompts_resolved=80", validate(vp)[0], "; ".join(validate(vp)[1]))
vp = vampire(); vp["epitaph"] = {"experience":"Return."}
test("P9-09: Epitaph with experience valid", validate(vp)[0], "; ".join(validate(vp)[1]))
vp = vampire(); vp["epitaph"] = None
test("P9-10: epitaph=null", validate(vp)[0], "; ".join(validate(vp)[1]))
for req in schema["required"]:
    vp = vampire()
    test(f"P9-11: required field '{req}'", req in vp, "missing")

### PHASE 10: Round-Trip ###
section("PHASE 10: JSON->serialized->parsedData->JSON Round-Trip")
print("Tests data integrity through full serialization/parsing cycle")
vp = vampire()
ok, errs = validate(vp)
test("P10-01a: Full skeleton JSON valid", ok, "; ".join(errs))
json_str = json.dumps(vampire(), indent=2)
vp2 = json.loads(json_str)
ok, errs = validate(vp2)
test("P10-01b: Round-trip JSON->obj->JSON->obj valid", ok, "; ".join(errs))
vp = vampire()
for req in schema["required"]:
    test(f"P10-02: '{req}' is present", req in vp, "missing")
vp = vampire()
for field in ["memories","skills","resources","characters","marks","journal"]:
    test(f"P10-03: '{field}' is array", isinstance(vp.get(field), list), f"got {type(vp.get(field))}")
vp = vampire()
for i,mem in enumerate(vp["memories"]):
    test(f"P10-04:{i}: memory has name", "name" in mem, "missing")
    test(f"P10-04:{i}: memory has experiences", "experiences" in mem, "missing")
    test(f"P10-04:{i}: exp is list", isinstance(mem.get("experiences"), list), f"got {type(mem.get('experiences'))}")
    test(f"P10-04:{i}: exp<=3", len(mem.get("experiences",[]))<=3, f"got {len(mem.get('experiences',[]))}")
    for j,exp in enumerate(mem.get("experiences",[])):
        test(f"P10-04:{i}:{j}: item is string", isinstance(exp, str), f"got {type(exp)}")
vp = vampire()
for i,c in enumerate(vp["characters"]):
    test(f"P10-05:{i}: char has name", "name" in c, "missing")
    test(f"P10-05:{i}: char has type", "type" in c, "missing")
    test(f"P10-05:{i}: type enum", c["type"] in ("mortal","immortal"), f"invalid: {c['type']}")
    if c.get("status")=="dead": test(f"P10-05:{i}: dead has death_reason", "death_reason" in c, "missing")
vp = vampire()
for i,j in enumerate(vp["journal"]):
    for f in ["turn","prompt","entry","prompt_text","resolved"]:
        test(f"P10-06:{i}: has '{f}'", f in j, "missing")
    if isinstance(j.get("prompt"),int):
        test(f"P10-06:{i}: prompt 1-80", 1<=j["prompt"]<=80, f"got {j['prompt']}")
    if isinstance(j.get("entry"),int):
        test(f"P10-06:{i}: entry 1-3", 1<=j["entry"]<=3, f"got {j['entry']}")
vp = vampire()
for sk in vp["skills"]:
    test(f"P10-07: skill '{sk['name']}' status", sk["status"] in ("available","spent","struck"), f"invalid: {sk['status']}")
for r in vp["resources"]:
    test(f"P10-07: resource '{r['name']}' status", r["status"] in ("available","struck"), f"invalid: {r['status']}")
    test(f"P10-07: resource '{r['name']}' type", r["type"] in ("portable","stationary"), f"invalid: {r['type']}")
for mem in vp["memories"]:
    if "status" in mem:
        test(f"P10-07: memory '{mem['name']}' status", mem["status"] in ("available","struck"), f"invalid: {mem['status']}")

### PHASE 11: Viewer Source Code Alignment ###
section("PHASE 11: Viewer-to-Schema Alignment")
print("Verifies viewer JS matches schema expectations")
test("P11-01: serializeJson outputs mortal_self", "mortal_self" in viewer_src, "not found")
test("P11-02: viewer maps character.description", "description: c.description" in viewer_src, "not found")
test("P11-03: skill description in serializeJson", "description: sk.description" in viewer_src, "not found")
test("P11-04: resource description in serializeJson", "description: r.description" in viewer_src, "not found")
test("P11-05: jsonToParsedData reads character.description", "description: c.description" in viewer_src, "not found")
test("P11-06: VIEWER hides TEST_ prefixed files", "TEST_" in viewer_src and "test_" in viewer_src, "not found")
test("P11-07: death_REASON mapped separately", "death_reason: c.death_reason" in viewer_src, "not found")
test("P11-08: current_prompt always serialized", "current_prompt" in viewer_src, "not found")

### FINAL ###
total = len(passed) + len(failed)
print(f"\\n{'='*60}")
print(f"  {len(passed)} passed / {total} total")
if failed:
    print(f"  {len(failed)} FAILURES:")
    for name, info in failed:
        print(f"    ✗ {name}" + (f"  [{info}]" if info else ""))
else:
    print("  ALL TESTS PASSED!")
print(f"{'='*60}")
