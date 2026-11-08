"""Count entry/result animation files and skeleton sizes for each Final Smash form versus its base fighter.

Reads the user's own Smash 4 dump (game and update `content` folders). Prints counts, folder names and sizes only;
no game data is written anywhere. Usage: python tools/audit_form_resources.py GAME_CONTENT UPDATE_CONTENT
"""
import json
import struct
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


def input_problem(game, update):
    """Return a one-line reason the two folders cannot hold a dump, or None when both look right."""
    if not (Path(game) / 'ls').is_file():
        return f"audit_form_resources: game folder has no 'ls' file: {game}"
    if not (Path(update) / 'patch').is_dir():
        return f"audit_form_resources: update folder has no 'patch' folder: {update}"
    return None


def audit_dump(game, update):
    resource = Dump(game, update).resources.get('data')
    if resource is None:
        raise ValueError('update patch folder has no resource data file')
    return audit((e.path, e.decompressed) for e in resource.entries if not e.directory)


def main(argv):
    if len(argv) != 3:
        sys.exit(__doc__)
    problem = input_problem(argv[1], argv[2])
    if problem:
        sys.exit(problem)
    try:
        print(json.dumps(audit_dump(argv[1], argv[2]), indent=2))
    except (OSError, ValueError, struct.error) as err:
        sys.exit(f'audit_form_resources: cannot read the dump: {err}')


if __name__ == '__main__':
    main(sys.argv)
