"""Pure UI mapping checks shared by the candidate preparer and the official verifier.

Offline checks establish internal consistency only. They do not prove that
names, icons, results art or new texture IDs render correctly in game.
"""
import struct
from smash4 import check_case_collisions, owns_pack

KNOWN_GAPS = (
    'Names and message IDs are not modelled; the ??? root cause is not established.',
    'Nameplates, CSS and stock icons, and results art are not verified offline.',
    'Question and sh_all overwrites change shared data; their impact on other menus is unknown.',
    'Texture-ID global uniqueness and rendering are not established.',
    'The same logical file can carry different texture IDs per partition.',
    'Category policy for donor portraits is unverified.',
    'Database field semantics beyond the edited fields are undocumented.',
    'Respawn and results code are not fixed; no RPX or global native mapping patches applied.',
)


def texture_id(raw):
    if len(raw)<16 or raw[:4]!=b'NTWU' or struct.unpack_from('>H',raw,6)[0]!=1:
        raise ValueError('Expected a single-texture Wii U NUT')
    at=raw.find(b'GIDX',16,256)
    if at<0 or at+12>len(raw) or struct.unpack_from('>I',raw,at+4)[0]!=16:raise ValueError('Unexpected NUT GIDX layout')
    return at+8,struct.unpack_from('>I',raw,at+8)[0]


def allocate_texture_id(candidate,occupied):
    """Return the first free 32-bit texture ID at or after candidate."""
    while candidate in occupied:
        candidate+=1
    if candidate>0xffffffff:raise ValueError('Texture ID space exhausted')
    return candidate


def native_texture_ids(entries):
    """Collect the texture ID of every native NUT; fail closed on anything not single-texture NTWU."""
    ids=set()
    for path,raw in entries:
        if raw[:4]!=b'NTWU':raise ValueError('Unparsed NUT (not NTWU): '+path)
        if raw[6:8]!=b'\0\1':raise ValueError('Cannot certify unique IDs without a multi-texture parser: '+path)
        ids.add(texture_id(raw)[1])
    return ids


def check_targets(native_paths,base_paths,targets):
    """Reject targets that replace a base portrait, repeat, or collide by case with a native path.

    Returns the sorted targets that identically overwrite a native file; these are reported, not fatal.
    """
    for path in targets:
        if path in base_paths:raise ValueError('Target replaces a base-roster portrait: '+path)
    exact=set()
    folded=set()
    for path in targets:
        if path in exact:raise ValueError('Duplicate target: '+path)
        if path.casefold() in folded:raise ValueError('Case-insensitive resource path collision: '+path)
        exact.add(path)
        folded.add(path.casefold())
    for path in targets:
        check_case_collisions(native_paths,[path])
    return sorted(p for p in targets if p in native_paths)


def check_new_ids(native_ids,new_ids):
    seen=set()
    for identifier in new_ids:
        if identifier in native_ids:raise ValueError('Texture ID collides with a native NUT: '+hex(identifier))
        if identifier in seen:raise ValueError('Duplicate new texture ID: '+hex(identifier))
        seen.add(identifier)


def check_manifest_targets(targets):
    """Reject a manifest that names the same partition/path twice; a dict would keep only the last entry."""
    seen=set()
    for key in targets:
        if key in seen:raise ValueError('Duplicate manifest target: '+'/'.join(key))
        seen.add(key)


def packed_folder(directories,path):
    """Return the nearest ancestor directory that is a packed folder (flag 0x400)."""
    parent_path=path.rsplit('/',1)[0]+'/'
    while parent_path not in directories or not directories[parent_path].flags&0x400:
        trimmed=parent_path.rstrip('/')
        if '/' not in trimmed:raise ValueError('No native packed ancestor')
        parent_path=trimmed.rsplit('/',1)[0]+'/'
    return directories[parent_path]


def check_import_placement(partition,folder):
    """Reject a localized import into a shared folder; that would create a partial language pack."""
    if not owns_pack(partition,folder):raise ValueError('Partial language pack for shared folder: '+folder.path)


def require_donors(base,donor_paths):
    """Require at least one donor portrait and return its sorted category folders."""
    if not donor_paths:raise ValueError('No donor portrait for base: '+base)
    return sorted({p.split('/')[-2] for p in donor_paths})
