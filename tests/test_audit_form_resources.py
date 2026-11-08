"""Pure-logic check of the form resource audit on synthetic paths (no game data)."""
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

TOOL = Path(__file__).resolve().parents[1] / 'tools' / 'audit_form_resources.py'
sys.path.insert(0, str(TOOL.parent))
from audit_form_resources import audit, folder_summary, input_problem


class AuditFormResourceTests(unittest.TestCase):
    def test_counts_entry_result_and_skeletons(self):
        entries = [
            ('fighter/koopa/motion/bodyentry/main.pac', 1),
            ('fighter/koopa/motion/bodyresult/main.pac', 1),
            ('fighter/koopa/model/body/c00/model.vbn', 8876),
            ('fighter/koopag/model/body/c00/model.vbn', 8204),
            ('fighter/koopagx/motion/bodyentry/main.pac', 1),
        ]
        base = folder_summary(entries, 'koopa')
        form = folder_summary(entries, 'koopag')
        self.assertEqual((base['bodyentry'], base['bodyresult'], base['model_vbn_sizes']), (1, 1, [8876]))
        self.assertEqual((form['files'], form['bodyentry'], form['bodyresult'], form['model_vbn_sizes']), (1, 0, 0, [8204]))

    def test_audit_covers_all_four_forms(self):
        self.assertEqual(set(audit([])), {'koopag', 'warioman', 'littlemacg', 'lucariom'})

    def test_missing_folders_name_the_bad_folder(self):
        with tempfile.TemporaryDirectory() as root:
            game = Path(root) / 'game'
            update = Path(root) / 'update'
            problem = input_problem(str(game), str(update))
            self.assertIn("no 'ls' file", problem)
            self.assertIn(str(game), problem)

    def test_update_without_patch_folder_is_reported(self):
        with tempfile.TemporaryDirectory() as root:
            (Path(root) / 'ls').write_bytes(b'')
            problem = input_problem(root, root)
            self.assertIn("no 'patch' folder", problem)

    def test_bad_input_prints_one_line_not_a_traceback(self):
        with tempfile.TemporaryDirectory() as root:
            missing = str(Path(root) / 'missing')
            ran = subprocess.run([sys.executable, '-I', str(TOOL), missing, missing],
                                 capture_output=True, text=True)
            self.assertEqual(ran.returncode, 1)
            self.assertNotIn('Traceback', ran.stderr)
            self.assertEqual(ran.stderr.count('\n'), 1)
            self.assertIn(missing, ran.stderr)


if __name__ == '__main__':
    unittest.main()
