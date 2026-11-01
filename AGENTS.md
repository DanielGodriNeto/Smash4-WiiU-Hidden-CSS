# Smash Wii U Hidden CSS Agent Guidelines

These instructions apply to AI agents and human contributors working in this
repository.

## Project Context

This repository contains source code, synthetic tests, and documentation for an
experimental US v304 Super Smash Bros. for Wii U CSS investigation. It does
not distribute Nintendo game data, decrypted executables, generated candidate
packs, or emulator profiles.

The project has two separate deliverables:

- The SDCafiine candidate replaces selected UI and database resources using the
  user's own game/update dump.
- The optional Aroma/WUPS companion is a narrowly guarded US-v304 executable
  experiment for Giga Bowser's post-KO fallback behavior. It is not required
  by the CSS pack and is not hardware-validated.

The current candidate preserves the native 82-row database and uses seven
validated reserved rows. Fighter IDs, cosmetic IDs, database rows, and CSS
field 13 are distinct values. Cosmetic IDs 203 and 204 intentionally reuse
native placeholder identities; this is a compatibility tradeoff, not proof of
dedicated retail mappings.

## Coding Standards

- Write all code, comments, variables, commit messages, and documentation in
  English.
- Use Python's standard library unless an existing dependency is required.
- Keep binary parsing lossless and explicit about byte order, offsets, sizes,
  and record counts.
- Reject malformed or unsupported mappings instead of silently inventing rows.
- Preserve unrelated resource entries byte-for-byte where the format permits.
- Keep experimental probes separate from the official candidate workflow.
- Treat user dumps and generated game archives as private inputs.
- Do not add absolute local paths, credentials, personal data, proprietary game
  assets, decrypted executables, or generated candidate ZIPs.
- Keep `companion/main.c` narrowly guarded by title, version, module bounds,
  and instruction signatures. It must fail closed when validation does not
  match.

## Build and Test

From the repository root, run:

```powershell
python -m unittest discover -s tests -v
python tools/package_source.py --out dist/smash4-css-source.zip
```

The private candidate workflow is:

```powershell
python tools/prepare_native_candidate.py --help
powershell -ExecutionPolicy Bypass -File tools/export_with_sm4shexplorer.ps1 -?
python tools/verify_official_candidate.py --help
python tools/package_official_candidate.py --help
```

Use a fresh private output directory for each export. Sm4shExplorer 0.07.4 and
the user's own decrypted US v304 base/update content are required for a real
candidate build. Do not use the retired custom exporter as release validation.

## Workflow Guidelines

1. Read `README.md`, `CONTRIBUTING.md`, `SECURITY.md`, and
   `docs/MAINTAINER-GUIDE.md` before editing.
2. Read `docs/NATIVE-FINDINGS.md` before changing fighter mappings or lifecycle
   assumptions.
3. Update `docs/VALIDATION.md` when new runtime evidence changes a conclusion.
4. Run the complete Python test suite and source-only packager before review.
5. Review the complete diff and inspect package contents before distribution.
6. Keep private dumps, exports, logs, and candidate packs outside the public
   repository.
7. Label Cemu-only or otherwise unverified behavior as experimental; never
   describe it as console-stable without hardware evidence.

## Strict AI Co-Author Rule

Any time an AI agent modifies, creates, or refactors code, it MUST append itself
as a co-author in the git commit message using the standard GitHub co-author
format. If the AI agent does not know its official GitHub contributor routing
email, it must check the repository's commit history to find previous examples
of its own attribution, or search the web to find its correct official
co-author tag.

## Strict Documentation Sync Rule

Any time an AI agent changes, adds, or removes code, it MUST simultaneously
update the relevant documentation (README, comments, or wikis) to reflect
those changes.

## Strict Language Rule

All contributions to this repository, including code comments, variables,
commit messages, and documentation, MUST be written in English.
