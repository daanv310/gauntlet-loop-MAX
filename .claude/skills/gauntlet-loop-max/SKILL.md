---
name: gauntlet-loop-max
description: Two-gate quality loop for work that tests alone can't prove is good - UI, animation, dashboards, landing pages, copy, scripts, titles, thumbnails, docs, decks. Gate 1 proves it works (spec + quality review by an independent reviewer, fix rounds, severity-ranked findings). Gate 2 proves it's good (a fresh, harsh critic compares ours against a real reference blind, A/B, no scores, names the biggest gap; loop up to 6 max-effort rounds until ours wins). Use whenever visual or written work is built by subagents, when the user says "/gauntlet-loop-max", "gauntlet loop max", "gauntlet this", "loop until it beats X", "make it match/beat this reference", or hands over an image or link to replicate - even if they don't name this skill.
---

# Gauntlet Loop MAX

Two gates, in this order, for every piece of work:

1. **Correctness gate** — the classic subagent-driven loop: the spec and plan are met, tests are
   green, an independent reviewer lists issues by severity (Critical / Important / Minor), and fix
   rounds run until no Critical or Important issue is left. It proves the work **functions**.
2. **Taste gate** — the gauntlet: a critic with fresh context compares ours against a **real bar**
   blind and picks the better one. It proves the work is **good**.

Why both: a severity review finds defects but never asks "is this as good as the reference?". A
blind comparison asks exactly that, but can't see a broken permission check or a missing test.
Correctness goes first, because there is no point polishing something the fix is about to change.

Use only the correctness gate for code with no visual or written surface (migrations, workers,
business rules, APIs). There, the bar is the test suite and the gauntlet adds nothing.

## 1. The bar (the whole trick)

Without a real bar, the critic invents the comparison and approves everything. A bar must be:

- **Named:** one specific thing ("the dashboard mockup the user sent", "Stripe's pricing page"),
  not a category ("beautiful dashboards").
- **Fetchable:** the critic can actually open it — an image file, a screenshot of the live page at
  the same viewport, the published text, the repo. If it can't be obtained, it isn't a bar.
- **Comparable:** the two can sit side by side and a judge can pick one.

Order of preference:
1. A reference the user provided (image, link, file). It wins.
2. The best in class, live, captured at the same viewport and theme.
3. The previous version of the same piece (the floor: never regress).

If there is a measurable half (load time, AA contrast, bundle size, word count, pass rate), name
it next to the reference. Taste plus a number beats taste alone.

When the reference has flaws (a typo in a mockup, a repeated axis label), the critic judges "which
one is closer to the reference's intent and better finished", and the list of improvements the
user approved becomes part of the bar.

Record the bar in the progress ledger before starting: `Bar: <piece> — <bar> — <where to get it>`.

## 2. Small, judgeable pieces

Split the task into pieces that can be improved and judged on their own (a dashboard: header,
KPI row, revenue chart, views chart, call-to-action card, lists, side column; a piece of writing:
the opening, each explanation, the close). A piece that is too big turns into "it depends" and the
critic can't choose.

## 3. The blind critic

Every round uses a **new** critic (a subagent with no history, on the most capable model, ideally
different from the builder's). It never knows which version is ours.

Build the blind pair with the bundled script (it shuffles and hides the key):

```bash
python3 <skill-dir>/scripts/blind_pair.py <our_capture> <bar_capture> <output_dir>
```

The script writes `A.<ext>` and `B.<ext>` into `<output_dir>` and prints the key **only to you**
(`ours=A` or `ours=B`). Keep the key in the ledger; never pass it to the critic. Both files must
share the same format (convert first, e.g. `sips -s format png in.webp --out in.png` on macOS).

Critic prompt (adapt the context, keep the answer format):

```
You are a harsh critic. Praise is not useful. Open both files: <dir>/A.png and <dir>/B.png.
They show <what the piece is> at the same size. <Criterion: which one is better finished / closer
to the intent X / a non-expert understands faster.>
Pick ONE. No score, no tie.
Answer exactly:
WINNER: A | B
BIGGEST_GAP: <the single biggest difference that makes the loser lose, one concrete, actionable sentence>
NEXT_GAPS: <1 or 2 more differences, each concrete and actionable, or "none">
WHY: <up to 3 sentences>
```

Why binary and score-free: scores drift upward every round even without real improvement; a choice
between two doesn't. Why the biggest gap first: the most important fix lands first and the builder
doesn't scatter small tweaks. The next gaps let one round fix more, as long as they don't conflict
with the biggest one.

## 4. The loop

For each piece, after the correctness gate:

1. Capture ours and the bar at the same viewport and theme (or the same span of text).
2. Build the blind pair and call a new critic.
3. **Won** (the critic picked ours): the piece passes. Ledger:
   `Gauntlet: <piece> — won round <R> (key ours=<A|B>)`.
4. **Lost:** send the builder (resumed, with its context) the `BIGGEST_GAP`, the `NEXT_GAPS`, the
   bar file and the current capture. It fixes the biggest gap fully and the next gaps that don't
   conflict, reruns the tests that cover the change, and recaptures.
5. **No regressions:** from round 2 on, also compare the new version against the previous one,
   blind. If the previous one wins, revert the change and send a different gap.
6. Repeat.

### Maximum effort every round (to win before the cap)

The goal is to win as early as possible, ideally by round 3. Every round is expensive, so none is a
warm-up:

- **Builder at full strength:** the most capable model available and maximum reasoning effort.
- **Study the bar before touching anything:** the builder opens the bar and its own capture side by
  side and measures what it can (spacing, heights, font sizes, radii, colours, alignment, rhythm of
  the text), writes the differences down, and only then fixes. Looking at the bar is allowed; what
  the builder never does is decide whether it won.
- **Fix in depth:** solve the cause, not the screenshot. If the gap is "weak hierarchy", rework the
  whole type scale, not one heading.
- **A strong, new critic every round:** most capable model, clean context, no knowledge of earlier
  rounds.
- **Rounds 4 to 6:** if it still hasn't won, replace the builder with a new one (more capable, if
  available), handing over the bar, the current capture, every gap raised so far and what was
  tried. Fresh eyes often see what the previous builder couldn't.

### The cap (a deliberate difference from the original gauntlet loop)

The original gauntlet loop runs until it wins, with no limit. This one caps at **6 rounds per
piece** (configurable). Reason: rounds consume usage limits and budget, and an unbounded loop can
stall everything else. When the cap is reached without a win:

- record `Gauntlet: <piece> — lost at cap <N> — gap: <BIGGEST_GAP> — Ruling: <accept / defer / ask the user>`;
- if the gap depends on a user decision (change the reference, accept a difference), bring it to
  them at the end with both captures side by side;
- never claim it "matches the reference" when it didn't win.

## 5. How it fits a subagent-driven plan

- **Plan:** tag visual and written tasks with their bar and pieces, e.g. "Task 7 — Gauntlet: bar =
  `design/reference/dashboard.png`; pieces = header, KPIs, revenue, views, CTA, lists, videos".
- **Execution:** brief → builder → spec + quality review (with fix rounds) → **gauntlet per piece**
  → task complete.
- **Final branch review:** include the ledger's `Gauntlet:` lines; pieces lost at the cap show up
  for triage.
- **Final message to the user:** besides the rulings you made, list each piece's gauntlet result
  and, for any lost ones, the remaining gap.

## 6. What breaks a gauntlet

- A vague bar: the critic approves everything. The most common failure.
- The builder judging its own work, or a critic that has seen earlier rounds.
- A critic that scores instead of choosing, or knows which one is ours.
- Comparing captures at different sizes, themes or data (the choice becomes about the size, not
  the quality). Same viewport, same theme, similar data.
- Sending the builder a pile of gaps with no priority.
- Skipping the correctness gate because "it won visually".
