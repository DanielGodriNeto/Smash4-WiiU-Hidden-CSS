"""Pure-logic check of the form resource audit on synthetic paths (no game data)."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from audit_form_resources import audit, folder_summary


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


if __name__ == '__main__':
    unittest.main()
