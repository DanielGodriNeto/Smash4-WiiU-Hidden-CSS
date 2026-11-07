"""Validate the public companion source and, optionally, a locally built WUPS file."""
import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from prepare_native_candidate import rpx_sections

MAIN_SOURCE = ROOT / 'companion' / 'main.c'
GUARD_SOURCE = ROOT / 'companion' / 'guard.h'
# Each requirement is checked in the one file that must contain it, so a definition in guard.h
# cannot satisfy a requirement on a call site in main.c.
MAIN_REQUIRED = (
    '#include "guard.h"',
    'ENTRY_INIT_ADDRESS 0x02E45558u', 'GIGA_ASSIGNMENT_ADDRESS 0x02E45708u',
    'guard_may_read_entry(guard_state.enabled, (uint32_t)(uintptr_t)entry',
    'guard_restored_alternate(kind_value, current)', '*alternate = restored;',
    'guard_title_allowed(', 'guard_bounds_ok(', 'guard_signature_ok(',
    'guard_apply(', 'guard_disable(', 'OSGetMapVirtAddrRange(',
    'module.textSize', 'code_matches()', '304, 304',
)
GUARD_REQUIRED = (
    'GUARD_TITLE_US_V304 UINT64_C(0x0005000010144F00)',
    'GUARD_ENABLED_FORMS_MASK (UINT64_C(1) << 58)',
    '#include "form_restore.h"', 'form_restore_alternate(kind, current)',
    'guard_form_enabled(kind)', 'guard_entry_ptr_ok(entry, range_lo, range_size)',
)
PRIVATE = (r'[A-Za-z]:[\\/]+Users[\\/]', r'gh[pousr]_[A-Za-z0-9]{20,}',
           r'github_pat_[A-Za-z0-9_]{20,}', r'PRIVATE KEY')


def check_source():
    main_text = MAIN_SOURCE.read_text(encoding='utf-8')
    guard_text = GUARD_SOURCE.read_text(encoding='utf-8')
    missing = [item for item in MAIN_REQUIRED if item not in main_text]
    missing += [item for item in GUARD_REQUIRED if item not in guard_text]
    if missing:
        raise ValueError('Missing companion safety requirement(s): ' + ', '.join(missing))
    if any(re.search(pattern, main_text + guard_text) for pattern in PRIVATE):
        raise ValueError('Private path or credential-like content in companion source')


def check_plugin(path):
    raw = Path(path).read_bytes()
    if raw[:4] != b'\x7fELF' or raw[9:11] != b'PL':
        raise ValueError('Expected a WUPS-marked ELF/RPL plugin')
    payload = b''.join(data for _, data in rpx_sections(path))
    text = payload.decode('latin-1', errors='ignore')
    if any(re.search(pattern, text) for pattern in PRIVATE):
        raise ValueError('Private path or credential-like content in built plugin')
    for expected in ('Hidden CSS Giga Respawn', 'US v304'):
        if expected not in text:
            raise ValueError('Built plugin is missing expected metadata: ' + expected)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--plugin', help='optional local .wps output to audit')
    args = parser.parse_args()
    check_source()
    if args.plugin:
        check_plugin(args.plugin)
    print('Companion source' + (' and plugin' if args.plugin else '') + ' validation passed.')


if __name__ == '__main__':
    main()
