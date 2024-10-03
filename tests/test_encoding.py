from unittest import TestCase

from src.common.encoding import bytes_to_encoding, encoding_to_bytes


class TestEncoding(TestCase):
    def test_encoding(self):
        raw = b"asodcxvokw2nigndgsiv80lj213lotrh114514"
        self.assertEqual(
            raw,
            encoding_to_bytes(bytes_to_encoding(raw)),
        )
