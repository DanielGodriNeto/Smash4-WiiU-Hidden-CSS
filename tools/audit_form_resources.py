"""Count entry/result animation files and skeleton sizes for each Final Smash form versus its base fighter.

Reads the user's own Smash 4 dump (game and update `content` folders). Prints counts, folder names and sizes only;
no game data is written anywhere. Usage: python tools/audit_form_resources.py GAME_CONTENT UPDATE_CONTENT
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from smash4 import Dump

PAIRS = (('koopa', 'koopag'), ('wario', 'warioman'), ('littlemac', 'littlemacg'), ('lucario', 'lucariom'))


def folder_summary(entries, fighter):
    """entries: iterable of (path, decompressed_size). Return counts of body entry/result files and model.vbn sizes."""
    prefix = 'fighter/' + fighter + '/'
    mine = [(p, s) for p, s in entries if p.startswith(prefix)]
    return {
        'files': len(mine),
        'bodyentry': sum(1 for p, _ in mine if '/motion/bodyentry/' in p),
        'bodyresult': sum(1 for p, _ in mine if '/motion/bodyresult/' in p),
        'model_vbn_sizes': sorted({s for p, s in mine if p.endswith('/model.vbn')}),
    }


def audit(entries):
    entries = list(entries)
    return {form: {'base': folder_summary(entries, base), 'form': folder_summary(entries, form)} for base, form in PAIRS}


def main(argv):
    if len(argv) != 3:
        sys.exit(__doc__)
    resource = Dump(argv[1], argv[2]).resources['data']
    print(json.dumps(audit((e.path, e.decompressed) for e in resource.entries if not e.directory), indent=2))


if __name__ == '__main__':
    main(sys.argv)
