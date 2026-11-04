"""Synthetic corruption checks for the official-export validator."""
import struct
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from verify_official_candidate import patch_paths, decode
from smash4 import Entry, owns_pack


def patchlist(names):
    header=bytearray(128)
    header[:4]=b'\x01\x00PL'
    struct.pack_into('<I',header,4,len(names))
    return bytes(header)+b''.join(n.encode('ascii').ljust(128,b'\0') for n in names)


class OfficialValidationTests(unittest.TestCase):
    def test_shared_ui_folder_is_not_a_language_pack(self):
        folder=Entry(0,0,'ui/replace/chr/chr_10/',0,3846460,8048532,0x1604)
        self.assertFalse(owns_pack('data(us_en)',folder))
        self.assertTrue(owns_pack('data',folder))

    def test_native_localized_folder_can_be_rebuilt(self):
        folder=Entry(0,0,'ui/replace/chr/chrn_11/',0,123,456,0x1e04)
        self.assertTrue(owns_pack('data(us_en)',folder))

    def test_child_flags_cannot_establish_pack_ownership(self):
        child=Entry(0,0,'ui/replace/chr/chr_10/chr_10_Koopa_01.nut',0,10,20,0x805)
        with self.assertRaisesRegex(ValueError,'packed folder'):
            owns_pack('data(us_en)',child)

    def test_valid_patchlist(self):
        self.assertEqual(patch_paths(patchlist(['data/param/ui/packed'])),{'data/param/ui/packed'})

    def test_truncated_patchlist_rejected(self):
        with self.assertRaisesRegex(ValueError,'count/length'):
            patch_paths(patchlist(['data/param/ui/packed'])[:-1])

    def test_case_collision_rejected(self):
        with self.assertRaisesRegex(ValueError,'Duplicate'):
            patch_paths(patchlist(['data/Koopag.nut','data/KoopaG.nut']))

    def test_invalid_paths_rejected(self):
        for name in ('../outside','/absolute','data//packed','data/./packed','C:/file','data\\packed'):
            with self.subTest(name=name),self.assertRaisesRegex(ValueError,'Invalid patchlist path'):
                patch_paths(patchlist([name]))

    def test_member_size_mismatch_rejected(self):
        with self.assertRaisesRegex(ValueError,'length mismatch'):
            decode(b'123',4)

    def test_texture_id_reads_single_texture_header(self):
        from prepare_native_candidate import texture_id
        self.assertEqual(texture_id(nut_header()),(24,0x28fe0005))

    def test_texture_id_rejects_malformed_headers(self):
        from prepare_native_candidate import texture_id
        cases={
            'magic':nut_header(magic=b'NUTX'),
            'texture count':nut_header(count=2),
            'gidx length':nut_header(gidx_len=12),
            'truncated gidx':nut_header()[:20],
            'tiny':b'NTWU',
        }
        for name,raw in cases.items():
            with self.subTest(name=name),self.assertRaises(ValueError):
                texture_id(raw)

    def test_native_head_rejects_span_past_packed_file(self):
        from prepare_native_candidate import native_head
        with self.assertRaisesRegex(ValueError,'span'):
            native_head(bytes(100),90,20)

    def test_allocate_texture_id_skips_occupied_and_rejects_overflow(self):
        from prepare_native_candidate import allocate_texture_id
        self.assertEqual(allocate_texture_id(5,{5,6}),7)
        self.assertEqual(allocate_texture_id(0xfffffffe,set()),0xfffffffe)
        with self.assertRaisesRegex(ValueError,'exhausted'):
            allocate_texture_id(0xffffffff,{0xffffffff})


def nut_header(count=1,gidx_len=16,identifier=0x28fe0005,magic=b'NTWU',size=64):
    raw=bytearray(size)
    raw[:4]=magic
    struct.pack_into('>H',raw,6,count)
    raw[16:20]=b'GIDX'
    struct.pack_into('>II',raw,20,gidx_len,identifier)
    return bytes(raw)


if __name__=='__main__':unittest.main()
