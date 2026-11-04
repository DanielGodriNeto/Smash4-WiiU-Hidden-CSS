import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import package_source
import verify_companion
import test_companion_validation as companion_tests

COMPANION = ROOT / 'companion'
GUARD = COMPANION / 'guard.h'
MAIN = COMPANION / 'main.c'
HARNESS = ROOT / 'tests' / 'guard_host_harness.c'
STRICT_FLAGS = ['-std=c11', '-pedantic', '-Wall', '-Wextra', '-Werror']
SANITIZER_FLAGS = ['-fsanitize=address,undefined', '-fno-sanitize-recover=undefined', '-g']


def compile_harness(workdir, extra_flags=()):
    exe = Path(workdir) / 'guard_host'
    command = [companion_tests.C_COMPILER, *STRICT_FLAGS, *extra_flags,
               '-I', str(COMPANION), str(HARNESS), '-o', str(exe)]
    return subprocess.run(command, capture_output=True, text=True), exe


@unittest.skipUnless(companion_tests.C_COMPILER, 'no gcc, cc or clang on PATH: guard host harness not run')
class GuardHarnessTests(unittest.TestCase):
    def run_harness(self, extra_flags=()):
        with tempfile.TemporaryDirectory() as workdir:
            built, exe = compile_harness(workdir, extra_flags)
            self.assertEqual(built.returncode, 0, 'compile failed:\n' + built.stderr)
            ran = subprocess.run([str(exe)], capture_output=True, text=True)
            self.assertEqual(ran.returncode, 0, 'harness failed:\n' + ran.stderr)

    def test_guard_rules_and_state_machine_pass_strict_flags(self):
        self.run_harness()

    def test_guard_rules_and_state_machine_pass_under_sanitizers(self):
        with tempfile.TemporaryDirectory() as workdir:
            probe = Path(workdir) / 'probe.c'
            probe.write_text('int main(void) { return 0; }\n', encoding='utf-8')
            linked = subprocess.run([companion_tests.C_COMPILER, *SANITIZER_FLAGS, str(probe),
                                     '-o', str(Path(workdir) / 'probe')], capture_output=True, text=True)
            if linked.returncode != 0:
                self.skipTest('compiler has no ASan/UBSan runtime: sanitizer run not performed')
        self.run_harness(SANITIZER_FLAGS)


class GuardWiringTests(unittest.TestCase):
    def test_guard_header_exists_and_is_packaged(self):
        self.assertTrue(GUARD.is_file())
        for relative in ('companion/guard.h', 'tests/guard_host_harness.c', 'tests/test_guard_host.py'):
            self.assertIn(relative, package_source.PUBLIC_FILES)

    def test_guard_header_has_no_platform_includes(self):
        includes = re.findall(r'#\s*include\s*[<"]([^>"]+)[>"]', GUARD.read_text(encoding='utf-8'))
        self.assertEqual(sorted(includes), ['form_restore.h', 'stdbool.h', 'stdint.h'])

    def test_guard_mask_enables_exactly_form_58(self):
        match = re.search(r'#define\s+GUARD_ENABLED_FORMS_MASK\s+\(\s*UINT64_C\(1\)\s*<<\s*(\d+)\s*\)',
                          GUARD.read_text(encoding='utf-8'))
        self.assertIsNotNone(match)
        self.assertEqual([int(match.group(1))], [58])

    def test_verify_companion_accepts_source(self):
        verify_companion.check_source()

    def test_main_routes_every_write_through_gate(self):
        text = MAIN.read_text(encoding='utf-8')
        for needle in ('#include "guard.h"', 'guard_enable(', 'guard_disable(', 'OSGetMapVirtAddrRange(',
                       'guard_may_read_entry(guard_state.enabled,', 'guard_restored_alternate(kind_value, current)'):
            self.assertIn(needle, text)
        self.assertNotIn('guard_state.enabled)', text.replace('guard_may_read_entry(guard_state.enabled,', ''))
        # The pointer gate precedes every dereference of entry, and the write decision precedes the store.
        gate = text.index('guard_may_read_entry(')
        self.assertLess(gate, text.index('(uint8_t *)entry + 0x10'))
        self.assertLess(gate, text.index('*kind'))
        self.assertLess(text.index('guard_restored_alternate('), text.index('*alternate = restored;'))
        self.assertEqual(len(re.findall(r'^\s*\*alternate\s*=', text, re.M)), 1)


if __name__ == '__main__':
    unittest.main()
