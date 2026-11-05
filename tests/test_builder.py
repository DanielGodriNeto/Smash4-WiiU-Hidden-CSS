"""Synthetic fixtures only: no Nintendo binary data is stored in tests."""
import struct
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from smash4 import FORMATS, Params, Resource, Entry, rebuild_resource
from build import edit_database, FIGHTERS


def fixture():
    kinds=[5,1,1,1,5,6,5,6,6]+[1]*7+[5]+[1]*36
    rows=[]
    for i in range(82):
        v=[0]*53
        v[0]=i
        v[6]=0xffffffff
        if 1<=i<=58:
            v[2]=1
            v[13]=i
        for row,cosmetic,fid in [(60,201,0xffffffff),(61,202,0xffffffff),(62,203,0xffffffff),(63,204,0xffffffff),(73,219,62),(74,220,63),(75,221,64)]:
            if i==row:
                v[0],v[6]=cosmetic,fid
        donors={16:15,23:22,39:41,31:30,1:0,2:1,3:2}
        if i in donors:
            v[6]=donors[i]
        rows.append(b''.join(bytes([k])+struct.pack('>'+FORMATS[k],x) for k,x in zip(kinds,v)))
    return b'\xff\xff\0\0'+bytes(4)+b'\x20'+struct.pack('>I',82)+b''.join(rows)


def rf_fixture():
    names=bytearray(4+0x2000)
    struct.pack_into('<I',names,0,1)
    names[21:27]=b'root/\0'
    names[27:33]=b'alpha\0'
    names[33:38]=b'.bin\0'
    names+=struct.pack('<III',2,0,29)
    table=bytearray(24)
    table[4]=16
    table[21]=2
    table+=struct.pack('<6I',0,17,128,256,0,0x1e01)
    table+=struct.pack('<6I',128,0x01000017,4,4,0,0x802)
    size=len(table)
    while len(table)%16 or len(table)<size+32:
        table.append(0xbb)
    import zlib
    header=bytearray(128)
    header[:4]=b'RF\x06\0'
    body=table+names+bytes([0xbb])*96
    struct.pack_into('<10I',header,4,128,0,128,size,0,0,len(body),128+len(table),len(names),3)
    compressed=zlib.compress(body)
    struct.pack_into('<I',header,24,len(compressed))
    return bytes(header)+compressed


class BuilderTests(unittest.TestCase):
    def test_four_forms_preserve_other_rows(self):
        raw=fixture()
        modified,report=edit_database(raw,FIGHTERS[:4])
        p=Params(modified)
        self.assertEqual(len(p.groups[0]),82)
        self.assertEqual([r['id'] for r in report],[58,59,60,61])
        for f in FIGHTERS[:4]:
            v=p.values(p.groups[0][f['row']])
            self.assertEqual((v[0],v[6],v[7],v[9],v[10]),(f['cosmetic'],f['id'],1,0,0))
        original=Params(raw)
        for i in range(82):
            if i not in {60,61,62,63}:
                self.assertEqual(original.values(original.groups[0][i]),p.values(p.groups[0][i]))

    def test_seven_have_unique_ids_and_positions(self):
        modified,report=edit_database(fixture(),FIGHTERS)
        self.assertEqual(len({r['css_position'] for r in report}),7)
        self.assertEqual(len({r['cosmetic'] for r in report}),7)
        p=Params(modified)
        self.assertEqual([p.values(p.groups[0][i])[6] for i in [73,74,75]],[62,63,64])

    def test_modified_database_rejected(self):
        raw=fixture()
        p=Params(raw)
        p.set(p.groups[0][60][6],58)
        with self.assertRaises(ValueError):
            edit_database(bytes(p.data),FIGHTERS)

    def test_wrong_donor_rejected(self):
        p=Params(fixture())
        p.set(p.groups[0][16][6],999)
        with self.assertRaises(ValueError):
            edit_database(bytes(p.data),FIGHTERS)

    def test_duplicate_slot_rejected(self):
        with self.assertRaisesRegex(ValueError,'Duplicate'):
            edit_database(fixture(),[FIGHTERS[0],FIGHTERS[0]])

    def test_duplicate_asset_rejected_nonadjacent(self):
        with self.assertRaisesRegex(ValueError,'Duplicate'):
            edit_database(fixture(),[FIGHTERS[0],FIGHTERS[1],dict(FIGHTERS[2],asset=FIGHTERS[0]['asset'])])

    def test_normal_row_replacement_and_appending_rejected(self):
        for row in (16,82):
            f=dict(FIGHTERS[0],row=row)
            with self.assertRaisesRegex(ValueError,'Unsupported fighter mapping'):
                edit_database(fixture(),[f])

    def test_invalid_cosmetic_rejected(self):
        f=dict(FIGHTERS[1],cosmetic=60)
        with self.assertRaisesRegex(ValueError,'Unsupported fighter mapping'):
            edit_database(fixture(),[f])

    def test_mismatched_row_schema_rejected(self):
        p=Params(fixture())
        p.data[p.groups[0][60][-1][0]]=2
        with self.assertRaisesRegex(ValueError,'typed schema'):
            edit_database(bytes(p.data),FIGHTERS)

    def test_rf_addition_keeps_original_names(self):
        r=Resource(rf_fixture())
        added=Entry(-1,-1,'root/beta.bin',256,10,20,0x802)
        result=Resource(rebuild_resource(r,[added]))
        self.assertEqual([e.path for e in result.entries],['root/','root/alpha.bin','root/beta.bin'])
        self.assertEqual(result.entries[1].offset,128)
        self.assertEqual(result.entries[2].decompressed,20)

    def test_rf_rejects_duplicate_path(self):
        r=Resource(rf_fixture())
        with self.assertRaises(ValueError):
            rebuild_resource(r,[Entry(-1,-1,'root/alpha.bin',0,0,0,0x802)])

    def test_parameter_values_are_big_endian(self):
        p=Params(fixture())
        p.set(p.groups[0][0][0],0x01020304)
        pos=p.groups[0][0][0][0]
        self.assertEqual(p.data[pos+1:pos+5],b'\1\2\3\4')

    def test_dlc_row_overlapping_new_slot_rejected(self):
        p=Params(fixture())
        p.set(p.groups[0][80][10],1)
        p.set(p.groups[0][80][13],59)
        with self.assertRaisesRegex(ValueError,'overlaps'):
            edit_database(bytes(p.data),FIGHTERS)

    def test_dlc_row_outside_new_slots_accepted(self):
        p=Params(fixture())
        p.set(p.groups[0][80][10],1)
        p.set(p.groups[0][80][13],200)
        _,report=edit_database(bytes(p.data),FIGHTERS)
        self.assertEqual([r['css_position'] for r in report],list(range(59,66)))

    def test_replaced_row_old_position_is_not_taken(self):
        p=Params(fixture())
        p.set(p.groups[0][60][13],59)
        _,report=edit_database(bytes(p.data),FIGHTERS)
        self.assertEqual(report[0]['css_position'],59)

    def test_position_beyond_unsigned_byte_field_rejected(self):
        p=Params(fixture())
        p.set(p.groups[0][58][13],255)
        with self.assertRaisesRegex(ValueError,'8-bit'):
            edit_database(bytes(p.data),FIGHTERS)

    def test_slot_position_helper_rejects_taken_and_repeated_values(self):
        from build import check_slot_positions
        check_slot_positions([59,60],{1,2,58})
        with self.assertRaisesRegex(ValueError,'overlaps'):
            check_slot_positions([59,60],{60})
        with self.assertRaisesRegex(ValueError,'Duplicate'):
            check_slot_positions([59,59],set())

    def test_case_collision_helper(self):
        from smash4 import check_case_collisions
        check_case_collisions(['root/alpha.bin'],['root/beta.bin'])
        check_case_collisions(['root/alpha.bin'],['root/alpha.bin'])
        with self.assertRaisesRegex(ValueError,'Case-insensitive'):
            check_case_collisions(['root/alpha.bin'],['root/ALPHA.bin'])
        with self.assertRaisesRegex(ValueError,'Case-insensitive'):
            check_case_collisions([],['root/a.bin','root/A.bin'])

    def test_archive_add_rejects_case_only_aliases(self):
        from build import ArchiveEdits
        edits=ArchiveEdits(FakeDump(Resource(rf_fixture()),bytes(512)),'data',None)
        with self.assertRaisesRegex(ValueError,'Case-insensitive'):
            edits.add('root/ALPHA.bin',b'x')
        edits.add('root/beta.bin',b'b'*20)
        with self.assertRaisesRegex(ValueError,'Case-insensitive'):
            edits.add('root/Beta.bin',b'c')
        edits.add('root/alpha.bin',b'a'*4)

    def test_archive_finish_accepts_valid_spans(self):
        from build import ArchiveEdits
        with tempfile.TemporaryDirectory() as tmp:
            edits=ArchiveEdits(FakeDump(Resource(rf_fixture()),bytes(512)),'data',Path(tmp))
            edits.add('root/beta.bin',b'b'*20)
            _,added=edits.finish()
        self.assertEqual(added,1)

    def test_archive_finish_rejects_span_past_packed_file(self):
        from build import ArchiveEdits
        edits=ArchiveEdits(FakeDump(Resource(rf_fixture()),bytes(512)),'data',None)
        edits.add('root/beta.bin',b'b'*20)
        edits.packs['root/']=edits.packs['root/'][:8]
        with self.assertRaisesRegex(ValueError,'span'):
            edits.finish()

    def test_span_helper_bounds(self):
        from smash4 import check_span
        check_span(100,92,8)
        check_span(100,100,0)
        for offset,length in [(93,8),(-1,4),(0,-1)]:
            with self.subTest(offset=offset,length=length),self.assertRaisesRegex(ValueError,'span'):
                check_span(100,offset,length)


class FakeDump:
    """Synthetic stand-in for Dump: one resource and one packed archive."""
    def __init__(self, resource, pack):
        self.resources={'data':resource}
        self._pack=pack

    def pack(self, partition, parent):
        return self._pack


if __name__=='__main__':
    unittest.main()
