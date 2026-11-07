"""A damaged resource file must raise ValueError, never a raw struct or index error."""
import struct
import sys
import unittest
import zlib
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from smash4 import Resource


class CorruptResourceTests(unittest.TestCase):
    def make(self, strings_offset, count):
        header = bytearray(128)
        header[:2] = b'RF'
        struct.pack_into('<I', header, 12, 0xFFFFFF00)  # entry table offset far outside the data
        struct.pack_into('<I', header, 28, 16)
        struct.pack_into('<I', header, 32, strings_offset)
        struct.pack_into('<I', header, 40, count)
        return bytes(header) + zlib.compress(bytes(16))

    def test_offsets_outside_data_raise_value_error(self):
        with self.assertRaises(ValueError):
            Resource(self.make(0, 5))

    def test_truncated_or_garbage_body_raises_value_error(self):
        for data in (b'RF'+bytes(126), b'RF'+bytes(126)+b'x', b'RF'+bytes(126)+bytes(60)):
            with self.subTest(length=len(data)):
                with self.assertRaises(ValueError):
                    Resource(data)

    def test_not_a_resource_still_rejected(self):
        with self.assertRaises(ValueError):
            Resource(b'XX' + bytes(200))


if __name__ == '__main__':
    unittest.main()
