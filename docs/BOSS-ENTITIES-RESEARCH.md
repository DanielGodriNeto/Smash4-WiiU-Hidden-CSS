# Boss entities research: Master Hand, Crazy Hand, Master Core

Date: 2026-11-04. Tracks issue #8.

**Status: research only, not planned, not validated on hardware or in Cemu, not part of the stable build.** This file is not a roadmap and does not commit the project to any work. Nothing described here has been run.

## 1. Summary and verdict

On public evidence, making Master Hand, Crazy Hand or Master Core playable in US v304 is **not shown to be feasible**. Public sources state that boss entries have no fighter-ID path in this game generation, and no public source was found that documents how these entities are created, controlled, shown in the HUD or counted in stocks. Whether the private US v304 dump contains a usable entry is **unknown**; only the maintainer can answer that.

| Area | Rating | Reason (one line) |
|---|---|---|
| Spawning | Low / unknown | Bosses are described as having no character IDs since Brawl; no public internal kind value found; repo excludes them (README.md:21) |
| Camera | Low | Wii U pause camera is special-cased in the Master Core fight; no camera parameters found |
| HUD | Low | Wii U does not show the Master Core HP meter; no HUD resource names found |
| Stocks | Low / unknown | The two Hands share one HP pool; no stock model documented |
| Animations | Low | No boss animation or motion data documented; general tools exist but no boss data was found |
| CSS slot | Unknown | Mechanically similar to the repo's seven-slot path, but a slot is useless without a spawnable entity; CSS absence is implied by "unplayable", not stated |
| Online / safety | Very low | Wii U online service has ended; the only playable-boss analogue found (a different game) warns against online use |

## 2. Scope and isolation statement

Scope: collect public facts, state what is unknown, and define a way a maintainer could test safely later. Out of scope: any code, any change to the 82-row `ui_character_db`, any change to the Final Smash forms (58-61) or the Mii enemy rows (62-64), any claim about gameplay. The issue itself asks that this stays isolated from the stable forms mod; section 9 makes that concrete.

## 3. Evidence table

Confidence scale. High: figure read on the primary page in this pass and re-checked by a second query. Medium: single read through a page summariser, or a repository front page. Low: search-result snippet only. Every row was fetched on 2026-11-04.

| Claim (paraphrased) | Source | Confidence | How verified |
|---|---|---|---|
| Since Brawl, boss character IDs were removed, so bosses are unplayable even with hacks (a Brawl Boss Battles exception is mentioned) | https://www.ssbwiki.com/Boss | Medium | Sentence located in the page intro. Wiki claim, no technical proof offered |
| Master Hand, Crazy Hand and Master Core are listed as bosses of the Smash 4 games; Master Core is new in the 3DS version | https://www.ssbwiki.com/Boss | Medium | Fetched |
| Master Hand and Crazy Hand share one HP pool on Wii U | https://www.ssbwiki.com/Master_Hand_(SSB4) , https://www.ssbwiki.com/Crazy_Hand_(SSB4) | High | Both pages fetched, same statement |
| Wii U Master Hand HP: Solo 110 / 280 / 380 and Co-op 165 / 398 / 580 at Intensity 0.0 / 5.0 / 9.0 | https://www.ssbwiki.com/Master_Hand_(SSB4) | High | Wiki table, not cross-checked |
| Crazy Hand is fought automatically on Wii U at Intensity 3.0 or higher | https://www.ssbwiki.com/Crazy_Hand_(SSB4) , https://www.ssbwiki.com/Boss | High | Two wiki pages agree |
| Master Core appears only at Intensity 5.1 or higher | https://www.ssbwiki.com/Master_Core , https://www.ssbwiki.com/Crazy_Hand_(SSB4) , https://www.ssbwiki.com/Boss | High for the wiki's statement; see conflicts (section 7) | Four fetches agree |
| Wii U does not display the Master Core HP meter; 3DS does | https://www.ssbwiki.com/Master_Core | Medium | Fetched |
| Wii U pause camera in the Master Core fight is limited to zoom at Intensity 8.0 and higher | https://www.ssbwiki.com/Master_Core | Medium | Fetched |
| Master Core fight timer stops when the Core is revealed; about 45 seconds to KO it | https://www.ssbwiki.com/Master_Core | Medium | Fetched |
| The Master Hand (SSB4) and Crazy Hand (SSB4) pages are categorised as unplayable characters; Master Core is described as a boss, not a playable fighter | https://www.ssbwiki.com/Master_Hand_(SSB4) , https://www.ssbwiki.com/Crazy_Hand_(SSB4) , https://www.ssbwiki.com/Master_Core | Medium | Fetched |
| Master Hand is "primarily non-playable"; playable only via a Melee glitch and in Ultimate; Wikipedia does not describe him as playable in the 3DS/Wii U game | https://en.wikipedia.org/wiki/Master_Hand | Medium | Fetched |
| CSS presence, stock counts, internal IDs and camera values for these bosses are not given on the ssbwiki pages above | the pages above | Medium | Targeted queries returned "absent"; absence in a summary is weaker than absence in the page |
| SmashWiki fighter numbers cover Ultimate numbering, not Smash 4 internal values | https://www.ssbwiki.com/Fighter_number | Low | Search snippet |
| Smash Forge opens Smash 4 models, textures, animations, materials, movesets (via a table file) and some parameter files; the front page does not mention enemy or boss data; MIT licence | https://github.com/jam1garner/Smash-Forge | Medium | Fetched front page |
| Smash Forge wiki lists 21 visible pages (plus 6 hidden); none about fighter kinds, enemies or bosses | https://github.com/jam1garner/Smash-Forge/wiki | Medium | Fetched; the 6 hidden pages were not read |
| Sm4sh-Tools provides a moveset editor, archive extractor, pack manager, param editor, script decompiler and XMB dumper; no kind table; licence stated per project | https://github.com/Sammi-Husky/Sm4sh-Tools | Medium | Fetched; last-commit date not shown (a search snippet said 2018, Low) |
| Playable_Bosses targets Ultimate, not Smash 4, and warns against online play unless all players run the same setup | https://github.com/NemesisSSBU/Playable_Bosses | Medium | Fetched |
| Wii U Nintendo Network online services ended on 2024-04-08 (US time) | https://en.wikipedia.org/wiki/Nintendo_Network | Medium | Fetched; only the first part of a long page was read |
| SmashWiki text is CC BY-SA 4.0 for recent contributions, CC BY-SA 3.0 for text before 2026-02-27, some older text also under GFDL; images are not under those licences | https://www.ssbwiki.com/SmashWiki:Copyrights | Medium | Fetched |

## 4. Repo facts (verified by opening the files)

- README.md:21: boss and item icons with fighter ID `0xFFFFFFFF` do not provide controllable fighter modules and are excluded. Strongest in-repo hint that bosses are not ordinary fighter-table entries.
- tools/build.py:20-22: Mii forms 62-64 use donor rows 1-3, DB rows 73-75 and cosmetics 219-221. docs/MAINTAINER-GUIDE.md:62-63 calls these enemy-oriented actors, not full retail fighters. docs/VALIDATION.md:64 says enemy Miis are multi-man actors.
- Runtime status of Mii 62-64: **not established.** docs/VALIDATION.md:12 records Cemu CSS loading and Giga Bowser Training for candidate 07 only; it records no Mii result. README.md:5 states the only runtime evidence is for form 58. So the Mii rows are a precedent that enemy-type actors can be listed in the fighter table, not proof that they run.
- docs/NATIVE-FINDINGS.md:7: the cosmetic key table at virtual address 0x1033BE70 has no mapping for cosmetics 60 or 62; 219-221 are the Mii enemy names. No Master Hand, Crazy Hand or Master Core entry is recorded anywhere in the repo (searched README, docs, tools, companion, tests).
- docs/NATIVE-FINDINGS.md:31-37 and docs/VALIDATION.md:8, 12, 31: CSS loading can pass while the fighter lifecycle (KO, respawn, results) still fails. A hidden CSS entry says nothing about gameplay.
- README.md:43: use one pack at a time. docs/VALIDATION.md:13-14 and README.md:49: the respawn companion enables only form 58 and is not hardware validated.
- tools/package_source.py:8-24 is the public allowlist; tests/test_guard_host.py:56 and tests/test_companion_validation.py:61 check allowlist membership. tests/test_builder.py asserts the 82-row database; this document does not touch it.

## 5. Findings per area

- **Spawning.** The only public statement found says boss character IDs were removed from Brawl onward. The repo already excludes `0xFFFFFFFF` icons. No public table of Smash 4 fighter or enemy kind values was found, so how Classic Mode creates the Hands is unknown here.
- **Camera.** The Master Core fight has a restricted pause camera on Wii U at high intensity. This hints at boss-specific camera handling; no parameter, file or hook is documented.
- **HUD.** The Wii U version hides the Master Core HP meter, which suggests boss HP is not a normal fighter damage display. No HUD resource names were found.
- **Stocks.** The Hands use HP, shared between the two, not stocks. A fighter-style stock and respawn path for them is not documented.
- **Animations.** Tools exist for animation, model and moveset files, but no source describes boss data, and the repo already shows that animation and results gaps break even real fighters (docs/NATIVE-FINDINGS.md:19).
- **CSS slot.** The repo can add a slot (README.md:9-19), but its own evidence shows the slot is the easy part. The unknown is the entity behind it.
- **Online.** Wii U online services ended in April 2024, so online play for this title is no longer a live concern. Any experiment must still treat a shared multiplayer session as unsafe.

## 6. What was NOT found

- Any public Smash 4 Wii U internal fighter or enemy kind table, or boss module names (including any fighter/ or enemy/ folder naming for the Hands or the Core). Searches run: kind table, boss module/folder, modding wiki enemy IDs.
- Any documented Smash 4 Wii U hack that makes Master Hand, Crazy Hand or Master Core playable, or adds them to the CSS. Searches found none; absence from search is not proof that none exists.
- A citable page from a Sm4sh community wiki on enemy or boss internals.
- Camera, HUD and stock parameters for bosses.
- The Master Core HP fraction at which the Hands transform (both Hand pages flag it as missing).
- https://smashboards.com/threads/how-master-hand-can-become-playable.457899/ returned HTTP 403 earlier; **unverified**, and not used as evidence.
- The 6 hidden Smash Forge wiki pages and the second part of the Nintendo Network article.

## 7. Conflicts

- Master Core unlock threshold: the SmashWiki pages say Intensity 5.1. Earlier search snippets from two other sites reportedly gave 7.0 and 8.0; those were **not re-fetched in this pass**, so they are unverified. Unresolved; treat 5.1 as the wiki's claim only. It is background, not needed by any step here.
- The Boss page describes Master Core as appearing on "high enough" difficulty, while the Core page gives 5.1. Likely the same fact in different wording; not resolved.

## 8. Risks to the stable mod

- Reusing Mii rows 73-75, fighter IDs 62-64 or cosmetics 219-221 for a boss would corrupt a known enemy-actor precedent.
- A boss entry with no fighter module can reproduce the Candidate06-style CSS crash (docs/NATIVE-FINDINGS.md:31) or a hang on load.
- Global patches to shared native helpers could alter legitimate Final Smashes (docs/NATIVE-FINDINGS.md:13).
- Documentation confusion: readers could take this file as a promise. Hence the status line at the top.
- Online or replay use of a modified session may desynchronise other players; not tested.

## 9. Isolation policy

- This document lives on its own docs branch. Any experiment would use a separate worktree and branch, never merged into the stable branch.
- Experiment files, if ever written, live in their own folder, with their own build profile and their own SDCafiine pack name. They are never bundled with the HiddenSeven CSS pack (README.md:43).
- No shared tables: no new rows in the 82-row `ui_character_db`, no new IDs in the forms set, no reuse of fighter IDs 62-64, rows 73-75 or cosmetics 219-221, no edits to `FIGHTERS` in tools/build.py, no edits to companion/guard.h.
- Kill switch: title, version and signature checks fail closed, plus a default-off flag. Disabling means removing the experiment pack folder.
- Experiment files stay out of the public allowlist unless the maintainer approves them.

## 10. Staged maintainer experiment plan (hypothetical)

Each stage changes one variable. The maintainer runs every hardware or Cemu test; no benchmarks. Nothing here is scheduled.

- **Stage 0, static, private dump, read-only.** Look for any kind value for the Hands or the Core in the parameter and UI tables. Abort and record "not feasible on this evidence" if none exists.
- **Stage 1, CSS display only, one entry, no spawn.** Abort on boot failure, a hang entering the CSS (Candidate06 precedent), or any change to the 82-row diff.
- **Stage 2, offline Training spawn of one entity, no results screen.** Abort on crash, softlock, camera lock, or any change to Giga Bowser or Bowser rows.
- **Stage 3, HP and stock probe, offline only.** Abort if HP or stock state leaks into ordinary fighter matches.
- **Stage 4, online.** Out of scope; blocked until multiplayer compatibility is shown.
- **Rollback at every stage:** remove the experiment folder, confirm the baseline pack loads, and record a result in docs/VALIDATION.md only after the maintainer confirms it.

## 11. Sources and licence notes

External pages (all fetched 2026-11-04): the SmashWiki pages Boss, Master_Hand_(SSB4), Crazy_Hand_(SSB4), Master_Core and SmashWiki:Copyrights on https://www.ssbwiki.com (Fighter_number appears only as a search snippet); https://en.wikipedia.org/wiki/Master_Hand; https://en.wikipedia.org/wiki/Nintendo_Network; https://github.com/jam1garner/Smash-Forge and its wiki; https://github.com/Sammi-Husky/Sm4sh-Tools; https://github.com/NemesisSSBU/Playable_Bosses. The Sm4shExplorer and Smash4ModdingTests repositories were only skimmed earlier (front pages, no boss, CSS or stock data seen); that is unverified and not re-checked.

Licence: SmashWiki text is CC BY-SA, so this file paraphrases it, links the source and quotes no more than a few words. Figures such as HP values are facts, listed with their source. Wikipedia text is also CC BY-SA. Repository front pages were used for capability statements only.
