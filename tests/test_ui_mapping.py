"""Synthetic fixtures only: no Nintendo binary data is stored in tests."""
import struct
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from smash4 import Entry
from ui_mapping import (check_import_placement, check_manifest_targets, check_new_ids, check_targets,
    native_texture_ids, packed_folder, require_donors)

CHR='ui/replace/chr/'


def portrait(name,category='chr_10'):
    return CHR+category+'/'+category+'_'+name+'_01.nut'


def nut(identifier=0x28fe0005,magic=b'NTWU',count=1,size=64):
    raw=bytearray(size)
    raw[:4]=magic
    struct.pack_into('>H',raw,6,count)
    raw[16:20]=b'GIDX'
    struct.pack_into('>II',raw,20,16,identifier)
    return bytes(raw)


def directory(path,flags):
    return Entry(0,0,path,0,0,0,flags)


class UiMappingTests(unittest.TestCase):
    def test_base_roster_target_rejected(self):
        native={portrait('Question'),portrait('Koopa'),portrait('Koopag')}
        with self.assertRaisesRegex(ValueError,'base-roster'):
            check_targets(native,{portrait('Koopa')},[portrait('Question'),portrait('Koopa')])

    def test_identical_native_overwrite_reported(self):
        native={portrait('Question'),portrait('Koopag')}
        targets=[portrait('Koopag'),portrait('Question')]
        self.assertEqual(check_targets(native,set(),targets),sorted(targets))

    def test_fresh_target_returns_no_overwrites(self):
        self.assertEqual(check_targets({portrait('Question')},set(),[portrait('Miienemyf')]),[])

    def test_duplicate_target_rejected(self):
        with self.assertRaisesRegex(ValueError,'Duplicate target'):
            check_targets(set(),set(),[portrait('Question')]*2)

    def test_case_only_duplicate_rejected(self):
        with self.assertRaisesRegex(ValueError,'Case-insensitive'):
            check_targets(set(),set(),[portrait('Koopag'),portrait('KOOPAG')])

    def test_nonadjacent_duplicate_rejected(self):
        with self.assertRaisesRegex(ValueError,'Duplicate target'):
            check_targets(set(),set(),[portrait('Koopag'),portrait('Question'),portrait('Koopag')])

    def test_native_casefold_collision_rejected(self):
        with self.assertRaisesRegex(ValueError,'Case-insensitive'):
            check_targets({portrait('Koopag')},set(),[portrait('Question'),portrait('KOOPAG')])

    def test_new_id_colliding_native_rejected(self):
        with self.assertRaisesRegex(ValueError,'collides'):
            check_new_ids({0x28fe0000,0x28fe0005},[0x28fe0001,0x28fe0005])

    def test_duplicate_new_id_rejected(self):
        with self.assertRaisesRegex(ValueError,'Duplicate new texture ID'):
            check_new_ids(set(),[0x28fe0000,0x28fe0000])

    def test_distinct_ids_same_low_bits_accepted(self):
        check_new_ids(set(),[0x28fe0000,0x18fe0000])

    def test_native_ids_collects_single_texture_ids(self):
        ids=native_texture_ids([(CHR+'a.nut',nut(0x280015fe)),(CHR+'b.nut',nut(0x28001000))])
        self.assertEqual(ids,{0x280015fe,0x28001000})

    def test_native_ids_reject_non_ntwu(self):
        with self.assertRaisesRegex(ValueError,'not NTWU'):
            native_texture_ids([(CHR+'a.nut',nut(magic=b'NTWX'))])

    def test_native_ids_reject_multi_texture(self):
        with self.assertRaisesRegex(ValueError,'multi-texture'):
            native_texture_ids([(CHR+'a.nut',nut(count=2))])

    def test_packed_folder_nearest_ancestor(self):
        dirs={CHR:directory(CHR,0x1604),CHR+'chr_10/':directory(CHR+'chr_10/',0x1e04)}
        self.assertEqual(packed_folder(dirs,portrait('Koopa')).path,CHR+'chr_10/')

    def test_packed_folder_skips_unpacked_directory(self):
        dirs={CHR:directory(CHR,0x1604),CHR+'chr_10/':directory(CHR+'chr_10/',0x200)}
        self.assertEqual(packed_folder(dirs,portrait('Koopa')).path,CHR)

    def test_packed_folder_missing_rejected(self):
        with self.assertRaisesRegex(ValueError,'No native packed ancestor'):
            packed_folder({},portrait('Koopa'))

    def test_shared_folder_localized_import_rejected(self):
        with self.assertRaisesRegex(ValueError,'Partial language pack'):
            check_import_placement('data(us_en)',directory(CHR+'chr_10/',0x1604))

    def test_localized_import_in_owned_folder_accepted(self):
        check_import_placement('data(us_en)',directory(CHR+'chrn_11/',0x1e04))

    def test_data_import_in_shared_folder_accepted(self):
        check_import_placement('data',directory(CHR+'chr_10/',0x1604))

    def test_donor_missing_rejected(self):
        with self.assertRaisesRegex(ValueError,'No donor'):
            require_donors('Miigunner',[])

    def test_donor_categories_sorted(self):
        donors=[portrait('Koopa',category='chr_13'),portrait('Koopa',category='chr_10')]
        self.assertEqual(require_donors('Koopa',donors),['chr_10','chr_13'])

    def test_manifest_duplicate_target_rejected(self):
        with self.assertRaisesRegex(ValueError,'Duplicate manifest target'):
            check_manifest_targets([('data','a/x.nut'),('data','b/y.nut'),('data','a/x.nut')])

    def test_manifest_same_path_in_other_partition_accepted(self):
        check_manifest_targets([('data','a/x.nut'),('data(us_en)','a/x.nut')])


if __name__=='__main__':unittest.main()
