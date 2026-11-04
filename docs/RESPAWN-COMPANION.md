# Experimental hidden-form respawn companion

`companion/main.c` is a separate Aroma WUPS plugin, not an SDCafiine file replacement. It targets only the US title `0005000010144F00`, update v304. After the original initializer runs, it reads the entry's kind (entry+0x10) and alternate (entry+0x14). If the pair matches the table below, it writes the hidden form ID back into the alternate. The pure rule is in `companion/form_restore.h`, which has no WUPS dependency and is tested on a host compiler.

| Form (kind) | Base written by native code (alternate) | Name |
|---:|---:|---|
| 58 | 15 | Giga Bowser |
| 59 | 22 | Wario-Man |
| 60 | 41 | Giga Mac |
| 61 | 30 | Mega Lucario |

**Fail-closed rule:** the alternate is changed only when kind is one of these four forms AND alternate equals that form's base. Every other input returns the alternate unchanged.

It has guardrails: title/version selection, `cross_f.rpx` text bounds, and the exact four-word US v304 signatures at both the initializer and the Giga Bowser assignment site. It remains inactive if any guard fails.

## Evidence

Only Giga Bowser (58 -> 15) was tested, and only through the equivalent one-instruction Cemu engine probe: changing the native alternate assignment from Bowser to Giga Bowser kept Giga Bowser after a KO. The 59, 60 and 61 pairs come from the native helper mapping in `docs/NATIVE-FINDINGS.md`; they have no runtime evidence.

**KNOWN GAP:** the guard signatures for forms 59, 60 and 61 are unknown. The code guards only the initializer and the Giga Bowser (58) assignment site. For the other three forms, the safety net is the exact kind+alternate pair match plus `code_matches()`. The native assignment sites for those forms were not located, so the hook may never fire for them. Closing this gap needs the assignment-site words from the user's own binary.

The hook runs on any initializer call that matches a pair, not only on KO. It may therefore also affect other transitions, such as Final Smash handling. Regression testing on the base roster is required before any wider claim.

It is **not hardware validated**. It does not fix results, entry animation, portraits/nameplates, enemy-Mii forms, or the known results softlock and T-pose issues. See `docs/VALIDATION.md` for the per-form lifecycle matrix (all untested).

## Build and use

Build from source with the pinned/current official WUPS and FunctionPatcher SDK sources, plus devkitPro, for example:

```powershell
.\tools\build_companion.ps1 -WupsRoot <WUPS SDK root> -FunctionPatcherRoot <FunctionPatcher SDK root>
```

The generated `.wps` needs Aroma's WUPS support and the separately installed FunctionPatcherModule/WUMS prerequisites documented by the FunctionPatcher project. Do not install it alongside unknown engine-patching plugins. Back up the SD card, use the US v304 game only, and remove the plugin immediately after a hang or unexpected behavior.

No binary plugin or Nintendo data is committed or included in the source ZIP.
