"""Validate the hidden-fighter regression matrix data and its generated Markdown.

The checker validates record shape only. A PASS is a maintainer attestation;
nothing here proves that a cell was played on hardware or in Cemu.
"""
from __future__ import annotations

import argparse
import codecs
import datetime
import functools
import itertools
import json
import re
import sys
from pathlib import Path
from typing import NamedTuple, cast

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / 'docs' / 'regression-matrix.json'
DOC_PATH = ROOT / 'docs' / 'REGRESSION-MATRIX.md'
MAX_BYTES = 200000
SCHEMA = 1
SUBJECTS = {
    'f58': 'Giga Bowser', 'f59': 'Wario-Man', 'f60': 'Giga Mac', 'f61': 'Mega Lucario',
    'roster': 'Regular roster', 'random': 'Random slot', 'mii': 'Standard Mii',
}
MODES = ('css', 'training', 'versus', 'cpu', 'rematch')
LIFECYCLES = ('ko', 'respawn', 'sudden-death', 'timeout', 'results', 'select')
LANGUAGES = ('en-us', 'fr', 'es')
LANGUAGE_LABELS = {'en-us': 'US English', 'fr': 'French', 'es': 'Spanish'}
PLUGINS = ('on', 'off')
RESULT_STATUSES = ('PASS', 'FAIL')
RUNTIME_KINDS = ('hardware', 'cemu')
NOT_APPLICABLE_PAIRS = (
    ('css', 'ko'), ('css', 'respawn'), ('css', 'sudden-death'), ('css', 'timeout'), ('css', 'results'),
    ('training', 'sudden-death'), ('training', 'timeout'), ('training', 'results'), ('training', 'select'),
    ('versus', 'select'), ('cpu', 'select'), ('rematch', 'select'),
)
MATRIX_KEYS = frozenset({'schema', 'not_applicable', 'runs', 'results'})
NA_KEYS = frozenset({'mode', 'lifecycle', 'reason'})
RUN_KEYS = frozenset({'id', 'commit', 'pack_sha256', 'plugin_sha256', 'language', 'runtime',
                      'date', 'tester', 'evidence'})
RUNTIME_KEYS = frozenset({'kind', 'version'})
RESULT_KEYS = frozenset({'cell', 'status', 'run', 'symptom'})
REQUIRED_RESULT_KEYS = frozenset({'cell', 'status', 'run'})
REASON_MAX = 200
SYMPTOM_MAX = 200
VERSION_MAX = 40
RUN_ID = re.compile(r'run-[0-9]{3}')
COMMIT = re.compile(r'[0-9a-f]{7,40}')
SHA256 = re.compile(r'[0-9a-f]{64}')
DATE = re.compile(r'[0-9]{4}-[0-9]{2}-[0-9]{2}')
TESTER = re.compile(r'[a-z0-9][a-z0-9-]{1,31}')
EVIDENCE_ID = re.compile(r'EV-[0-9]{8}-[0-9]{3}')
ISSUE_COMMENT = re.compile(
    r'https://github\.com/Wiirizon/Smash4-WiiU-Hidden-CSS/issues/[0-9]+#issuecomment-[0-9]+')
PATH_MARKERS = re.compile(r'\b[A-Za-z]:[\\/]|\\|/Users/|/home/|~|%|file:', re.IGNORECASE)


class Cell(NamedTuple):
    id: str
    subject: str
    mode: str
    lifecycle: str
    language: str
    plugin: str


def enumerate_cells() -> list[Cell]:
    return [Cell('.'.join(parts), *parts)
            for parts in itertools.product(SUBJECTS, MODES, LIFECYCLES, LANGUAGES, PLUGINS)]


@functools.lru_cache(maxsize=None)
def cell_index() -> dict[str, Cell]:
    return {cell.id: cell for cell in enumerate_cells()}


def parse_strict(raw: bytes) -> object:
    if raw.startswith(codecs.BOM_UTF8):
        raise ValueError('data file: byte order mark not allowed')
    try:
        text = raw.decode('utf-8')
    except UnicodeDecodeError as exc:
        raise ValueError('data file: not valid UTF-8') from exc
    try:
        return json.loads(text, object_pairs_hook=_reject_duplicates, parse_constant=_reject_constant)
    except RecursionError as exc:
        raise ValueError('data file: JSON nested too deeply') from exc


def _reject_duplicates(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('data file: duplicate JSON key')
        result[key] = value
    return result


def _reject_constant(name: str) -> object:
    raise ValueError('data file: NaN and Infinity are not allowed')


def load_matrix(path: Path = DATA_PATH) -> dict[str, object]:
    if path.stat().st_size > MAX_BYTES:
        raise ValueError('data file: exceeds size cap')
    with path.open('rb') as handle:
        raw = handle.read(MAX_BYTES + 1)
    if len(raw) > MAX_BYTES:
        raise ValueError('data file: exceeds size cap')
    data = parse_strict(raw)
    if not isinstance(data, dict):
        raise ValueError('matrix: must be an object')
    return cast(dict[str, object], data)


def _require_keys(obj: dict[str, object], allowed: frozenset[str], required: frozenset[str], where: str) -> None:
    if set(obj) - allowed:
        raise ValueError(where + ': unexpected key')
    missing = sorted(required - set(obj))
    if missing:
        raise ValueError(where + ": missing field '" + missing[0] + "'")


def _matches(value: object, pattern: re.Pattern[str]) -> bool:
    return isinstance(value, str) and pattern.fullmatch(value) is not None


def _printable(value: object, where: str, max_len: int) -> None:
    if not isinstance(value, str) or not 1 <= len(value) <= max_len or not value.isascii() or not value.isprintable():
        raise ValueError(where + ': must be printable ASCII, 1-' + str(max_len) + ' characters')


def validate_evidence_pointer(text: object) -> None:
    if not isinstance(text, str):
        raise ValueError('evidence: must be text')
    if PATH_MARKERS.search(text):
        raise ValueError('evidence: path-like text is not allowed')
    if _matches(text, EVIDENCE_ID) or _matches(text, ISSUE_COMMENT):
        return
    raise ValueError('evidence: must be EV-YYYYMMDD-NNN or a same-repo issue comment URL')


def _validate_runtime(runtime: object) -> None:
    if not isinstance(runtime, dict):
        raise ValueError('run.runtime: must be an object')
    _require_keys(runtime, RUNTIME_KEYS, RUNTIME_KEYS, 'run.runtime')
    if runtime['kind'] not in RUNTIME_KINDS:
        raise ValueError('run.runtime.kind: must be hardware or cemu')
    _printable(runtime['version'], 'run.runtime.version', VERSION_MAX)


def _validate_date(value: object) -> None:
    if not _matches(value, DATE):
        raise ValueError('run.date: must be YYYY-MM-DD')
    try:
        datetime.date.fromisoformat(cast(str, value))
    except ValueError as exc:
        raise ValueError('run.date: not a valid calendar date') from exc


def validate_run(run: object) -> None:
    if not isinstance(run, dict):
        raise ValueError('run: must be an object')
    _require_keys(run, RUN_KEYS, RUN_KEYS, 'run')
    if not _matches(run['id'], RUN_ID):
        raise ValueError('run.id: must be run-NNN')
    if not _matches(run['commit'], COMMIT):
        raise ValueError('run.commit: must be 7-40 lowercase hex characters')
    if run['plugin_sha256'] is not None and not _matches(run['plugin_sha256'], SHA256):
        raise ValueError('run.plugin_sha256: must be null or 64 lowercase hex characters')
    if not _matches(run['pack_sha256'], SHA256):
        raise ValueError('run.pack_sha256: must be 64 lowercase hex characters')
    if run['language'] not in LANGUAGES:
        raise ValueError('run.language: unknown language')
    _validate_runtime(run['runtime'])
    _validate_date(run['date'])
    if not _matches(run['tester'], TESTER):
        raise ValueError('run.tester: must be a lowercase handle, 2-32 characters')
    validate_evidence_pointer(run['evidence'])


def _applicable_cell(value: object, na_pairs: frozenset[tuple[str, str]]) -> Cell:
    cell = cell_index().get(value) if isinstance(value, str) else None
    if cell is None:
        raise ValueError('result.cell: unknown cell id')
    if (cell.mode, cell.lifecycle) in na_pairs:
        raise ValueError('result.cell: N/A cell cannot carry a result')
    return cell


def validate_result(result: object, runs: dict[str, dict[str, object]],
                    na_pairs: frozenset[tuple[str, str]]) -> None:
    if not isinstance(result, dict):
        raise ValueError('result: must be an object')
    _require_keys(result, RESULT_KEYS, REQUIRED_RESULT_KEYS, 'result')
    cell = _applicable_cell(result['cell'], na_pairs)
    if result['status'] not in RESULT_STATUSES:
        raise ValueError('result.status: must be PASS or FAIL')
    run_id = result['run']
    if not isinstance(run_id, str) or run_id not in runs:
        raise ValueError('result.run: references no run')
    run = runs[run_id]
    if run['language'] != cell.language:
        raise ValueError('result.run: language differs from cell')
    if (run['plugin_sha256'] is not None) != (cell.plugin == 'on'):
        raise ValueError('result.run: plugin state differs from cell')
    if result['status'] == 'FAIL':
        if 'symptom' not in result:
            raise ValueError('result.symptom: required for FAIL')
        _printable(result['symptom'], 'result.symptom', SYMPTOM_MAX)
    elif 'symptom' in result:
        raise ValueError('result.symptom: forbidden on PASS')


def _validate_not_applicable(entries: object) -> None:
    if not isinstance(entries, list):
        raise ValueError('not_applicable: must be a list')
    for entry in entries:
        if not isinstance(entry, dict):
            raise ValueError('not_applicable: entries must be objects')
        _require_keys(entry, NA_KEYS, NA_KEYS, 'not_applicable')
        if entry['mode'] not in MODES:
            raise ValueError('not_applicable.mode: unknown value')
        if entry['lifecycle'] not in LIFECYCLES:
            raise ValueError('not_applicable.lifecycle: unknown value')
        _printable(entry['reason'], 'not_applicable.reason', REASON_MAX)
    pairs = tuple((entry['mode'], entry['lifecycle']) for entry in cast(list[dict[str, object]], entries))
    if pairs != NOT_APPLICABLE_PAIRS:
        raise ValueError('not_applicable: must list the 12 rule pairs once, in enum order')


def _validate_runs(runs: object) -> dict[str, dict[str, object]]:
    if not isinstance(runs, list):
        raise ValueError('runs: must be a list')
    for run in runs:
        validate_run(run)
    typed = cast(list[dict[str, object]], runs)
    ids = [str(run['id']) for run in typed]
    if len(set(ids)) != len(ids):
        raise ValueError('runs.id: duplicate run id')
    if ids != sorted(ids):
        raise ValueError('runs: must be sorted by id')
    return {str(run['id']): run for run in typed}


def _validate_results(results: object, runs: dict[str, dict[str, object]],
                      na_pairs: frozenset[tuple[str, str]]) -> list[dict[str, object]]:
    if not isinstance(results, list):
        raise ValueError('results: must be a list')
    for result in results:
        validate_result(result, runs, na_pairs)
    typed = cast(list[dict[str, object]], results)
    cells = [str(result['cell']) for result in typed]
    if len(set(cells)) != len(cells):
        raise ValueError('results.cell: duplicate cell')
    if cells != sorted(cells):
        raise ValueError('results: must be sorted by cell')
    return typed


def validate_matrix(data: object) -> None:
    if not isinstance(data, dict):
        raise ValueError('matrix: must be an object')
    _require_keys(data, MATRIX_KEYS, MATRIX_KEYS, 'matrix')
    if type(data['schema']) is not int or data['schema'] != SCHEMA:
        raise ValueError('schema: must be integer 1')
    _validate_not_applicable(data['not_applicable'])
    na_pairs = frozenset(NOT_APPLICABLE_PAIRS)
    runs = _validate_runs(data['runs'])
    results = _validate_results(data['results'], runs, na_pairs)
    referenced = {result['run'] for result in results}
    for run_id in runs:
        if run_id not in referenced:
            raise ValueError('runs.id: run is not referenced by any result')


def na_pairs_of(data: dict[str, object]) -> frozenset[tuple[str, str]]:
    entries = cast(list[dict[str, str]], data['not_applicable'])
    return frozenset((entry['mode'], entry['lifecycle']) for entry in entries)


def status_map(data: dict[str, object]) -> dict[str, str]:
    na_pairs = na_pairs_of(data)
    statuses = {cell.id: 'N/A' if (cell.mode, cell.lifecycle) in na_pairs else 'UNTESTED'
                for cell in enumerate_cells()}
    for result in cast(list[dict[str, str]], data['results']):
        statuses[result['cell']] = result['status']
    return statuses


def _cell_text(text: str) -> str:
    return text.replace('|', '\\|')


def _cell_label(cell: Cell, statuses: dict[str, str], results: dict[str, dict[str, str]],
                na_numbers: dict[tuple[str, str], int]) -> str:
    key = (cell.mode, cell.lifecycle)
    if key in na_numbers:
        return 'N/A #' + str(na_numbers[key])
    status = statuses[cell.id]
    if status == 'UNTESTED':
        return status
    result = results[cell.id]
    label = status + ' ' + result['run']
    return label + ': ' + result['symptom'] if status == 'FAIL' else label


def _header_lines() -> list[str]:
    return [
        '# Hidden-fighter regression matrix',
        '',
        'Generated from `docs/regression-matrix.json` by `tools/check_regression_matrix.py --write`. '
        'Do not edit by hand.',
        '',
        'A PASS is a maintainer attestation based on a run record. It is not a tool result: the checker '
        'validates the shape of records and cannot confirm that a cell was played. Every cell stays '
        'UNTESTED until maintainer run records exist.',
        '',
    ]


def _status_lines() -> list[str]:
    return [
        '## Status and evidence', '',
        '- UNTESTED: no result entry. Default for every applicable cell; carries no evidence.',
        '- PASS: a result entry pointing to a run record. The maintainer observed every pass criterion '
        'in the cell on that run.',
        '- FAIL: a result entry, a run record and a symptom (printable ASCII, 1-200 characters). Stays '
        'FAIL until a later run passes the cell.',
        '- N/A: derived from a not-applicable rule. Never appears in results.',
        '- Earlier user reports (results softlock, T-pose, death restoring Bowser) lack run metadata and '
        'stay UNTESTED until a maintainer run confirms them.',
        '',
        'Run records: one per session, one language and one plugin state per run, plugin state fixed at '
        'boot. Fields: id, commit, pack SHA-256, plugin SHA-256 (none when the plugin is off), language, '
        'runtime (kind and version), date, tester handle and evidence ID.',
        '',
        'Evidence: `EV-YYYYMMDD-NNN` maps to clips and logs in a private log outside the repository, or is '
        'a comment URL on the project issue tracker. The Random control records which fighter Random drew '
        'in that log.',
        '',
    ]


def _dimension_lines() -> list[str]:
    return [
        '## Dimensions', '',
        'Cell id: `subject.mode.lifecycle.language.plugin`. The full product is 7 x 5 x 6 x 3 x 2 = 1260 '
        'cells: 756 applicable and 504 N/A.',
        '',
        '- Subjects: f58 Giga Bowser, f59 Wario-Man, f60 Giga Mac, f61 Mega Lucario (Final Smash forms), '
        'and the controls roster, random and mii.',
        '- Modes: css, training, versus, cpu, rematch.',
        '- Lifecycles: ko, respawn, sudden-death, timeout, results, select.',
        '- Languages: en-us (US English), fr, es. Columns show the setting; the exact console label is '
        'kept in the private evidence log.',
        '- Plugin: on or off. Plugin ON for 59-61 is inert by design: a PASS means no regression, not that '
        'the feature works.',
        '- `select` is an added sixth lifecycle: open CSS, cursor over additions, select, cancel, reselect, '
        'check portrait and nameplate render. The five issue lifecycles are match events and CSS has no '
        'match, so `select` is the only CSS lifecycle. The maintainer may reject it.',
        '- Out of scope: Fighting Mii 62-64, because they are enemy actors and issue #7 names only forms 58-61.',
        '- Out of scope: combinations of hidden forms; a separate table is planned.',
        '',
    ]


def _controls_lines() -> list[str]:
    return [
        '## Controls', '',
        '- roster: a regular roster fighter, chosen from the normal CSS.',
        '- random: the Random slot. A PASS does not prove that a hidden form was drawn; the run must record '
        'which fighter Random drew.',
        '- mii: a standard Mii from the normal Mii menu. Not the candidate rows 62-64.',
        '',
    ]


def _na_lines(data: dict[str, object]) -> list[str]:
    lines = ['## Not applicable rules', '', '| # | Mode | Lifecycle | Reason |', '| --- | --- | --- | --- |']
    entries = cast(list[dict[str, str]], data['not_applicable'])
    for number, entry in enumerate(entries, start=1):
        lines.append('| {} | {} | {} | {} |'.format(number, entry['mode'], entry['lifecycle'],
                                                    _cell_text(entry['reason'])))
    return lines + ['']


def _criteria_lines() -> list[str]:
    return [
        '## Pass criteria', '',
        'Every applicable cell needs all of the following on its run:', '',
        '- Selected fighter, costume, model, controls, portrait and nameplate are correct before and after '
        'the event.',
        '- No freeze, buzzing audio, T-pose or results softlock.',
        '- The form is still the form after KO, respawn, timeout or results.',
        '- CPU cells: the form plays as CPU at least once and as a player once.',
        '- Team results where the mode allows.',
        '- The cell procedure fixes the rule presets (stock, timer, sudden death) so the event occurs.',
        '',
    ]


def _runs_lines(data: dict[str, object]) -> list[str]:
    lines = ['## Run register', '',
             '| Run | Commit | Pack SHA-256 | Plugin SHA-256 | Language | Runtime | Date | Tester | Evidence |',
             '| --- | --- | --- | --- | --- | --- | --- | --- | --- |']
    for run in cast(list[dict[str, object]], data['runs']):
        runtime = cast(dict[str, str], run['runtime'])
        plugin = run['plugin_sha256'] if run['plugin_sha256'] is not None else 'none'
        lines.append('| {} |'.format(' | '.join(_cell_text(str(value)) for value in (
            run['id'], run['commit'], run['pack_sha256'], plugin, run['language'],
            runtime['kind'] + ' ' + runtime['version'], run['date'], run['tester'], run['evidence']))))
    if not data['runs']:
        lines.append('')
        lines.append('No runs recorded.')
    return lines + ['']


def _summary_lines(data: dict[str, object], statuses: dict[str, str]) -> list[str]:
    counts = {status: 0 for status in ('UNTESTED', 'PASS', 'FAIL', 'N/A')}
    for status in statuses.values():
        counts[status] += 1
    lines = ['## Summary', '', '| Status | Cells |', '| --- | --- |']
    for status, count in counts.items():
        lines.append('| {} | {} |'.format(status, count))
    lines.append('| Total | {} |'.format(len(statuses)))
    lines += ['', 'PASS results per build (commit and candidate SHA-256). A PASS on another build is not '
              'evidence for the current one.', '']
    runs = cast(list[dict[str, str]], data['runs'])
    results = cast(list[dict[str, str]], data['results'])
    if not runs:
        return lines + ['No runs recorded.', '']
    builds = sorted({(run['commit'], run['pack_sha256']) for run in runs})
    lines += ['| Commit | Pack SHA-256 | PASS results |', '| --- | --- | --- |']
    for commit, pack in builds:
        run_ids = {run['id'] for run in runs if run['commit'] == commit and run['pack_sha256'] == pack}
        passes = sum(1 for result in results if result['status'] == 'PASS' and result['run'] in run_ids)
        lines.append('| {} | {} | {} |'.format(commit, pack, passes))
    return lines + ['']


def _matrix_lines(data: dict[str, object], statuses: dict[str, str]) -> list[str]:
    na_numbers = {(entry['mode'], entry['lifecycle']): number for number, entry in
                  enumerate(cast(list[dict[str, str]], data['not_applicable']), start=1)}
    results = {result['cell']: result for result in cast(list[dict[str, str]], data['results'])}
    headers = [LANGUAGE_LABELS[lang] for lang in LANGUAGES]
    lines = ['## Matrix', '']
    for subject, label in SUBJECTS.items():
        for plugin in PLUGINS:
            lines += ['### {} {}, plugin {}'.format(subject, label, plugin), '',
                      '| Mode | Lifecycle | ' + ' | '.join(headers) + ' |',
                      '| --- | --- | --- | --- | --- |']
            for mode in MODES:
                for lifecycle in LIFECYCLES:
                    labels = [_cell_text(_cell_label(cell_index()[
                        '.'.join([subject, mode, lifecycle, lang, plugin])], statuses, results, na_numbers))
                        for lang in LANGUAGES]
                    lines.append('| {} | {} | {} |'.format(mode, lifecycle, ' | '.join(labels)))
            lines.append('')
    return lines


def render_markdown(data: dict[str, object]) -> str:
    statuses = status_map(data)
    lines = (_header_lines() + _status_lines() + _dimension_lines() + _controls_lines()
             + _na_lines(data) + _criteria_lines() + _runs_lines(data) + _summary_lines(data, statuses)
             + _matrix_lines(data, statuses))
    return '\n'.join(lines).rstrip('\n') + '\n'


def check_doc(data: dict[str, object], doc_path: Path = DOC_PATH) -> None:
    try:
        with doc_path.open(encoding='utf-8') as handle:
            current = handle.read()
    except OSError as exc:
        raise ValueError('doc: missing or unreadable; run with --write') from exc
    if current != render_markdown(data):
        raise ValueError('doc: out of date; run tools/check_regression_matrix.py --write')


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true', help='regenerate docs/REGRESSION-MATRIX.md')
    args = parser.parse_args(argv)
    try:
        data = load_matrix()
        validate_matrix(data)
        if args.write:
            DOC_PATH.write_bytes(render_markdown(data).encode('ascii'))
        else:
            check_doc(data)
    except ValueError as exc:
        print('invalid: ' + str(exc), file=sys.stderr)
        return 1
    except OSError:
        print('error: cannot read the matrix data or write the document', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
