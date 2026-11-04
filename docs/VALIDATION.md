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
- Giga respawn investigation: an equivalent Cemu one-instruction engine probe changed the US-v304 Giga Bowser alternate assignment from Bowser (15) to Giga Bowser (58). The user confirmed Giga Bowser remained Giga after KO. The separately built WUPS companion is intended to reproduce that narrow post-initializer change with title, version, module-bound and instruction-signature guards. Its PowerPC build and Aroma load have not been run, and it has not run on hardware.
- Companion scope (host-only evidence): the companion now restores four hidden forms (58->15, 59->22, 60->41, 61->30) through `companion/form_restore.h`. Only the Giga Bowser pair has any runtime evidence, and that evidence comes from the Cemu probe above. Forms 59, 60 and 61 have no assignment-site guards and no runtime evidence.

## Hidden-form respawn companion lifecycle matrix

Every cell is **UNTESTED on hardware and in Cemu**. Host tests check only the pure pair rule.

| Lifecycle path | 58 Giga Bowser | 59 Wario-Man | 60 Giga Mac | 61 Mega Lucario |
|---|---|---|---|---|
| Match entry (initializer runs) | UNTESTED | UNTESTED | UNTESTED | UNTESTED |
| Respawn after KO | UNTESTED (Cemu probe: kept Giga after KO) | UNTESTED | UNTESTED | UNTESTED |
| Final stock loss | UNTESTED | UNTESTED | UNTESTED | UNTESTED |
| Sudden Death | UNTESTED | UNTESTED | UNTESTED | UNTESTED |
| Timeout | UNTESTED | UNTESTED | UNTESTED | UNTESTED |
| Rematch | UNTESTED | UNTESTED | UNTESTED | UNTESTED |
| Return to CSS | UNTESTED | UNTESTED | UNTESTED | UNTESTED |
| Assignment-site guard | present (signature at 0x02E45708) | MISSING | MISSING | MISSING |

Known runtime failures from the table above still apply: results softlock and T-pose after a win, and freezes on win for forms.

## Host tests run for the companion pair rule

- `python -m unittest discover -s tests -v` on the Windows host (gcc from Strawberry Perl): 29 tests, all OK, including the four C harness tests C1-C4 compiled with `-std=gnu11 -Wall -Wextra -Werror`.
- The same suite inside the `devkitpro/devkitppc` Docker image (Debian gcc 12.2): 29 tests, all OK, no skips.
- Mutation checks on copies outside the repo: a table entry changed from 60->41 to 60->40 fails C1, C2 and C3; an unconditional `return kind` fails C2 and C3.
- `powerpc-eabi-gcc -fsyntax-only -Wall -Wextra` on `companion/main.c` with stub WUPS and FunctionPatcher headers: exit 0. The stubs are declarations only, so this is not a real WUPS SDK build.

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
