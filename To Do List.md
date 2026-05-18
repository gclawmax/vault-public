# Features
---

  ## Editing
  -----
 We don't do it. Can't fix spelling mistakes.

# Future Aspirations
------------------
New Game Wizard or something.
A nicer UX experience for Vampire selection


# Stuff I can't be bothered to fix.
--------------------------
- Losing a mark doesn't have a lost section. Not sure mechanically if it's even a thing. You can restore anyway.
- Resources don't need a description unless you're going to use it properly. They get one on lost, but not visible on creation.
- Edit Journal needs a re-write, or does it? Right now it's a fixed book.

# Schema stuff to sort out before create character should be fixed
-----

Important Field-Level Findings

4. Character typing is bifurcated

Persisted:

characters: [{ type: "mortal" | "immortal" }]

Runtime:

mortals: ParsedCharacter[]
immortals: ParsedCharacter[]

Serialization merges them back together.

5. theme and name are aliases

Reader:

theme: mem.theme || mem.name || ''

Writer always emits:

theme

So:

name is legacy compatibility
canonical persisted field is theme
6. Experiences normalize objects to strings

Input accepted:

["text"]

or

[{ "text": "..." }]

Runtime always becomes:

string[]

Writer emits only strings.

So object-form experiences are legacy-compatible but lossy.

7. Journal resolution logic is tricky

Reader runtime:

awaiting: j.resolved === false

Writer:

resolved:
  j.resolved !== undefined
    ? j.resolved
    : (j.awaiting === undefined ? false : !j.awaiting)

Implications:

runtime primarily uses awaiting
persisted format uses resolved
absent values default to false
8. modified is overwritten on save

Input:

modified

Output:

new Date().toISOString().slice(0, 10)

Meaning:

serialization destroys original timestamp precision
persisted format becomes YYYY-MM-DD
9. frontmatter is synthetic

frontmatter does NOT exist in persisted JSON.

It is runtime-only derived state.

10. rawAfterJournal is runtime-only

Never read.
Never written.

Likely editor/UI scratch state.

Canonical Persisted Model (Recommended)

If you wanted a cleaned canonical schema, it would be:

use theme, never name
use string experiences only
use:
skills:
available
spent
struck
use:
resources:
available
lost
use:
journal.resolved`
use epitaph.experience
remove:
epithet
frontmatter
rawAfterJournal

Those are compatibility/runtime artifacts.