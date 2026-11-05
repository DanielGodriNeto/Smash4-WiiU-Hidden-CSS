import sys
import tempfile
import unittest
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import check_regression_matrix as checker
import package_source

DATA = ROOT / 'docs' / 'regression-matrix.json'
DOC = ROOT / 'docs' / 'REGRESSION-MATRIX.md'
README = ROOT / 'README.md'
NEW_FILES = ('docs/REGRESSION-MATRIX.md', 'docs/regression-matrix.json',
             'tools/check_regression_matrix.py', 'tests/test_regression_matrix.py')
# Spec table (section 2 of the plan), written out independently of the checker.
SPEC_NA_PAIRS = [
    ('css', 'ko'), ('css', 'respawn'), ('css', 'sudden-death'), ('css', 'timeout'), ('css', 'results'),
    ('training', 'sudden-death'), ('training', 'timeout'), ('training', 'results'), ('training', 'select'),
    ('versus', 'select'), ('cpu', 'select'), ('rematch', 'select'),
]
SPEC_REASON = 'Spec reason.'
RUN_ID = 'run-001'
PASS_CELL = 'f58.versus.ko.en-us.off'


def make_run(**changes):
    run = {'id': RUN_ID, 'commit': '0123456789abcdef0123456789abcdef01234567', 'pack_sha256': 'a' * 64,
           'plugin_sha256': None, 'language': 'en-us', 'runtime': {'kind': 'hardware', 'version': 'v1.0'},
           'date': '2026-11-04', 'tester': 'tester-01', 'evidence': 'EV-20261104-001'}
    run.update(changes)
    return run


def make_result(**changes):
    result = {'cell': PASS_CELL, 'status': 'PASS', 'run': RUN_ID}
    result.update(changes)
    return result


def base_matrix(runs=(), results=()):
    return {
        'schema': 1,
        'not_applicable': [{'mode': mode, 'lifecycle': lifecycle, 'reason': SPEC_REASON}
                           for mode, lifecycle in SPEC_NA_PAIRS],
        'runs': list(runs),
        'results': list(results),
    }


def runs_by_id(*runs):
    return {run['id']: run for run in runs}


NA_SET = frozenset(SPEC_NA_PAIRS)


class RegressionMatrixDataTests(unittest.TestCase):
    def test_t01_enumerates_1260_unique_cells(self):
        cells = checker.enumerate_cells()
        self.assertEqual(len(cells), 1260)
        self.assertEqual(len({cell.id for cell in cells}), 1260)
        self.assertEqual({cell.subject for cell in cells},
                         {'f58', 'f59', 'f60', 'f61', 'roster', 'random', 'mii'})
        for cell in cells:
            self.assertEqual(cell.id, '.'.join([cell.subject, cell.mode, cell.lifecycle, cell.language, cell.plugin]))

    def test_t02_applicable_and_na_counts(self):
        counts = Counter(checker.status_map(base_matrix()).values())
        self.assertEqual(counts['N/A'], 504)
        self.assertEqual(counts['UNTESTED'], 756)

    def test_t03_pinned_cell_ids(self):
        statuses = checker.status_map(base_matrix())
        self.assertEqual(statuses['f58.css.select.en-us.off'], 'UNTESTED')
        self.assertEqual(statuses['f58.css.ko.en-us.on'], 'N/A')

    def test_t04_committed_initial_state_is_all_untested(self):
        data = checker.load_matrix()
        checker.validate_matrix(data)
        self.assertEqual(data['results'], [])
        self.assertEqual(data['runs'], [])
        counts = Counter(checker.status_map(data).values())
        self.assertEqual((counts['UNTESTED'], counts['PASS'], counts['FAIL'], counts['N/A']), (756, 0, 0, 504))

    def test_t05_not_applicable_set_is_exact(self):
        data = base_matrix()
        checker.validate_matrix(data)
        self.assertEqual([(entry['mode'], entry['lifecycle']) for entry in data['not_applicable']], SPEC_NA_PAIRS)
        duplicate = base_matrix()
        duplicate['not_applicable'][1] = dict(duplicate['not_applicable'][0])
        with self.assertRaisesRegex(ValueError, 'not_applicable'):
            checker.validate_matrix(duplicate)
        unknown = base_matrix()
        unknown['not_applicable'][0]['lifecycle'] = 'bogus'
        with self.assertRaisesRegex(ValueError, 'not_applicable'):
            checker.validate_matrix(unknown)
        too_long = base_matrix()
        too_long['not_applicable'][0]['reason'] = 'x' * 201
        with self.assertRaisesRegex(ValueError, 'reason'):
            checker.validate_matrix(too_long)
        empty = base_matrix()
        empty['not_applicable'][0]['reason'] = ''
        with self.assertRaisesRegex(ValueError, 'reason'):
            checker.validate_matrix(empty)

    def test_t06_malformed_json_and_deep_nesting_raise_value_error(self):
        with self.assertRaises(ValueError):
            checker.parse_strict(b'{')
        with self.assertRaisesRegex(ValueError, 'nested too deeply'):
            checker.parse_strict(b'[' * 100000)

    def test_t07_duplicate_keys_raise(self):
        raw = b'{"schema": 1, "schema": 1, "not_applicable": [], "runs": [], "results": []}'
        with self.assertRaisesRegex(ValueError, 'duplicate'):
            checker.parse_strict(raw)

    def test_t08_nan_and_infinity_raise(self):
        for literal in (b'NaN', b'Infinity', b'-Infinity'):
            with self.subTest(literal=literal):
                with self.assertRaisesRegex(ValueError, 'NaN and Infinity'):
                    checker.parse_strict(b'{"schema": ' + literal + b'}')

    def test_t09_wrong_types_raise(self):
        schema_string = base_matrix()
        schema_string['schema'] = '1'
        schema_bool = base_matrix()
        schema_bool['schema'] = True
        results_object = base_matrix()
        results_object['results'] = {}
        with self.assertRaisesRegex(ValueError, 'schema'):
            checker.validate_matrix(schema_string)
        with self.assertRaisesRegex(ValueError, 'schema'):
            checker.validate_matrix(schema_bool)
        with self.assertRaisesRegex(ValueError, 'results'):
            checker.validate_matrix(results_object)
        with self.assertRaisesRegex(ValueError, 'date'):
            checker.validate_run(make_run(date=20261104))

    def test_t10_unknown_keys_raise(self):
        with self.assertRaisesRegex(ValueError, 'unexpected key'):
            checker.validate_run(make_run(name='Someone'))
        extra = base_matrix()
        extra['notes'] = 'x'
        with self.assertRaisesRegex(ValueError, 'unexpected key'):
            checker.validate_matrix(extra)

    def test_t11_oversize_file_rejected_before_parse(self):
        with tempfile.TemporaryDirectory() as workdir:
            path = Path(workdir) / 'matrix.json'
            # Not JSON: a parse attempt would fail with a different message than the size cap.
            path.write_bytes(b'x' * 200001)
            with self.assertRaisesRegex(ValueError, 'size cap'):
                checker.load_matrix(path)

    def test_t12_path_like_and_control_ids_raise(self):
        with self.assertRaisesRegex(ValueError, 'cell'):
            checker.validate_result(make_result(cell='f58/css.ko.en-us.off'), runs_by_id(make_run()), NA_SET)
        with self.assertRaisesRegex(ValueError, 'id'):
            checker.validate_run(make_run(id='../run-001'))
        with self.assertRaisesRegex(ValueError, 'id'):
            checker.validate_run(make_run(id='run-001\x00'))

    def test_t13_text_hygiene_rejects_control_and_non_ascii(self):
        with self.assertRaisesRegex(ValueError, 'symptom'):
            checker.validate_result(make_result(status='FAIL', symptom='bad\x1b[0m'),
                                    runs_by_id(make_run()), NA_SET)
        with self.assertRaisesRegex(ValueError, 'tester'):
            checker.validate_run(make_run(tester='tester\t1'))
        accented = base_matrix()
        accented['not_applicable'][0]['reason'] = 'Caf\u00e9'
        with self.assertRaisesRegex(ValueError, 'reason'):
            checker.validate_matrix(accented)

    def test_t14_status_vocabulary_is_pass_or_fail_only(self):
        runs = runs_by_id(make_run())
        for status in ('UNTESTED', 'N/A', 'pass'):
            with self.subTest(status=status):
                with self.assertRaisesRegex(ValueError, 'status'):
                    checker.validate_result(make_result(status=status), runs, NA_SET)

    def test_t15_run_evidence_fields_are_required_and_non_empty(self):
        empty_values = {'commit': '', 'pack_sha256': '', 'runtime': {}, 'date': '', 'tester': '', 'evidence': ''}
        for field, empty in empty_values.items():
            with self.subTest(field=field, case='missing'):
                run = make_run()
                del run[field]
                with self.assertRaisesRegex(ValueError, field):
                    checker.validate_run(run)
            with self.subTest(field=field, case='empty'):
                with self.assertRaisesRegex(ValueError, field):
                    checker.validate_run(make_run(**{field: empty}))

    def test_t16_evidence_allowlist_accepts_ids_and_rejects_paths(self):
        checker.validate_evidence_pointer('EV-20261104-001')
        checker.validate_evidence_pointer(
            'https://github.com/Wiirizon/Smash4-WiiU-Hidden-CSS/issues/7#issuecomment-1234567890')
        # Windows profile path built from parts so this file does not contain a personal-path pattern.
        windows_profile = 'C:' + chr(92) + 'Users' + chr(92) + 'x' + chr(92) + 'a.mp4'
        rejected = ['', 'TBD', 'placeholder', windows_profile, '/home/x/a.mp4', '~/a.mp4',
                    '%USERPROFILE%\\a', 'file:///x', 'https://example.com/x']
        for text in rejected:
            with self.subTest(text=text):
                with self.assertRaisesRegex(ValueError, 'evidence'):
                    checker.validate_evidence_pointer(text)

    def test_t17_fail_needs_symptom_and_pass_forbids_it(self):
        runs = runs_by_id(make_run())
        with self.assertRaisesRegex(ValueError, 'symptom'):
            checker.validate_result(make_result(status='FAIL'), runs, NA_SET)
        with self.assertRaisesRegex(ValueError, 'symptom'):
            checker.validate_result(make_result(status='PASS', symptom='Freeze'), runs, NA_SET)
        checker.validate_result(make_result(status='FAIL', symptom='Freeze on results'), runs, NA_SET)

    def test_t18_na_cell_cannot_carry_result(self):
        cell = 'f58.css.ko.en-us.on'
        run = make_run(plugin_sha256='b' * 64)
        with self.assertRaisesRegex(ValueError, 'N/A'):
            checker.validate_result(make_result(cell=cell), runs_by_id(run), NA_SET)

    def test_t19_plugin_state_must_match_cell(self):
        runs = runs_by_id(make_run())
        with self.assertRaisesRegex(ValueError, 'plugin'):
            checker.validate_result(make_result(cell='f58.versus.ko.en-us.on'), runs, NA_SET)
        hashed = runs_by_id(make_run(plugin_sha256='b' * 64))
        with self.assertRaisesRegex(ValueError, 'plugin'):
            checker.validate_result(make_result(), hashed, NA_SET)

    def test_t20_language_must_match_cell(self):
        with self.assertRaisesRegex(ValueError, 'language'):
            checker.validate_result(make_result(cell='f58.versus.ko.fr.off'), runs_by_id(make_run()), NA_SET)

    def test_t21_link_integrity(self):
        with self.subTest(case='duplicate cell'):
            data = base_matrix(runs=[make_run()], results=[make_result(), make_result()])
            with self.assertRaisesRegex(ValueError, 'duplicate'):
                checker.validate_matrix(data)
        with self.subTest(case='orphan run'):
            with self.assertRaisesRegex(ValueError, 'not referenced'):
                checker.validate_matrix(base_matrix(runs=[make_run()], results=[]))
        with self.subTest(case='dangling run'):
            with self.assertRaisesRegex(ValueError, 'references no run'):
                checker.validate_matrix(base_matrix(runs=[], results=[make_result()]))

    def test_t22_date_and_commit_format(self):
        with self.assertRaisesRegex(ValueError, 'date'):
            checker.validate_run(make_run(date='2026-02-30'))
        with self.assertRaisesRegex(ValueError, 'commit'):
            checker.validate_run(make_run(commit='xyz'))
        with self.assertRaisesRegex(ValueError, 'commit'):
            checker.validate_run(make_run(commit='ABCDEF0'))

    def test_t23_render_is_deterministic_and_escapes_pipes(self):
        data = base_matrix(runs=[make_run()], results=[make_result(status='FAIL', symptom='a|b')])
        checker.validate_matrix(data)
        first = checker.render_markdown(data)
        self.assertEqual(first, checker.render_markdown(data))
        self.assertIn('a\\|b', first)
        self.assertTrue(first.isascii())

    def test_t24_committed_doc_matches_data(self):
        data = checker.load_matrix()
        checker.validate_matrix(data)
        checker.check_doc(data, DOC)
        self.assertTrue(DOC.read_bytes().isascii())

    def test_t25_drift_is_detected(self):
        data = base_matrix(runs=[make_run()], results=[make_result()])
        checker.validate_matrix(data)
        with self.assertRaisesRegex(ValueError, 'out of date'):
            checker.check_doc(data, DOC)
        checker.check_doc(checker.load_matrix(), DOC)

    def test_t26_results_must_be_sorted_by_cell(self):
        later = make_result(cell='f58.versus.respawn.en-us.off')
        data = base_matrix(runs=[make_run()], results=[later, make_result()])
        with self.assertRaisesRegex(ValueError, 'sorted'):
            checker.validate_matrix(data)


class RegressionMatrixPackagingTests(unittest.TestCase):
    def test_t27_packaging_and_hygiene(self):
        for relative in NEW_FILES:
            self.assertIn(relative, package_source.PUBLIC_FILES)
        package_source.scan(list(NEW_FILES))
        self.assertLess(len(DATA.read_bytes()), 200000)

    def test_t28_readme_links_the_matrix(self):
        self.assertIn('docs/REGRESSION-MATRIX.md', README.read_text(encoding='utf-8'))


if __name__ == '__main__':
    unittest.main()
