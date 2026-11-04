import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import build
import package_source
import verify_companion

COMPANION = ROOT / 'companion'
HEADER = COMPANION / 'form_restore.h'
MAIN = COMPANION / 'main.c'
C_FLAGS = ['-std=gnu11', '-Wall', '-Wextra', '-Werror']
EXPECTED_PAIRS = [(58, 15), (59, 22), (60, 41), (61, 30)]
OLD_HARDCODED_LINES = ('*kind == 58u', '*alternate == 15u', '*alternate = 58u')


def find_c_compiler():
    for name in ('gcc', 'cc', 'clang'):
        path = shutil.which(name)
        if path:
            return path
    return None


C_COMPILER = find_c_compiler()


def header_pairs():
    text = HEADER.read_text(encoding='utf-8')
    body = re.search(r'form_restore_pairs\[\] = \{(.*?)\n\};', text, re.S)
    if body is None:
        raise ValueError('form_restore_pairs table not found in header')
    return [(int(form), int(base)) for form, base in
            re.findall(r'\{\s*(\d+)u?\s*,\s*(\d+)u?\s*\}', body.group(1))]


def build_donor_bases():
    text = (ROOT / 'tools' / 'build.py').read_text(encoding='utf-8')
    return [(int(donor), int(base)) for donor, base in
            re.findall(r'\((16|23|39|31),(15|22|41|30)\)', text)]


class CompanionValidationTests(unittest.TestCase):
    def test_public_companion_has_required_guards(self):
        verify_companion.check_source()


class FormRestoreTableTests(unittest.TestCase):
    def test_form_restore_table_is_exact_unique_and_packaged(self):
        self.assertTrue(HEADER.is_file())
        pairs = header_pairs()
        self.assertEqual(pairs, EXPECTED_PAIRS)
        self.assertEqual(len({form for form, _ in pairs}), 4)
        self.assertEqual(len({base for _, base in pairs}), 4)
        self.assertIn('companion/form_restore.h', package_source.PUBLIC_FILES)

    def test_form_restore_table_matches_builder_fighters(self):
        ids = [fighter['id'] for fighter in build.FIGHTERS[:4]]
        self.assertEqual(ids, [form for form, _ in EXPECTED_PAIRS])
        self.assertEqual(build_donor_bases(), [(16, 15), (23, 22), (39, 41), (31, 30)])
        self.assertEqual(header_pairs(), list(zip(ids, [base for _, base in build_donor_bases()])))

    def test_companion_main_uses_helper_without_hardcoded_pair(self):
        text = MAIN.read_text(encoding='utf-8')
        self.assertIsNotNone(re.search(r'guard_restored_alternate\(\s*kind_value\s*,', text))
        for line in OLD_HARDCODED_LINES:
            self.assertNotIn(line, text)
        self.assertIsNone(re.search(r'\b(58|15)u\b', text))
        verify_companion.check_source()


def compile_c(source_path, exe_path=None, syntax_only=False):
    command = [C_COMPILER, *C_FLAGS, '-I', str(COMPANION), str(source_path)]
    if syntax_only:
        command.append('-fsyntax-only')
    else:
        command += ['-o', str(exe_path)]
    return subprocess.run(command, capture_output=True, text=True)


@unittest.skipUnless(C_COMPILER, 'no gcc, cc or clang on PATH: host C harness not run')
class FormRestoreHostTests(unittest.TestCase):
    def run_harness(self, name, body):
        with tempfile.TemporaryDirectory() as workdir:
            source = Path(workdir) / (name + '.c')
            exe = Path(workdir) / (name + '.exe')
            source.write_text('#include <stdio.h>\n#include "form_restore.h"\n' + body, encoding='utf-8')
            built = compile_c(source, exe)
            self.assertEqual(built.returncode, 0, 'compile failed:\n' + built.stderr)
            ran = subprocess.run([str(exe)], capture_output=True, text=True)
            self.assertEqual(ran.returncode, 0, 'harness failed:\n' + ran.stderr)

    def test_c1_four_form_mappings(self):
        self.run_harness('c1', r'''
static int failures = 0;
static void expect(uint32_t kind, uint32_t alternate, uint32_t want) {
    uint32_t got = form_restore_alternate(kind, alternate);
    if (got != want) {
        fprintf(stderr, "kind %u alternate %u: got %u want %u\n", kind, alternate, got, want);
        failures++;
    }
}
int main(void) {
    expect(58u, 15u, 58u);
    expect(59u, 22u, 59u);
    expect(60u, 41u, 60u);
    expect(61u, 30u, 61u);
    return failures ? 1 : 0;
}
''')

    def test_c2_fail_closed_exhaustive_sweep(self):
        self.run_harness('c2', r'''
static int is_exact_pair(uint32_t kind, uint32_t alternate) {
    return (kind == 58u && alternate == 15u) || (kind == 59u && alternate == 22u) ||
           (kind == 60u && alternate == 41u) || (kind == 61u && alternate == 30u);
}
int main(void) {
    static const uint32_t named[][3] = {
        {58u, 0u, 0u}, {58u, 22u, 22u}, {58u, 41u, 41u}, {15u, 15u, 15u},
        {22u, 22u, 22u}, {41u, 41u, 41u}, {30u, 30u, 30u}, {62u, 0u, 0u},
        {57u, 15u, 15u}, {0u, 0u, 0u},
    };
    uint32_t changed = 0;
    for (uint32_t i = 0; i < sizeof named / sizeof named[0]; ++i) {
        if (form_restore_alternate(named[i][0], named[i][1]) != named[i][2]) {
            fprintf(stderr, "named case %u failed\n", i);
            return 1;
        }
    }
    for (uint32_t kind = 0; kind <= 255u; ++kind) {
        for (uint32_t alternate = 0; alternate <= 255u; ++alternate) {
            uint32_t got = form_restore_alternate(kind, alternate);
            uint32_t want = is_exact_pair(kind, alternate) ? kind : alternate;
            if (got != want) {
                fprintf(stderr, "kind %u alternate %u: got %u want %u\n", kind, alternate, got, want);
                return 1;
            }
            if (got != alternate) {
                changed++;
            }
        }
    }
    if (changed != 4u) {
        fprintf(stderr, "changed %u entries, expected 4\n", changed);
        return 1;
    }
    return 0;
}
''')

    def test_c3_idempotent_and_scan_order_independent(self):
        self.run_harness('c3', r'''
static const uint32_t kinds[4] = {58u, 59u, 60u, 61u};
static const uint32_t bases[4] = {15u, 22u, 41u, 30u};
static uint32_t reverse_scan(uint32_t kind, uint32_t alternate) {
    for (int i = 3; i >= 0; --i) {
        if (kind == kinds[i]) {
            return alternate == bases[i] ? kind : alternate;
        }
    }
    return alternate;
}
int main(void) {
    for (uint32_t kind = 0; kind <= 255u; ++kind) {
        for (uint32_t alternate = 0; alternate <= 255u; ++alternate) {
            uint32_t once = form_restore_alternate(kind, alternate);
            if (form_restore_alternate(kind, once) != once) {
                fprintf(stderr, "not idempotent at kind %u alternate %u\n", kind, alternate);
                return 1;
            }
            if (reverse_scan(kind, alternate) != once) {
                fprintf(stderr, "scan order changes result at kind %u alternate %u\n", kind, alternate);
                return 1;
            }
        }
    }
    return 0;
}
''')

    def test_c4_header_syntax_under_strict_flags(self):
        with tempfile.TemporaryDirectory() as workdir:
            source = Path(workdir) / 'driver.c'
            source.write_text('#include "form_restore.h"\n'
                              'uint32_t driver(uint32_t k, uint32_t a) { return form_restore_alternate(k, a); }\n',
                              encoding='utf-8')
            checked = compile_c(source, syntax_only=True)
            self.assertEqual(checked.returncode, 0, 'syntax check failed:\n' + checked.stderr)


if __name__ == '__main__':
    unittest.main()
