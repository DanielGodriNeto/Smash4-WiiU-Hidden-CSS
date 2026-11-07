# Results, victory and animation resource safety: findings

Refs #4. Report only. This document records repository evidence, open questions and a maintainer test matrix. It does not claim a fix, and it does not name a confirmed crash cause.

Every hypothesis below is **hypothesis, unverified**. Only the maintainer can run the runtime matrix in section 8, using a private dump and a private Cemu log. Nothing here has been run on hardware or in Cemu by the contributor.

Citations are `path:line` in this repository. Game data, path strings and offsets from the maintainer's private dump are not in the repository and are not reproduced here.

## 1. Status and scope

- Question: fighters 58 (Giga Bowser), 59 (Wario-Man), 60 (Giga Mac) and 61 (Mega Lucario) freeze or show a T-pose in some results or victory cases. What resource is involved, and what evidence is still missing?
- Outcome of this pass: documentation only. No code, data, test, checker or build output changed.
- Not claimed: a fix, a crash cause, a working results screen, or any hardware behavior.

## 2. Premise corrections

1. **Stage and build of each reported softlock.** The issue reports a softlock with buzzing before the Results screen, attributed to missing victory animations and size-mismatched skeletons. The repository does not establish that cause. The only recorded buzzing is probe 04, which freezes while loading CSS (`docs/VALIDATION.md:9`; `docs/UI-FAILURE-AUDIT.md:3`). That is a different build and a different stage. The recorded results softlock is probe 03, after a win (`docs/VALIDATION.md:8`). See section 5 for the attribution table.
2. **No path list exists in the repository.** `docs/NATIVE-FINDINGS.md:19` says Bowser has entry and results animation paths and Giga Bowser has none. It gives no path strings. The exact strings exist only in the maintainer's private dump.
3. **"Four forms" means four fighters in one match.** The official preparer writes all seven slots (`tools/prepare_native_candidate.py:144`). It takes only `--out`, `--manifest` and `--report` (`:80-84`). The forms-only profile is in the retired builder (`tools/build.py:186`), which exits before running (`tools/build.py:235-236`). Four-fighter runs therefore use the seven-slot pack with four form fighters selected.
4. **Stale line numbers.** Use the cites in this document. The old plan cited `tools/build.py:213` for the exit and `:52` for the donor tuple; the correct lines are `tools/build.py:235-236` and `:66`.
5. **Stale test count.** `docs/VALIDATION.md:35`, `:36` and `:45` say 36 tests. Current code has 50 test methods in five modules: `test_builder` 21, `test_official_validation` 12, `test_companion_validation` 8, `test_guard_host` 7, `test_ui_path_collisions` 2. The figure 36 is not repeated here. The fix belongs in a later docs pass.
6. **Package allowlist check.** `tools/package_source.py:51-53` checks that the ZIP matches `PUBLIC_FILES` at run time. Two tests read the list: `tests/test_companion_validation.py:61` and `tests/test_guard_host.py:56`.

## 3. Repository facts

| # | Fact | Cite |
|---|---|---|
| F1 | Form-to-base pairs: 58→15, 59→22, 60→41, 61→30 | `companion/form_restore.h:13-18`; `tools/build.py:66`; `docs/NATIVE-FINDINGS.md:13` |
| F2 | A test cross-checks the header pairs against the builder donors | `tests/test_companion_validation.py:63-67` |
| F3 | Native helpers at `0x030BF9C0` and `0x030C1FDC` map forms back to base kinds. They are not patched. Call sites are not established; several look like resource lookup paths | `docs/NATIVE-FINDINGS.md:13` |
| F4 | Initializer hook at `0x02E45558`. Entry kind at +0x10, alternate at +0x14 | `companion/main.c:20`, `:36-37` |
| F5 | Giga assignment signature at `0x02E45708` (4 words, plus 4 entry words). The Cemu experiment changed word `0x02E4570C` (named in `docs/NATIVE-FINDINGS.md:35`; the experiment files are private). Sites for 59, 60 and 61 are not located | `companion/guard.h:17`, `:33`; `companion/main.c:21`; `docs/NATIVE-FINDINGS.md:35`; `docs/RESPAWN-COMPANION.md:32` |
| F6 | Entry and results animation: Bowser has paths, Giga Bowser has none. No path strings are given | `docs/NATIVE-FINDINGS.md:19` |
| F7 | Skeleton sizes, base/form: 8876/8204, 12348/9548, 5404/5964, 7308/9100 bytes. File names and the animation-to-skeleton binding are not given | `docs/NATIVE-FINDINGS.md:19` |
| F8 | Form model folders exist (checked by the preparer): `fighter/<module>/model/body/c00/model.nud`. Modules: koopag, warioman, littlemacg, lucariom | `tools/prepare_native_candidate.py:102-104`; `tools/build.py:16-19` |
| F9 | Donor UI names are Koopa, Wario, Littlemac, Lucario. These are not the base module folder names | `tools/build.py:16-19`; `tools/prepare_native_candidate.py:154` |
| F10 | The official builder writes only the param/UI database and `ui/replace/chr` NUT files. No motion, skeleton, sound or results path is written for any slot | `tools/prepare_native_candidate.py:146-149`, `:176-184` |
| F11 | Every replacement row gets field 5 = 0 | `tools/build.py:81` |
| F12 | The probe labels field 5 "victory". Bowser's donor row has field 5 = 1 in the baseline check | `tools/build_giga_probe.py:24`, `:32` |
| F13 | Probe 03 (separate slot) wrote row 60 with field 5 = 0 (via `edit_database`). Probe 02 also wrote field 5 = 0 on row 16. Probe 03 is the only probe whose result records a win softlock. Field 5 is therefore confounded with the build and not isolated. In the probe 03 (separate-slot) output the script asserts every row except 60 is unchanged, so row 16 keeps field 5 = 1 there (`tools/build_giga_probe.py:54-58`); the generator was read, the probe was not re-run (see section 11) | `tools/build_giga_probe.py:34`, `:36-41`, `:54-58`; `tools/build.py:81`; `docs/VALIDATION.md:7-8` |
| F14 | Probe 02 (Giga in the Bowser slot): training loads and controls pass. No win result is recorded | `docs/VALIDATION.md:7` |
| F15 | Probe 03: death restores Bowser; a later win gives a T-pose and a results softlock. The fighter at the win (Giga or restored Bowser) is not recorded | `docs/VALIDATION.md:8` |
| F16 | In CSS-only builds, death restores Bowser (probes 02 and 03, and candidate07: "A KO still restores Bowser") | `docs/VALIDATION.md:7`, `:8`, `:12` |
| F17 | Giga Bowser uses native cosmetic 201 (Koopag). Wario-Man and Mega Lucario reuse Question and sh_all (203/204) | `docs/NATIVE-FINDINGS.md:7`, `:9`; `tools/build.py:16-19` |
| F18 | Training load and control passed for Giga Bowser, although its entry paths are absent (F6). Absence did not block match start in that test | `docs/VALIDATION.md:7`, `:12`; `docs/NATIVE-FINDINGS.md:19` |
| F19 | A private Cemu log identified the reading thread and a resource path in the candidate06 CSS crash. This is a precedent for path capture | `docs/NATIVE-FINDINGS.md:31` |
| F20 | The first 2,239 common MSC scripts of Bowser and Giga Bowser are identical by opcode. This rules out a difference in those scripts only | `docs/NATIVE-FINDINGS.md:15` |
| F21 | The companion hook runs on any initializer call that matches an enabled pair, so it may affect other transitions | `docs/RESPAWN-COMPANION.md:34` |
| F22 | Mii forms 62-64 are enemy-oriented actors | `docs/MAINTAINER-GUIDE.md:62-63` |
| F23 | "Standalone fighter results behavior is incomplete" and "UI victory fallback does not repair gameplay code" are stated with no location or source | `docs/VALIDATION.md:64` |
| F24 | No repository document names the DB field 5 meaning. The external tutorial mentions "victory/results limitations" and names no field | `docs/SOURCES.md:6` |

## 4. Not provable offline

- N1. Exact results, victory or entry path strings, for any fighter.
- N2. Which resource the softlock requests. This needs the private dump and a private Cemu log.
- N3. Animation-to-skeleton binding and size class.
- N4. Whether the engine falls back to a base file when a form path is missing. If it does, H1 and H2 merge (section 6).
- N5. Whether a copied animation would play. Runtime only.
- N6. Base module folder names (for example koopa). F8 proves only the form folders.
- N7. Meaning of DB field 5.
- N8. Whether any sound or voice bank is involved. The repository has no evidence either way.
- N9. Mii results behavior.
- N10. Every runtime outcome: win, loss, timeout, Sudden Death, buzzing, T-pose, softlock.
- N11. Whether the companion was active in any results test.

## 5. Build and stage attribution of recorded failures

| Reported behavior | Build (probe or candidate) | Stage | Source |
|---|---|---|---|
| Buzzing audio and freeze while loading CSS | Probe 04 (UI probe). Do not use | CSS load | `docs/VALIDATION.md:9`; `docs/UI-FAILURE-AUDIT.md:3` |
| CSS-loading crash; logged count consistent with an invalid size calculation (inference) | Candidate06. Rejected | CSS load | `docs/NATIVE-FINDINGS.md:31` |
| Death restores Bowser | Probes 02, 03; candidate07 | Respawn (after KO) | `docs/VALIDATION.md:7`, `:8`, `:12` |
| Win gives T-pose and results softlock | Probe 03 (separate slot) | Results (after win) | `docs/VALIDATION.md:8` |
| "Freezes upon winning" for Final Smash forms | Not attributed to a build | Results (after win) | `docs/VALIDATION.md:64` |
| Known runtime failures: results softlock, T-pose after a win, freezes on win | Not attributed to a build | Results | `docs/VALIDATION.md:31` |

Consequence: probe 03 is the only recorded results-stage softlock with a named build. Its fighter at the win is not recorded (F15). The two undated lines (`:31`, `:64`) cannot be assigned to a build, and this document does not assign them.

## 6. Resource families

| Family | Form (58/59/60/61) | Base (15/22/41/30) | Evidence | Status |
|---|---|---|---|---|
| Results and victory animation | No path (F6) | Path exists (F6) | `docs/NATIVE-FINDINGS.md:19` | Exact paths: maintainer's private dump only |
| Entry animation | No path (F6) | Path exists (F6) | same | Same. Entry tolerated in training (F18) |
| Skeleton | Sizes 8204, 9548, 5964, 9100 | 8876, 12348, 5404, 7308 | F7 | File names unknown |
| Model folder | `fighter/koopag`, `warioman`, `littlemacg`, `lucariom` (model.nud checked, F8) | Base folders unknown (N6) | F8, F9 | Form side verified by the preparer |
| Kind routing | Helper pairs (F3, F1) | Same pairs | `docs/NATIVE-FINDINGS.md:13` | Call sites unknown |
| Alternate-kind write | 58 site has a signature (F5); 59/60/61 have none | 15 | `companion/guard.h:17` | 59/60/61 unknown |
| DB row field 5 | Set to 0 (F11) | 1 (F12) | `tools/build.py:81` | Meaning unknown (N7) |
| CSS UI donors | `ui/replace/chr/*_<base>_01.nut` (CSS icons, not results) | n/a | `tools/prepare_native_candidate.py:154` | Not a results path |
| Mii actors 62-64 | Enemy modules | Enemy actors (F22) | `tools/build.py:20-22` | No results evidence (N9) |
| Sound, voice, BGM | None in repository | None | N8 | Unknown |

## 7. Hypotheses, ranked by evidence

Each row is **hypothesis, unverified**. The run order differs from the rank: H6 is the cheapest A/B, so it runs first.

| Rank | ID | Hypothesis | For | Against | Decisive runtime result |
|---|---|---|---|---|---|
| 1 | H1 | Hypothesis, unverified. Results code requests a form results or victory path that is absent, with no fallback | F6 (absent paths); the issue's own theory | Entry paths are equally absent and a Training load and control passed (F18), so absence alone is not sufficient | Cemu log at freeze requests an absent Giga results path |
| 2 | H3 | Hypothesis, unverified. Results or victory lookup goes through the base kind (after a KO restore, or via native helpers, F3), so Bowser's animation drives Giga's model | F3; F15 and F16 (win after restored Bowser) | No call site identified (F3); restore evidence is respawn-only | Log requests a base (Bowser) path; a win without any KO behaves differently from a win after a KO |
| 3 | H2 | Hypothesis, unverified. A base animation on a form skeleton of different size gives a T-pose or loader failure | F7 | No animation-to-skeleton map; size is not proof (F7 says so); T-pose only seen after a win | T-pose on Results with no freeze (Results reached) |
| 4 | H6 | Hypothesis, unverified. Field 5 = 0 on new rows disables a victory-related flag | F11, F13 (the probe 03 build had it, but so did probe 02) | Label unsourced (F12, F24); Bowser's own row has field 5 = 1 (no in-game result is recorded for it) | Single-field A/B on a fresh export (field 5 set to the donor value 1, nothing else changed) changes the win result |
| 5 | H5 | Hypothesis, unverified. A missing victory or result sound/voice bank causes buzzing or a loop | Issue reports buzzing | No sound resource anywhere in repository (N8); buzzing is documented only for probe 04 at CSS load | Buzzing at win or timeout only, with a sound path in the log |
| 6 | H4 | Hypothesis, unverified. Standalone form results-state logic is incomplete | `docs/VALIDATION.md:64` | No source or location (F23) | Not testable offline; only the runtime matrix |
| 7 | H7 | Hypothesis, unverified. Placeholder cosmetic reuse (203/204) breaks results | F17 (generic art for Wario-Man and Mega Lucario) | Probe 03 (cosmetic 201) softlocked after a win, but the fighter at the win is unrecorded (F15), so this cannot be confirmed as the sole cause | Affects portraits only; not a softlock discriminator |

Interaction to test, not assume: if the engine falls back to base when a form path is missing (N4), H1 turns into H2 and H3. Do not treat H1 and H2 as separate causes.

## 8. Fallback options (none implemented)

| Option | What | Risk | Verdict |
|---|---|---|---|
| A. Status quo, docs only | Record hypotheses and the runtime matrix | No gameplay risk; softlock remains | Default |
| B. Copy base results, victory or entry animation bytes into form paths | New physical files in the data partition | Skeleton size mismatch may give T-pose or loader failure (F7); duplicates game bytes (private only); RF and patchlist edits proved fragile (`docs/UI-FAILURE-AUDIT.md:5-11`) | Not until H1 or H2 is confirmed |
| C. RF name redirect (form entry points at a base file offset, no copy) | Avoids duplication | Same skeleton risk; RF rebuild risk. Precedent: test05 may leave normal Bowser's portrait blank (`docs/UI-FAILURE-AUDIT.md:7`; `docs/VALIDATION.md:10`) | Not now |
| D. Skip Results, return to CSS | Bypass the screen | Rejected by the issue as blind bypass; needs gameplay or binary change; out of scope | No |
| E. Route base kind into results (companion-style rewrite before results, H3) | Keeps form kind at results | Gameplay code; the only runtime evidence is respawn (F16); the companion must not be bundled with the CSS pack | After H3 evidence, as a separate issue |
| F. Field 5 A/B (H6) | One DB value on new rows | Low risk, but meaning unknown (N7); may change other flags | Maintainer A/B only, from a fresh export; never shipped |
| G. Warning text in install notes | Tell users to avoid match wins with forms | None; does not fix | Partly present: `tools/build_giga_probe.py:96` ("avoid a match win"); `tools/build.py:231` ("Use offline versus/training only") |

**Checker status.** No checker is implemented. The repository has no path strings, so a checker could only run on the maintainer's private dump. The set logic is small and a synthetic test would prove only that logic, not a game fact. Existing gates already cover adjacent checks (`tools/prepare_native_candidate.py:102-104`; `tools/verify_official_candidate.py:99`, `:107-109`, `:116-118`). A checker becomes worth building only if the family comparison must repeat across builds, or if a fallback is chosen and must be enforced. The deferred spec is not included here; it is available on request.

## 9. Maintainer runtime checklist

The maintainer runs this. The contributor does not claim any result.

Preconditions:
- Clean US v304 base and update. One candidate pack only (the seven-slot candidate). No other CSS mods.
- Companion NOT installed. If it is installed, the run does not count for CSS-only claims (F21).
- Record: game update, SDCafiine version, language (US English), profile. No personal paths and no hardware identifiers.
- Enable the Cemu log as in the candidate06 investigation (F19). Keep the log private. Share only path strings, with user-specific path parts removed.
- Do not save replays (`docs/VALIDATION.md:64`).

Runs (each cell at least 2 trials; a freeze means force-quit, then restart):
- Stage 1, one form: Giga Bowser (58) alone. Outcomes: win without any KO, win after one KO, loss, timeout, Sudden Death.
- Stage 2, four fighters in one match (FFA or CPU-filled): 58, 59, 60, 61. Same five outcomes.
- Stage 3: 59, 60, 61 each alone, same five outcomes (mandatory, because each has a different skeleton size and unknown paths; the issue asks for single-form results).
- Control, regular roster: normal Mario and normal Bowser with the pack installed, same five outcomes. Then repeat with the pack removed (stock). Stock and pack results must match. This tests "normal Results is preserved".
- H6 A/B (maintainer only): a fresh export with field 5 of the form rows set to donor value 1, nothing else changed. Repeat Stage 1 win-without-KO. Never install it as the candidate.

Record per run:
- Stage reached: CSS, match load, match, Results, return to CSS.
- Entry pose: normal or T-pose.
- Results: reached yes/no; pose normal or T-pose.
- Audio: normal, silent, buzzing, looping; and at which stage it started.
- Softlock: yes/no; seconds from win to freeze.
- Force-quit needed: yes/no.
- Model at the result (Giga or Bowser, by appearance).
- Whether any KO happened before this win.
- From the log: the resource path string requested at the freeze, and the stage.
- Screenshot or video of Results or the freeze.
- Build name and exact stage. Do not merge reports from different builds.

## 10. Interpretation table

| Observation | Reading |
|---|---|
| Win freezes, Results never shown; log requests an absent Giga results path | H1 supported (not proven; N4) |
| Win freezes; log requests a base-fighter (Bowser) path | H3 supported |
| Win without KO is fine; win after KO freezes (or the reverse) | H3 over H1 (kind routing after restore) |
| Results shown with T-pose; no freeze | H2 or H3 binding; H1 weakened |
| Win fine but timeout or Sudden Death freezes | State-specific path (H1 family-specific); read the logged path |
| Loss fine; win freezes | Victory-specific path (H1 victory family, or H6) |
| H6 A/B changes win result | H6 supported; repeat 3 times before any claim |
| H6 A/B changes nothing | H6 refuted for the win |
| Buzzing at win or timeout only, sound path in log | H5 supported |
| Buzzing at CSS only | Probe 04 class; not a results finding |
| Normal Mario or Bowser freezes in any outcome | Pack-wide regression; stop and report; not a form result |
| Four fighters freeze while one does not | Interaction; read per-fighter paths in the log |

## 11. Confounds, privacy handling and open questions

Confounds:
- Build, stage and fighter at the win are not recorded together in any existing probe (F13, F15). Each new run must record all three.
- Companion state: an installed companion changes kinds (F21). Record it in every run.
- Field 5 is changed together with the candidate build (F13). Use the H6 A/B from a fresh export to separate them.
- Probe 03 wrote row 60 through `edit_database` (`tools/build_giga_probe.py:39`). Whether row 16 also changed in its output is unverified: `Params.set` (`tools/smash4.py:163-165`) edits only the copy in `params.data`, and the separate-slot output comes from `edit_database(raw)`. The row-16 check at `tools/build_giga_probe.py:45-53` reads both values. The probe was not re-run in this pass.

Privacy handling:
- Logs stay private. Share path strings only, with user path parts removed.
- No dump, decrypted executable or log is committed. Keep the candidate ZIP outside the repository.
- Never write a personal path or hardware identifier into a report.

Open questions:
- N2: which resource the win softlock requests (needs the private dump and a Cemu log).
- N4: does the engine fall back to a base file when a form path is missing?
- N7: meaning of DB field 5.
- N8: whether any sound or voice bank is involved.
- The 58 win-after-KO question: does a win after a restore differ from a win without a KO (the H3 test)?
- Probe 03: which fighter was at the win.
- The stale test count (`docs/VALIDATION.md:35`, `:36`, `:45`; section 2, item 5) needs a later docs fix.
- Not run in this pass: the private-dump run. It is not run, and no result from it is claimed.

## 12. Measured on the real US v304 resource table

`python tools/audit_form_resources.py GAME_CONTENT UPDATE_CONTENT` reads the resource table of the user's own dump (game plus update 0005000E10144F00 v304) and prints counts only. Result, counting files under `fighter/<name>/motion/bodyentry` and `bodyresult`:

| base | form | base entry / result files | form entry / result files | body skeleton sizes, base / form (bytes) |
|---|---|---|---|---|
| koopa | koopag | 5 / 6 | 0 / 0 | 8876 / 8204 |
| wario | warioman | 5 / 6 | 3 / 3 | 12348 / 9548 |
| littlemac | littlemacg | 3 / 3 | 0 / 0 | 5404 / 5964 |
| lucario | lucariom | 6 / 6 | 3 / 3 | 7308 / 9100 |

What this establishes: Giga Bowser and Giga Mac have no entry or results animation files of their own at all, and Wario-Man and Mega Lucario have only main, left-hand and right-hand packs (the partner packs of the base fighter, such as `*pt1`, `*sw1`, face, are absent). Skeleton sizes match the numbers in `docs/NATIVE-FINDINGS.md`. This supports the "missing victory animation" hypothesis and shows a redirect to the base form's packs would have to cope with different skeletons, so a blind copy is not safe.

What it does not establish: which of these files the game opens on Results, or that a missing file is the softlock cause. That needs a console run (Aroma plugins and the forms do not run in Cemu; a base-game boot to the title screen works but does not exercise Results). No fallback is implemented.
