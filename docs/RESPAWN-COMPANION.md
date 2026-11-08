# Experimental hidden-form respawn companion

`companion/main.c` is a separate Aroma WUPS plugin, not an SDCafiine file replacement. It targets only the US title `0005000010144F00`. Update v304 is enforced by the FunctionPatcher version arguments (304, 304) and the code signatures, not by the title ID. After the original initializer runs, it reads the entry's kind (entry+0x10) and alternate (entry+0x14). If the pair matches the table below and the form is enabled (only 58 today), it writes the hidden form ID back into the alternate. The pure rules are in `companion/form_restore.h` (pair table) and `companion/guard.h` (gates and the write decision `guard_restored_alternate`), which have no WUPS dependency and are tested on a host compiler.

| Form (kind) | Base written by native code (alternate) | Name |
|---:|---:|---|
| 58 | 15 | Giga Bowser |
| 59 | 22 | Wario-Man |
| 60 | 41 | Giga Mac |
| 61 | 30 | Mega Lucario |

**Fail-closed rule:** the alternate is changed only when kind is an enabled form (currently only 58) AND alternate equals that form's base. Every other input returns the alternate unchanged.

It has guardrails: the US title ID (base title only), `cross_f.rpx` text bounds, the exact four-word US v304 signatures at both the initializer and the Giga Bowser assignment site, an entry-pointer validator, and an enabled-forms mask. It remains inactive if any guard fails.

## Gates and enable state

Only form 58 (Giga Bowser) is enabled at runtime. `GUARD_ENABLED_FORMS_MASK` in `companion/guard.h` sets bit 58 and nothing else. Forms 59, 60 and 61 stay in `companion/form_restore.h` and in the table above, but the hook skips them. Their assignment sites have no verified signature, so nothing can check them. To enable one, add its verified words and a separate check in `companion/main.c`, set its mask bit, and update this document.

Entry validation: `guard_entry_ptr_ok` rejects a NULL, misaligned or out-of-range entry. The hook reads entry+0x10 and entry+0x14, so the whole 0x18-byte window must lie inside the reported range.

ASSUMPTION, not verified on hardware: the fighter entry lies inside the range returned by `OSGetMapVirtAddrRange()`. wut documents that call only as the range available for mapping. If the entry lies outside it, the validator rejects it and the hook never writes. The alternative `OSGetMemBound(OS_MEM2)` was not used.

Enable is all or nothing. `guard_enable` checks the title, module, bounds, signatures and range before touching FunctionPatcher. It then initializes the library and adds one patch, and it requires `applied` to be true and the handle to be non-zero. Any failure rolls back by removing the patch with `FunctionPatcher_RemoveFunctionPatch` and deinitializing the library. If removal fails, the handle is kept, the hook stays disabled, and the next enable reports `GUARD_STUCK`. `guard_disable` runs on application start, application end and plugin deinit. The removal semantics come from the FunctionPatcher header and are not verified at runtime. The teardown race is also unverified.

The companion has now been attempted on Wii U hardware but did not pass its target test: with the latest supplied pack and a separately installed `.wps`, Giga Bowser reverted to Bowser after a KO. The plugin's guard log, exact plugin/candidate hashes, and game update were not recorded, so it is unknown whether the hook loaded and passed its guards. Do not treat the companion as working on console. In an earlier four-form battle, hidden-form behavior had stopped working by Sudden Death, but the individual form outcomes are unknown. Forms 59, 60 and 61 remain disabled at runtime by design.

## Evidence

The equivalent one-instruction Cemu engine probe changed the Giga Bowser alternate assignment from Bowser to Giga Bowser and kept Giga Bowser after a KO. This is probe evidence, not a companion-plugin pass. In the later Wii U companion test, Giga Bowser reverted after a KO. The 59, 60 and 61 pairs come from the native helper mapping in `docs/NATIVE-FINDINGS.md`; they have no runtime evidence.

**KNOWN GAP:** the guard signatures for forms 59, 60 and 61 are unknown. The code guards only the initializer and the Giga Bowser (58) assignment site. For the other three forms the mask keeps the hook from writing at all, so the pair match and `code_matches()` never run for them. The native assignment sites for those forms were not located, so enabling them is not yet possible. Closing this gap needs the assignment-site words from the user's own binary.

The hook runs on any initializer call that matches an enabled pair, not only on KO. It may therefore also affect other transitions, such as Final Smash handling. Regression testing on the base roster is required before any wider claim.

It is **not successfully hardware validated**. The one reported Wii U KO attempt failed to preserve Giga Bowser, and the cause has not been diagnosed. It does not fix results, entry animation, portraits/nameplates, enemy-Mii forms, or the known results softlock and T-pose issues. See `docs/VALIDATION.md` for observed failures and the incomplete per-form lifecycle matrix.

## Build and use

Build from source with the pinned/current official WUPS and FunctionPatcher SDK sources, plus devkitPro, for example:

```powershell
.\tools\build_companion.ps1 -WupsRoot <WUPS SDK root> -FunctionPatcherRoot <FunctionPatcher SDK root>
```

The generated `.wps` needs Aroma's WUPS support and the separately installed FunctionPatcherModule/WUMS prerequisites documented by the FunctionPatcher project. Do not install it alongside unknown engine-patching plugins. Back up the SD card, use the US v304 game only, and remove the plugin immediately after a hang or unexpected behavior.

No binary plugin or Nintendo data is committed or included in the source ZIP.

## Settings and persisted state

The hook is **OFF by default** (`GUARD_DEFAULT_ENABLED` in `companion/guard.h`, experimental). Turn it on in the WUPS config menu: category "Settings", item "Enable respawn hook (experimental, US v304)". The value is stored under storage id `hidden_css_respawn`, key `enabled`. A missing key stores OFF. Any other read error, or a failed config API init, keeps the hook OFF. Toggling applies at once: OFF removes the patch and deinitializes FunctionPatcher, ON adds it, and the menu close re-applies the stored value. The plugin logs a `[HiddenCSS]` line for each outcome: armed (the entry range is still checked on each call, so the first rejected entry is logged once with its address and the range, and later ones are silent), inactive (disabled in settings), or failed (removal, storage, menu or config-init error). A failed removal is retried on the next toggle, on menu close and on the next ON, and the menu shows ON while the patch is still held. If removing the patch fails, only the failure is logged, never "inactive"; the leftover wrapper stays inert because the hook body is gated by the enabled flag.

Default change (release note): earlier builds restored Giga Bowser after KO without any setting. This build defaults to OFF, so after updating, turn the item on in the WUPS menu to get the restore back. The OFF default is a maintainer decision and is not final.

NOT verified: the real WUPS menu, that the stored value survives a reboot, dynamic patch removal on the console, the order of the value-changed and menu-closed callbacks, and the case where the menu is opened outside the game (the module is then absent, so the hook stays off until the game starts with the setting ON).
