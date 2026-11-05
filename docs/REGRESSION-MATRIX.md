# Hidden-fighter regression matrix

Generated from `docs/regression-matrix.json` by `tools/check_regression_matrix.py --write`. Do not edit by hand.

A PASS is a maintainer attestation based on a run record. It is not a tool result: the checker validates the shape of records and cannot confirm that a cell was played. Every cell stays UNTESTED until maintainer run records exist.

## Status and evidence

- UNTESTED: no result entry. Default for every applicable cell; carries no evidence.
- PASS: a result entry pointing to a run record. The maintainer observed every pass criterion in the cell on that run.
- FAIL: a result entry, a run record and a symptom (printable ASCII, 1-200 characters). Stays FAIL until a later run passes the cell.
- N/A: derived from a not-applicable rule. Never appears in results.
- Earlier user reports (results softlock, T-pose, death restoring Bowser) lack run metadata and stay UNTESTED until a maintainer run confirms them.

Run records: one per session, one language and one plugin state per run, plugin state fixed at boot. Fields: id, commit, pack SHA-256, plugin SHA-256 (none when the plugin is off), language, runtime (kind and version), date, tester handle and evidence ID.

Evidence: `EV-YYYYMMDD-NNN` maps to clips and logs in a private log outside the repository, or is a comment URL on the project issue tracker. The Random control records which fighter Random drew in that log.

## Dimensions

Cell id: `subject.mode.lifecycle.language.plugin`. The full product is 7 x 5 x 6 x 3 x 2 = 1260 cells: 756 applicable and 504 N/A.

- Subjects: f58 Giga Bowser, f59 Wario-Man, f60 Giga Mac, f61 Mega Lucario (Final Smash forms), and the controls roster, random and mii.
- Modes: css, training, versus, cpu, rematch.
- Lifecycles: ko, respawn, sudden-death, timeout, results, select.
- Languages: en-us (US English), fr, es. Columns show the setting; the exact console label is kept in the private evidence log.
- Plugin: on or off. Plugin ON for 59-61 is inert by design: a PASS means no regression, not that the feature works.
- `select` is an added sixth lifecycle: open CSS, cursor over additions, select, cancel, reselect, check portrait and nameplate render. The five issue lifecycles are match events and CSS has no match, so `select` is the only CSS lifecycle. The maintainer may reject it.
- Out of scope: Fighting Mii 62-64, because they are enemy actors and issue #7 names only forms 58-61.
- Out of scope: combinations of hidden forms; a separate table is planned.

## Controls

- roster: a regular roster fighter, chosen from the normal CSS.
- random: the Random slot. A PASS does not prove that a hidden form was drawn; the run must record which fighter Random drew.
- mii: a standard Mii from the normal Mii menu. Not the candidate rows 62-64.

## Not applicable rules

| # | Mode | Lifecycle | Reason |
| --- | --- | --- | --- |
| 1 | css | ko | No match runs in CSS, so no match event can occur. |
| 2 | css | respawn | No match runs in CSS, so no match event can occur. |
| 3 | css | sudden-death | No match runs in CSS, so no match event can occur. |
| 4 | css | timeout | No match runs in CSS, so no match event can occur. |
| 5 | css | results | No match runs in CSS, so no match event can occur. |
| 6 | training | sudden-death | Training has no stocks, no timer, no results screen. |
| 7 | training | timeout | Training has no stocks, no timer, no results screen. |
| 8 | training | results | Training has no stocks, no timer, no results screen. |
| 9 | training | select | Selection is exercised once in the css row; match modes start from it. |
| 10 | versus | select | Selection is exercised once in the css row; match modes start from it. |
| 11 | cpu | select | Selection is exercised once in the css row; match modes start from it. |
| 12 | rematch | select | Selection is exercised once in the css row; match modes start from it. |

## Pass criteria

Every applicable cell needs all of the following on its run:

- Selected fighter, costume, model, controls, portrait and nameplate are correct before and after the event.
- No freeze, buzzing audio, T-pose or results softlock.
- The form is still the form after KO, respawn, timeout or results.
- CPU cells: the form plays as CPU at least once and as a player once.
- Team results where the mode allows.
- The cell procedure fixes the rule presets (stock, timer, sudden death) so the event occurs.

## Run register

| Run | Commit | Pack SHA-256 | Plugin SHA-256 | Language | Runtime | Date | Tester | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |

No runs recorded.

## Summary

| Status | Cells |
| --- | --- |
| UNTESTED | 756 |
| PASS | 0 |
| FAIL | 0 |
| N/A | 504 |
| Total | 1260 |

PASS results per build (commit and candidate SHA-256). A PASS on another build is not evidence for the current one.

No runs recorded.

## Matrix

### f58 Giga Bowser, plugin on

| Mode | Lifecycle | US English | French | Spanish |
| --- | --- | --- | --- | --- |
| css | ko | N/A #1 | N/A #1 | N/A #1 |
| css | respawn | N/A #2 | N/A #2 | N/A #2 |
| css | sudden-death | N/A #3 | N/A #3 | N/A #3 |
| css | timeout | N/A #4 | N/A #4 | N/A #4 |
| css | results | N/A #5 | N/A #5 | N/A #5 |
| css | select | UNTESTED | UNTESTED | UNTESTED |
| training | ko | UNTESTED | UNTESTED | UNTESTED |
| training | respawn | UNTESTED | UNTESTED | UNTESTED |
| training | sudden-death | N/A #6 | N/A #6 | N/A #6 |
| training | timeout | N/A #7 | N/A #7 | N/A #7 |
| training | results | N/A #8 | N/A #8 | N/A #8 |
| training | select | N/A #9 | N/A #9 | N/A #9 |
| versus | ko | UNTESTED | UNTESTED | UNTESTED |
| versus | respawn | UNTESTED | UNTESTED | UNTESTED |
| versus | sudden-death | UNTESTED | UNTESTED | UNTESTED |
| versus | timeout | UNTESTED | UNTESTED | UNTESTED |
| versus | results | UNTESTED | UNTESTED | UNTESTED |
| versus | select | N/A #10 | N/A #10 | N/A #10 |
| cpu | ko | UNTESTED | UNTESTED | UNTESTED |
| cpu | respawn | UNTESTED | UNTESTED | UNTESTED |
| cpu | sudden-death | UNTESTED | UNTESTED | UNTESTED |
| cpu | timeout | UNTESTED | UNTESTED | UNTESTED |
| cpu | results | UNTESTED | UNTESTED | UNTESTED |
| cpu | select | N/A #11 | N/A #11 | N/A #11 |
| rematch | ko | UNTESTED | UNTESTED | UNTESTED |
| rematch | respawn | UNTESTED | UNTESTED | UNTESTED |
| rematch | sudden-death | UNTESTED | UNTESTED | UNTESTED |
| rematch | timeout | UNTESTED | UNTESTED | UNTESTED |
| rematch | results | UNTESTED | UNTESTED | UNTESTED |
| rematch | select | N/A #12 | N/A #12 | N/A #12 |

### f58 Giga Bowser, plugin off

| Mode | Lifecycle | US English | French | Spanish |
| --- | --- | --- | --- | --- |
| css | ko | N/A #1 | N/A #1 | N/A #1 |
| css | respawn | N/A #2 | N/A #2 | N/A #2 |
| css | sudden-death | N/A #3 | N/A #3 | N/A #3 |
| css | timeout | N/A #4 | N/A #4 | N/A #4 |
| css | results | N/A #5 | N/A #5 | N/A #5 |
| css | select | UNTESTED | UNTESTED | UNTESTED |
| training | ko | UNTESTED | UNTESTED | UNTESTED |
| training | respawn | UNTESTED | UNTESTED | UNTESTED |
| training | sudden-death | N/A #6 | N/A #6 | N/A #6 |
| training | timeout | N/A #7 | N/A #7 | N/A #7 |
| training | results | N/A #8 | N/A #8 | N/A #8 |
| training | select | N/A #9 | N/A #9 | N/A #9 |
| versus | ko | UNTESTED | UNTESTED | UNTESTED |
| versus | respawn | UNTESTED | UNTESTED | UNTESTED |
| versus | sudden-death | UNTESTED | UNTESTED | UNTESTED |
| versus | timeout | UNTESTED | UNTESTED | UNTESTED |
| versus | results | UNTESTED | UNTESTED | UNTESTED |
| versus | select | N/A #10 | N/A #10 | N/A #10 |
| cpu | ko | UNTESTED | UNTESTED | UNTESTED |
| cpu | respawn | UNTESTED | UNTESTED | UNTESTED |
| cpu | sudden-death | UNTESTED | UNTESTED | UNTESTED |
| cpu | timeout | UNTESTED | UNTESTED | UNTESTED |
| cpu | results | UNTESTED | UNTESTED | UNTESTED |
| cpu | select | N/A #11 | N/A #11 | N/A #11 |
| rematch | ko | UNTESTED | UNTESTED | UNTESTED |
| rematch | respawn | UNTESTED | UNTESTED | UNTESTED |
| rematch | sudden-death | UNTESTED | UNTESTED | UNTESTED |
| rematch | timeout | UNTESTED | UNTESTED | UNTESTED |
| rematch | results | UNTESTED | UNTESTED | UNTESTED |
| rematch | select | N/A #12 | N/A #12 | N/A #12 |

### f59 Wario-Man, plugin on

| Mode | Lifecycle | US English | French | Spanish |
| --- | --- | --- | --- | --- |
| css | ko | N/A #1 | N/A #1 | N/A #1 |
| css | respawn | N/A #2 | N/A #2 | N/A #2 |
| css | sudden-death | N/A #3 | N/A #3 | N/A #3 |
| css | timeout | N/A #4 | N/A #4 | N/A #4 |
| css | results | N/A #5 | N/A #5 | N/A #5 |
| css | select | UNTESTED | UNTESTED | UNTESTED |
| training | ko | UNTESTED | UNTESTED | UNTESTED |
| training | respawn | UNTESTED | UNTESTED | UNTESTED |
| training | sudden-death | N/A #6 | N/A #6 | N/A #6 |
| training | timeout | N/A #7 | N/A #7 | N/A #7 |
| training | results | N/A #8 | N/A #8 | N/A #8 |
| training | select | N/A #9 | N/A #9 | N/A #9 |
| versus | ko | UNTESTED | UNTESTED | UNTESTED |
| versus | respawn | UNTESTED | UNTESTED | UNTESTED |
| versus | sudden-death | UNTESTED | UNTESTED | UNTESTED |
| versus | timeout | UNTESTED | UNTESTED | UNTESTED |
| versus | results | UNTESTED | UNTESTED | UNTESTED |
| versus | select | N/A #10 | N/A #10 | N/A #10 |
| cpu | ko | UNTESTED | UNTESTED | UNTESTED |
| cpu | respawn | UNTESTED | UNTESTED | UNTESTED |
| cpu | sudden-death | UNTESTED | UNTESTED | UNTESTED |
| cpu | timeout | UNTESTED | UNTESTED | UNTESTED |
| cpu | results | UNTESTED | UNTESTED | UNTESTED |
| cpu | select | N/A #11 | N/A #11 | N/A #11 |
| rematch | ko | UNTESTED | UNTESTED | UNTESTED |
| rematch | respawn | UNTESTED | UNTESTED | UNTESTED |
| rematch | sudden-death | UNTESTED | UNTESTED | UNTESTED |
| rematch | timeout | UNTESTED | UNTESTED | UNTESTED |
| rematch | results | UNTESTED | UNTESTED | UNTESTED |
| rematch | select | N/A #12 | N/A #12 | N/A #12 |

### f59 Wario-Man, plugin off

| Mode | Lifecycle | US English | French | Spanish |
| --- | --- | --- | --- | --- |
| css | ko | N/A #1 | N/A #1 | N/A #1 |
| css | respawn | N/A #2 | N/A #2 | N/A #2 |
| css | sudden-death | N/A #3 | N/A #3 | N/A #3 |
| css | timeout | N/A #4 | N/A #4 | N/A #4 |
| css | results | N/A #5 | N/A #5 | N/A #5 |
| css | select | UNTESTED | UNTESTED | UNTESTED |
| training | ko | UNTESTED | UNTESTED | UNTESTED |
| training | respawn | UNTESTED | UNTESTED | UNTESTED |
| training | sudden-death | N/A #6 | N/A #6 | N/A #6 |
| training | timeout | N/A #7 | N/A #7 | N/A #7 |
| training | results | N/A #8 | N/A #8 | N/A #8 |
| training | select | N/A #9 | N/A #9 | N/A #9 |
| versus | ko | UNTESTED | UNTESTED | UNTESTED |
| versus | respawn | UNTESTED | UNTESTED | UNTESTED |
| versus | sudden-death | UNTESTED | UNTESTED | UNTESTED |
| versus | timeout | UNTESTED | UNTESTED | UNTESTED |
| versus | results | UNTESTED | UNTESTED | UNTESTED |
| versus | select | N/A #10 | N/A #10 | N/A #10 |
| cpu | ko | UNTESTED | UNTESTED | UNTESTED |
| cpu | respawn | UNTESTED | UNTESTED | UNTESTED |
| cpu | sudden-death | UNTESTED | UNTESTED | UNTESTED |
| cpu | timeout | UNTESTED | UNTESTED | UNTESTED |
| cpu | results | UNTESTED | UNTESTED | UNTESTED |
| cpu | select | N/A #11 | N/A #11 | N/A #11 |
| rematch | ko | UNTESTED | UNTESTED | UNTESTED |
| rematch | respawn | UNTESTED | UNTESTED | UNTESTED |
| rematch | sudden-death | UNTESTED | UNTESTED | UNTESTED |
| rematch | timeout | UNTESTED | UNTESTED | UNTESTED |
| rematch | results | UNTESTED | UNTESTED | UNTESTED |
| rematch | select | N/A #12 | N/A #12 | N/A #12 |

### f60 Giga Mac, plugin on

| Mode | Lifecycle | US English | French | Spanish |
| --- | --- | --- | --- | --- |
| css | ko | N/A #1 | N/A #1 | N/A #1 |
| css | respawn | N/A #2 | N/A #2 | N/A #2 |
| css | sudden-death | N/A #3 | N/A #3 | N/A #3 |
| css | timeout | N/A #4 | N/A #4 | N/A #4 |
| css | results | N/A #5 | N/A #5 | N/A #5 |
| css | select | UNTESTED | UNTESTED | UNTESTED |
| training | ko | UNTESTED | UNTESTED | UNTESTED |
| training | respawn | UNTESTED | UNTESTED | UNTESTED |
| training | sudden-death | N/A #6 | N/A #6 | N/A #6 |
| training | timeout | N/A #7 | N/A #7 | N/A #7 |
| training | results | N/A #8 | N/A #8 | N/A #8 |
| training | select | N/A #9 | N/A #9 | N/A #9 |
| versus | ko | UNTESTED | UNTESTED | UNTESTED |
| versus | respawn | UNTESTED | UNTESTED | UNTESTED |
| versus | sudden-death | UNTESTED | UNTESTED | UNTESTED |
| versus | timeout | UNTESTED | UNTESTED | UNTESTED |
| versus | results | UNTESTED | UNTESTED | UNTESTED |
| versus | select | N/A #10 | N/A #10 | N/A #10 |
| cpu | ko | UNTESTED | UNTESTED | UNTESTED |
| cpu | respawn | UNTESTED | UNTESTED | UNTESTED |
| cpu | sudden-death | UNTESTED | UNTESTED | UNTESTED |
| cpu | timeout | UNTESTED | UNTESTED | UNTESTED |
| cpu | results | UNTESTED | UNTESTED | UNTESTED |
| cpu | select | N/A #11 | N/A #11 | N/A #11 |
| rematch | ko | UNTESTED | UNTESTED | UNTESTED |
| rematch | respawn | UNTESTED | UNTESTED | UNTESTED |
| rematch | sudden-death | UNTESTED | UNTESTED | UNTESTED |
| rematch | timeout | UNTESTED | UNTESTED | UNTESTED |
| rematch | results | UNTESTED | UNTESTED | UNTESTED |
| rematch | select | N/A #12 | N/A #12 | N/A #12 |

### f60 Giga Mac, plugin off

| Mode | Lifecycle | US English | French | Spanish |
| --- | --- | --- | --- | --- |
| css | ko | N/A #1 | N/A #1 | N/A #1 |
| css | respawn | N/A #2 | N/A #2 | N/A #2 |
| css | sudden-death | N/A #3 | N/A #3 | N/A #3 |
| css | timeout | N/A #4 | N/A #4 | N/A #4 |
| css | results | N/A #5 | N/A #5 | N/A #5 |
| css | select | UNTESTED | UNTESTED | UNTESTED |
| training | ko | UNTESTED | UNTESTED | UNTESTED |
| training | respawn | UNTESTED | UNTESTED | UNTESTED |
| training | sudden-death | N/A #6 | N/A #6 | N/A #6 |
| training | timeout | N/A #7 | N/A #7 | N/A #7 |
| training | results | N/A #8 | N/A #8 | N/A #8 |
| training | select | N/A #9 | N/A #9 | N/A #9 |
| versus | ko | UNTESTED | UNTESTED | UNTESTED |
| versus | respawn | UNTESTED | UNTESTED | UNTESTED |
| versus | sudden-death | UNTESTED | UNTESTED | UNTESTED |
| versus | timeout | UNTESTED | UNTESTED | UNTESTED |
| versus | results | UNTESTED | UNTESTED | UNTESTED |
| versus | select | N/A #10 | N/A #10 | N/A #10 |
| cpu | ko | UNTESTED | UNTESTED | UNTESTED |
| cpu | respawn | UNTESTED | UNTESTED | UNTESTED |
| cpu | sudden-death | UNTESTED | UNTESTED | UNTESTED |
| cpu | timeout | UNTESTED | UNTESTED | UNTESTED |
| cpu | results | UNTESTED | UNTESTED | UNTESTED |
| cpu | select | N/A #11 | N/A #11 | N/A #11 |
| rematch | ko | UNTESTED | UNTESTED | UNTESTED |
| rematch | respawn | UNTESTED | UNTESTED | UNTESTED |
| rematch | sudden-death | UNTESTED | UNTESTED | UNTESTED |
| rematch | timeout | UNTESTED | UNTESTED | UNTESTED |
| rematch | results | UNTESTED | UNTESTED | UNTESTED |
| rematch | select | N/A #12 | N/A #12 | N/A #12 |

### f61 Mega Lucario, plugin on

| Mode | Lifecycle | US English | French | Spanish |
| --- | --- | --- | --- | --- |
| css | ko | N/A #1 | N/A #1 | N/A #1 |
| css | respawn | N/A #2 | N/A #2 | N/A #2 |
| css | sudden-death | N/A #3 | N/A #3 | N/A #3 |
| css | timeout | N/A #4 | N/A #4 | N/A #4 |
| css | results | N/A #5 | N/A #5 | N/A #5 |
| css | select | UNTESTED | UNTESTED | UNTESTED |
| training | ko | UNTESTED | UNTESTED | UNTESTED |
| training | respawn | UNTESTED | UNTESTED | UNTESTED |
| training | sudden-death | N/A #6 | N/A #6 | N/A #6 |
| training | timeout | N/A #7 | N/A #7 | N/A #7 |
| training | results | N/A #8 | N/A #8 | N/A #8 |
| training | select | N/A #9 | N/A #9 | N/A #9 |
| versus | ko | UNTESTED | UNTESTED | UNTESTED |
| versus | respawn | UNTESTED | UNTESTED | UNTESTED |
| versus | sudden-death | UNTESTED | UNTESTED | UNTESTED |
| versus | timeout | UNTESTED | UNTESTED | UNTESTED |
| versus | results | UNTESTED | UNTESTED | UNTESTED |
| versus | select | N/A #10 | N/A #10 | N/A #10 |
| cpu | ko | UNTESTED | UNTESTED | UNTESTED |
| cpu | respawn | UNTESTED | UNTESTED | UNTESTED |
| cpu | sudden-death | UNTESTED | UNTESTED | UNTESTED |
| cpu | timeout | UNTESTED | UNTESTED | UNTESTED |
| cpu | results | UNTESTED | UNTESTED | UNTESTED |
| cpu | select | N/A #11 | N/A #11 | N/A #11 |
| rematch | ko | UNTESTED | UNTESTED | UNTESTED |
| rematch | respawn | UNTESTED | UNTESTED | UNTESTED |
| rematch | sudden-death | UNTESTED | UNTESTED | UNTESTED |
| rematch | timeout | UNTESTED | UNTESTED | UNTESTED |
| rematch | results | UNTESTED | UNTESTED | UNTESTED |
| rematch | select | N/A #12 | N/A #12 | N/A #12 |

### f61 Mega Lucario, plugin off

| Mode | Lifecycle | US English | French | Spanish |
| --- | --- | --- | --- | --- |
| css | ko | N/A #1 | N/A #1 | N/A #1 |
| css | respawn | N/A #2 | N/A #2 | N/A #2 |
| css | sudden-death | N/A #3 | N/A #3 | N/A #3 |
| css | timeout | N/A #4 | N/A #4 | N/A #4 |
| css | results | N/A #5 | N/A #5 | N/A #5 |
| css | select | UNTESTED | UNTESTED | UNTESTED |
| training | ko | UNTESTED | UNTESTED | UNTESTED |
| training | respawn | UNTESTED | UNTESTED | UNTESTED |
| training | sudden-death | N/A #6 | N/A #6 | N/A #6 |
| training | timeout | N/A #7 | N/A #7 | N/A #7 |
| training | results | N/A #8 | N/A #8 | N/A #8 |
| training | select | N/A #9 | N/A #9 | N/A #9 |
| versus | ko | UNTESTED | UNTESTED | UNTESTED |
| versus | respawn | UNTESTED | UNTESTED | UNTESTED |
| versus | sudden-death | UNTESTED | UNTESTED | UNTESTED |
| versus | timeout | UNTESTED | UNTESTED | UNTESTED |
| versus | results | UNTESTED | UNTESTED | UNTESTED |
| versus | select | N/A #10 | N/A #10 | N/A #10 |
| cpu | ko | UNTESTED | UNTESTED | UNTESTED |
| cpu | respawn | UNTESTED | UNTESTED | UNTESTED |
| cpu | sudden-death | UNTESTED | UNTESTED | UNTESTED |
| cpu | timeout | UNTESTED | UNTESTED | UNTESTED |
| cpu | results | UNTESTED | UNTESTED | UNTESTED |
| cpu | select | N/A #11 | N/A #11 | N/A #11 |
| rematch | ko | UNTESTED | UNTESTED | UNTESTED |
| rematch | respawn | UNTESTED | UNTESTED | UNTESTED |
| rematch | sudden-death | UNTESTED | UNTESTED | UNTESTED |
| rematch | timeout | UNTESTED | UNTESTED | UNTESTED |
| rematch | results | UNTESTED | UNTESTED | UNTESTED |
| rematch | select | N/A #12 | N/A #12 | N/A #12 |

### roster Regular roster, plugin on

| Mode | Lifecycle | US English | French | Spanish |
| --- | --- | --- | --- | --- |
| css | ko | N/A #1 | N/A #1 | N/A #1 |
| css | respawn | N/A #2 | N/A #2 | N/A #2 |
| css | sudden-death | N/A #3 | N/A #3 | N/A #3 |
| css | timeout | N/A #4 | N/A #4 | N/A #4 |
| css | results | N/A #5 | N/A #5 | N/A #5 |
| css | select | UNTESTED | UNTESTED | UNTESTED |
| training | ko | UNTESTED | UNTESTED | UNTESTED |
| training | respawn | UNTESTED | UNTESTED | UNTESTED |
| training | sudden-death | N/A #6 | N/A #6 | N/A #6 |
| training | timeout | N/A #7 | N/A #7 | N/A #7 |
| training | results | N/A #8 | N/A #8 | N/A #8 |
| training | select | N/A #9 | N/A #9 | N/A #9 |
| versus | ko | UNTESTED | UNTESTED | UNTESTED |
| versus | respawn | UNTESTED | UNTESTED | UNTESTED |
| versus | sudden-death | UNTESTED | UNTESTED | UNTESTED |
| versus | timeout | UNTESTED | UNTESTED | UNTESTED |
| versus | results | UNTESTED | UNTESTED | UNTESTED |
| versus | select | N/A #10 | N/A #10 | N/A #10 |
| cpu | ko | UNTESTED | UNTESTED | UNTESTED |
| cpu | respawn | UNTESTED | UNTESTED | UNTESTED |
| cpu | sudden-death | UNTESTED | UNTESTED | UNTESTED |
| cpu | timeout | UNTESTED | UNTESTED | UNTESTED |
| cpu | results | UNTESTED | UNTESTED | UNTESTED |
| cpu | select | N/A #11 | N/A #11 | N/A #11 |
| rematch | ko | UNTESTED | UNTESTED | UNTESTED |
| rematch | respawn | UNTESTED | UNTESTED | UNTESTED |
| rematch | sudden-death | UNTESTED | UNTESTED | UNTESTED |
| rematch | timeout | UNTESTED | UNTESTED | UNTESTED |
| rematch | results | UNTESTED | UNTESTED | UNTESTED |
| rematch | select | N/A #12 | N/A #12 | N/A #12 |

### roster Regular roster, plugin off

| Mode | Lifecycle | US English | French | Spanish |
| --- | --- | --- | --- | --- |
| css | ko | N/A #1 | N/A #1 | N/A #1 |
| css | respawn | N/A #2 | N/A #2 | N/A #2 |
| css | sudden-death | N/A #3 | N/A #3 | N/A #3 |
| css | timeout | N/A #4 | N/A #4 | N/A #4 |
| css | results | N/A #5 | N/A #5 | N/A #5 |
| css | select | UNTESTED | UNTESTED | UNTESTED |
| training | ko | UNTESTED | UNTESTED | UNTESTED |
| training | respawn | UNTESTED | UNTESTED | UNTESTED |
| training | sudden-death | N/A #6 | N/A #6 | N/A #6 |
| training | timeout | N/A #7 | N/A #7 | N/A #7 |
| training | results | N/A #8 | N/A #8 | N/A #8 |
| training | select | N/A #9 | N/A #9 | N/A #9 |
| versus | ko | UNTESTED | UNTESTED | UNTESTED |
| versus | respawn | UNTESTED | UNTESTED | UNTESTED |
| versus | sudden-death | UNTESTED | UNTESTED | UNTESTED |
| versus | timeout | UNTESTED | UNTESTED | UNTESTED |
| versus | results | UNTESTED | UNTESTED | UNTESTED |
| versus | select | N/A #10 | N/A #10 | N/A #10 |
| cpu | ko | UNTESTED | UNTESTED | UNTESTED |
| cpu | respawn | UNTESTED | UNTESTED | UNTESTED |
| cpu | sudden-death | UNTESTED | UNTESTED | UNTESTED |
| cpu | timeout | UNTESTED | UNTESTED | UNTESTED |
| cpu | results | UNTESTED | UNTESTED | UNTESTED |
| cpu | select | N/A #11 | N/A #11 | N/A #11 |
| rematch | ko | UNTESTED | UNTESTED | UNTESTED |
| rematch | respawn | UNTESTED | UNTESTED | UNTESTED |
| rematch | sudden-death | UNTESTED | UNTESTED | UNTESTED |
| rematch | timeout | UNTESTED | UNTESTED | UNTESTED |
| rematch | results | UNTESTED | UNTESTED | UNTESTED |
| rematch | select | N/A #12 | N/A #12 | N/A #12 |

### random Random slot, plugin on

| Mode | Lifecycle | US English | French | Spanish |
| --- | --- | --- | --- | --- |
| css | ko | N/A #1 | N/A #1 | N/A #1 |
| css | respawn | N/A #2 | N/A #2 | N/A #2 |
| css | sudden-death | N/A #3 | N/A #3 | N/A #3 |
| css | timeout | N/A #4 | N/A #4 | N/A #4 |
| css | results | N/A #5 | N/A #5 | N/A #5 |
| css | select | UNTESTED | UNTESTED | UNTESTED |
| training | ko | UNTESTED | UNTESTED | UNTESTED |
| training | respawn | UNTESTED | UNTESTED | UNTESTED |
| training | sudden-death | N/A #6 | N/A #6 | N/A #6 |
| training | timeout | N/A #7 | N/A #7 | N/A #7 |
| training | results | N/A #8 | N/A #8 | N/A #8 |
| training | select | N/A #9 | N/A #9 | N/A #9 |
| versus | ko | UNTESTED | UNTESTED | UNTESTED |
| versus | respawn | UNTESTED | UNTESTED | UNTESTED |
| versus | sudden-death | UNTESTED | UNTESTED | UNTESTED |
| versus | timeout | UNTESTED | UNTESTED | UNTESTED |
| versus | results | UNTESTED | UNTESTED | UNTESTED |
| versus | select | N/A #10 | N/A #10 | N/A #10 |
| cpu | ko | UNTESTED | UNTESTED | UNTESTED |
| cpu | respawn | UNTESTED | UNTESTED | UNTESTED |
| cpu | sudden-death | UNTESTED | UNTESTED | UNTESTED |
| cpu | timeout | UNTESTED | UNTESTED | UNTESTED |
| cpu | results | UNTESTED | UNTESTED | UNTESTED |
| cpu | select | N/A #11 | N/A #11 | N/A #11 |
| rematch | ko | UNTESTED | UNTESTED | UNTESTED |
| rematch | respawn | UNTESTED | UNTESTED | UNTESTED |
| rematch | sudden-death | UNTESTED | UNTESTED | UNTESTED |
| rematch | timeout | UNTESTED | UNTESTED | UNTESTED |
| rematch | results | UNTESTED | UNTESTED | UNTESTED |
| rematch | select | N/A #12 | N/A #12 | N/A #12 |

### random Random slot, plugin off

| Mode | Lifecycle | US English | French | Spanish |
| --- | --- | --- | --- | --- |
| css | ko | N/A #1 | N/A #1 | N/A #1 |
| css | respawn | N/A #2 | N/A #2 | N/A #2 |
| css | sudden-death | N/A #3 | N/A #3 | N/A #3 |
| css | timeout | N/A #4 | N/A #4 | N/A #4 |
| css | results | N/A #5 | N/A #5 | N/A #5 |
| css | select | UNTESTED | UNTESTED | UNTESTED |
| training | ko | UNTESTED | UNTESTED | UNTESTED |
| training | respawn | UNTESTED | UNTESTED | UNTESTED |
| training | sudden-death | N/A #6 | N/A #6 | N/A #6 |
| training | timeout | N/A #7 | N/A #7 | N/A #7 |
| training | results | N/A #8 | N/A #8 | N/A #8 |
| training | select | N/A #9 | N/A #9 | N/A #9 |
| versus | ko | UNTESTED | UNTESTED | UNTESTED |
| versus | respawn | UNTESTED | UNTESTED | UNTESTED |
| versus | sudden-death | UNTESTED | UNTESTED | UNTESTED |
| versus | timeout | UNTESTED | UNTESTED | UNTESTED |
| versus | results | UNTESTED | UNTESTED | UNTESTED |
| versus | select | N/A #10 | N/A #10 | N/A #10 |
| cpu | ko | UNTESTED | UNTESTED | UNTESTED |
| cpu | respawn | UNTESTED | UNTESTED | UNTESTED |
| cpu | sudden-death | UNTESTED | UNTESTED | UNTESTED |
| cpu | timeout | UNTESTED | UNTESTED | UNTESTED |
| cpu | results | UNTESTED | UNTESTED | UNTESTED |
| cpu | select | N/A #11 | N/A #11 | N/A #11 |
| rematch | ko | UNTESTED | UNTESTED | UNTESTED |
| rematch | respawn | UNTESTED | UNTESTED | UNTESTED |
| rematch | sudden-death | UNTESTED | UNTESTED | UNTESTED |
| rematch | timeout | UNTESTED | UNTESTED | UNTESTED |
| rematch | results | UNTESTED | UNTESTED | UNTESTED |
| rematch | select | N/A #12 | N/A #12 | N/A #12 |

### mii Standard Mii, plugin on

| Mode | Lifecycle | US English | French | Spanish |
| --- | --- | --- | --- | --- |
| css | ko | N/A #1 | N/A #1 | N/A #1 |
| css | respawn | N/A #2 | N/A #2 | N/A #2 |
| css | sudden-death | N/A #3 | N/A #3 | N/A #3 |
| css | timeout | N/A #4 | N/A #4 | N/A #4 |
| css | results | N/A #5 | N/A #5 | N/A #5 |
| css | select | UNTESTED | UNTESTED | UNTESTED |
| training | ko | UNTESTED | UNTESTED | UNTESTED |
| training | respawn | UNTESTED | UNTESTED | UNTESTED |
| training | sudden-death | N/A #6 | N/A #6 | N/A #6 |
| training | timeout | N/A #7 | N/A #7 | N/A #7 |
| training | results | N/A #8 | N/A #8 | N/A #8 |
| training | select | N/A #9 | N/A #9 | N/A #9 |
| versus | ko | UNTESTED | UNTESTED | UNTESTED |
| versus | respawn | UNTESTED | UNTESTED | UNTESTED |
| versus | sudden-death | UNTESTED | UNTESTED | UNTESTED |
| versus | timeout | UNTESTED | UNTESTED | UNTESTED |
| versus | results | UNTESTED | UNTESTED | UNTESTED |
| versus | select | N/A #10 | N/A #10 | N/A #10 |
| cpu | ko | UNTESTED | UNTESTED | UNTESTED |
| cpu | respawn | UNTESTED | UNTESTED | UNTESTED |
| cpu | sudden-death | UNTESTED | UNTESTED | UNTESTED |
| cpu | timeout | UNTESTED | UNTESTED | UNTESTED |
| cpu | results | UNTESTED | UNTESTED | UNTESTED |
| cpu | select | N/A #11 | N/A #11 | N/A #11 |
| rematch | ko | UNTESTED | UNTESTED | UNTESTED |
| rematch | respawn | UNTESTED | UNTESTED | UNTESTED |
| rematch | sudden-death | UNTESTED | UNTESTED | UNTESTED |
| rematch | timeout | UNTESTED | UNTESTED | UNTESTED |
| rematch | results | UNTESTED | UNTESTED | UNTESTED |
| rematch | select | N/A #12 | N/A #12 | N/A #12 |

### mii Standard Mii, plugin off

| Mode | Lifecycle | US English | French | Spanish |
| --- | --- | --- | --- | --- |
| css | ko | N/A #1 | N/A #1 | N/A #1 |
| css | respawn | N/A #2 | N/A #2 | N/A #2 |
| css | sudden-death | N/A #3 | N/A #3 | N/A #3 |
| css | timeout | N/A #4 | N/A #4 | N/A #4 |
| css | results | N/A #5 | N/A #5 | N/A #5 |
| css | select | UNTESTED | UNTESTED | UNTESTED |
| training | ko | UNTESTED | UNTESTED | UNTESTED |
| training | respawn | UNTESTED | UNTESTED | UNTESTED |
| training | sudden-death | N/A #6 | N/A #6 | N/A #6 |
| training | timeout | N/A #7 | N/A #7 | N/A #7 |
| training | results | N/A #8 | N/A #8 | N/A #8 |
| training | select | N/A #9 | N/A #9 | N/A #9 |
| versus | ko | UNTESTED | UNTESTED | UNTESTED |
| versus | respawn | UNTESTED | UNTESTED | UNTESTED |
| versus | sudden-death | UNTESTED | UNTESTED | UNTESTED |
| versus | timeout | UNTESTED | UNTESTED | UNTESTED |
| versus | results | UNTESTED | UNTESTED | UNTESTED |
| versus | select | N/A #10 | N/A #10 | N/A #10 |
| cpu | ko | UNTESTED | UNTESTED | UNTESTED |
| cpu | respawn | UNTESTED | UNTESTED | UNTESTED |
| cpu | sudden-death | UNTESTED | UNTESTED | UNTESTED |
| cpu | timeout | UNTESTED | UNTESTED | UNTESTED |
| cpu | results | UNTESTED | UNTESTED | UNTESTED |
| cpu | select | N/A #11 | N/A #11 | N/A #11 |
| rematch | ko | UNTESTED | UNTESTED | UNTESTED |
| rematch | respawn | UNTESTED | UNTESTED | UNTESTED |
| rematch | sudden-death | UNTESTED | UNTESTED | UNTESTED |
| rematch | timeout | UNTESTED | UNTESTED | UNTESTED |
| rematch | results | UNTESTED | UNTESTED | UNTESTED |
| rematch | select | N/A #12 | N/A #12 | N/A #12 |
