# Runtime validation still required

The original four/seven profiles have not passed runtime validation; seven-v2 produced an Aroma boot failure. Later probes were tested by the user on a US Wii U with Aroma SDCafiine:

- 00 StockControl: boot and CSS passed.
- 01 MarioSevenCostumes: boot and CSS passed.
- 02 GigaBowser in BowserSlot: Training loading/control passed; death restores Bowser.
- 03 SeparateSlot: extra slot selects playable Giga Bowser. Icon is white and name missing. Death restores Bowser; a subsequent win produced a T-pose and results softlock.
- 04 UI probe: user confirmed boot, followed by a freeze with buzzing audio while loading CSS. Do not use. It added 88 external UI overrides across four partitions. Root cause is not established.
- 05 SinglePortrait: built, awaiting console testing. Temporarily reassigns normal Bowser's existing CSS portrait record to Giga Bowser. No new records, external flags, name blocks, nameplates or aliases. Normal Bowser may have a blank icon during this diagnostic. All packed files and patchlist remain identical to test03. Respawn/results are unchanged.
- 06 HiddenSeven candidate: boots, but the user confirmed a CSS-loading crash in Cemu. The earlier byte-content verifier passed 316 imports and 11,308 unchanged members but missed unsafe pack localization. This build is now rejected by the current validator and must not be installed.
- 07 HiddenSeven SharedUI: the user confirmed CSS loading and Giga Bowser Training in Cemu. A KO still restores Bowser. It removes 190 redundant UI language imports. Validation confirms 126 physical imports, 190 inherited shared references, 11,308 unchanged members and 925 patchlist records. Hardware behavior, results, other fighters and cosmetic rendering remain unverified.
- Giga respawn investigation: an equivalent Cemu one-instruction engine probe changed the US-v304 Giga Bowser alternate assignment from Bowser (15) to Giga Bowser (58); the user confirmed that probe kept Giga Bowser after KO. The separately built WUPS companion is intended to reproduce that narrow post-initializer change with title, version, module-bound and instruction-signature guards.
- Companion scope (host-only evidence): the pure pair rules in `companion/form_restore.h` cover four pairs (58->15, 59->22, 60->41, 61->30), but the runtime mask in `companion/guard.h` enables only 58->15. Only the Giga Bowser pair has runtime evidence, from the Cemu probe above. Forms 59, 60 and 61 are disabled at runtime by design, because their assignment sites have no verified signature.
- New user hardware report: in an earlier four-form battle, hidden-form behavior had stopped working by Sudden Death; which individual forms reverted is unknown, and normal KO/respawn was not tested in that session. In a later one-on-one test using the latest supplied SDCafiine pack and a separately installed `.wps` companion, Giga Bowser reverted to Bowser after a KO. Thus the intended companion behavior was not achieved in that console test. The exact candidate/archive and plugin hashes, game update, and plugin guard log are not recorded, so the cause is unknown. The Little Mac Final Smash form reached its victory screen but appeared as regular Little Mac in a T-pose; the user reported no crash in that test. This is consistent with the known missing/unsafe results-animation resources, not proof that other results paths are safe. The companion has been attempted on hardware but is not successfully validated. Issue #3 remains open for reproduction; issue #4 tracks results/victory resource safety.

## Hidden-form respawn companion lifecycle matrix

No complete, hash-identified matrix run is recorded. Host tests check only the pure pair rule. The individual user observations above are failures/partial outcomes, but lack enough per-run metadata to populate the generated matrix safely.

| Lifecycle path | 58 Giga Bowser | 59 Wario-Man | 60 Giga Mac | 61 Mega Lucario |
|---|---|---|---|---|
| Match entry (initializer runs) | UNTESTED | UNTESTED | UNTESTED | UNTESTED |
| Respawn after KO | Hardware attempt: reverted to Bowser; Cemu probe kept Giga | UNTESTED | UNTESTED | UNTESTED |
| Final stock loss | UNTESTED | UNTESTED | UNTESTED | UNTESTED |
| Sudden Death | UNTESTED (which forms reverted is unknown) | UNTESTED (which forms reverted is unknown) | UNTESTED (which forms reverted is unknown) | UNTESTED (which forms reverted is unknown) |
| Timeout | UNTESTED | UNTESTED | UNTESTED | UNTESTED |
| Rematch | UNTESTED | UNTESTED | UNTESTED | UNTESTED |
| Return to CSS | UNTESTED | UNTESTED | UNTESTED | UNTESTED |
| Assignment-site guard | present (signature at 0x02E45708), enabled | MISSING, disabled by design | MISSING, disabled by design | MISSING, disabled by design |

Known runtime failures from the table above still apply: results softlock and T-pose after a win, and freezes on win for forms.

## Host tests run for the companion pair rule

- `python -m unittest discover -s tests -v` on the Windows host (gcc from Strawberry Perl): 36 tests, 1 skipped. The skip is the sanitizer run of the guard harness, because that gcc has no ASan/UBSan runtime.
- The same suite inside the `devkitpro/devkitppc` Docker image (Debian gcc 12.2): 36 tests, all OK, no skips, including the ASan/UBSan run of `tests/guard_host_harness.c`.
- Guard tests in `tests/test_guard_host.py` cover the title gate, module bounds, signatures, entry-pointer validator, the enabled-forms mask (exactly form 58), the form-restore sweep, and the enable/disable state machine with fake FunctionPatcher ops (add failure, not applied, null handle, removal failure, all-or-nothing rollback).
- Mutation checks on copies outside the repo: 10 mutants of `guard.h` (mask adds 59, alignment dropped, title accepts +1, 32-bit wrap in the entry range check, bounds off by one, enabled set before add, applied ignored, null handle accepted, rollback skips release, disable clears enabled after release). Each fails the harness at run time.
- `powerpc-eabi-gcc -std=gnu11 -fsyntax-only -Wall -Wextra` in the devkitppc image, with wut headers and stub WUPS and FunctionPatcher headers, on `companion/main.c`: exit 0. The stubs are declarations only, so this is not a real WUPS SDK build.

Not run: the real PowerPC plugin build (`tools/build_companion.ps1` needs the WUPS and FunctionPatcher SDKs), loading under Aroma, and any Cemu or hardware run.

Local Cemu 2.6 boot reaches the album-data prompt with both a stock US v304 merged dump and candidate06. The user confirmed physical J advanced the stock prompt. Automated input did not establish reliable gameplay control; this is not evidence of a mod gameplay pass. The private test GamePad profile was corrected after finding that Pro Controller direction enum values had been used. Its intended controls are J=A, K=B, U=X/jump, I=Y, P=Start and arrows=left stick. No settings in the user's separate Cemu installation were changed.

Thirty-six synthetic tests (`python -m unittest discover -s tests -v`, 22 before the grid-integrity change) cover typed-schema mismatch, duplicate fighter mappings, invalid cosmetics, overwriting normal rows, appending rows, patchlist truncation/path traversal/case collisions, physical pack ownership and prior resource-table regressions. The grid-integrity change adds: CSS field-13 overlap and duplicate rejection against kept rows (DLC and hidden rows included, replaced rows excluded), rejection of field-13 values above 255, case-insensitive resource path collisions in `ArchiveEdits.add` and the native candidate preparer, span bounds checks before archive slicing (`check_span`, also in `Dump.read`), zlib failure mapping in `ArchiveEdits.finish`, out-of-range span rejection in the native fighter-UI NUT scan (`native_head`) instead of silent skipping, malformed single-texture NUT header rejection, and texture-ID exhaustion at 0xFFFFFFFF. These guard build correctness; they do not certify fighter stability. Neither original profile nor any probe is a stable release.

Grid-integrity status (issue "CSS Resource Packing and Grid Integrity", partial):

- Implemented and synthetic-tested: the checks above. Not implemented: texture width/height/crop checks (needs private NUT parsing offsets), and any CSS grid row/column bound (no verified dimensions in the repository).
- Open decision D1: new slots still go after the maximum non-DLC field-13 value. Whether DLC or hidden rows hold higher values, and whether appended slots fit the native CSS grid, is unverified without a private dump of field 2, 9, 10 and 13 for all 82 rows in each partition.
- Unverified: whether native positions already repeat, whether any target path exists natively in another letter case in the real dump (the preparer now rejects such a case-only variant), and in-game CSS stretching or overlap. Only a US v304 dump and console/Cemu testing can verify these.

Start with a clean US game and only this pack. Record game update, SDCafiine version, active language and profile. Test each hidden fighter separately before testing combinations.

- Open/reopen CSS and move every player cursor over all additions.
- Select each addition, cancel, reselect, start training and a normal local match.
- Confirm the selected fighter, costume, controls, model, portraits and nameplates.
- Test entry, all movement/attacks, shielding/grabs/items, KO, respawn, match exit, loss and win.
- Test timeout, sudden death, individual and team results, rematch and return to CSS.
- Test CPU as each addition and combinations of different hidden fighters.
- Test the original roster, DLC actually installed, Random and the normal Mii menu.
- Repeat US English/French/Spanish before claiming language support.

Known research limitations: Final Smash forms may freeze upon winning because standalone fighter results behavior is incomplete. Enemy Miis are multi-man actors, not full retail fighters. UI victory fallback does not repair gameplay code. Avoid saving/relying on replays until validated. Eight-player, Classic, All-Star, Tour, Orders, amiibo and network play are outside the supported test scope.

If a case fails, disable the pack, restart and compare stock behavior. Do not assume a different icon or another enabled flag fixes the fighter module. A stable release requires actual runtime evidence and potentially engine/animation work beyond CSS parameters.

## Latest user-reported console results (2026-11-10)

The user tested the current Hidden CSS build on a Wii U. The exact pack/plugin hashes, game update, language and match settings were not recorded; these observations are reports, not a root-cause diagnosis:

- The companion plugin's configuration page has no visible on/off button. The toggle was previously validated only at host/code level; console visibility is not verified. Reopened issue #5 and recorded hardware follow-up in #21.
- The character-selection screen still has a visual defect. Names are blank or `???`, and added forms use base-character portraits. The supplied screenshot shows the CSS grid with Custom Fighters Off, but does not isolate a separate layout/rendering cause. Name/portrait tracking: #2; separate visual-defect investigation: #23.
- Final Smash forms still T-pose, and respawning reportedly restores the base character. Which forms and exact runs are unknown. Tracking: #3 and #4.
- Results reportedly take a long time to appear and show Mario. An eight-player match containing all four Final Smash forms and added Mii characters ended in buzzing audio at the Results transition. This does not establish whether the symptoms share a cause. Tracking: #4.
- A new experimental checklist in issue #8 records the requested hidden-entity and extra-slot playability candidates. None is validated as playable.

Do not treat these outcomes as passing cells in `docs/regression-matrix.json`: no hash-identified run records were supplied. Reproduce one candidate at a time, compare with stock behavior, and stop if a hang, softlock, or buzzing occurs.

Documentation-change checks on this host: the source-only package privacy scan passed. `python -m unittest discover -s tests -v` attempted 114 tests; Windows App Control blocked two generated companion harness executables, and one sanitizer-dependent test was skipped. No Wii U build or hardware test was performed for this documentation-only update.
