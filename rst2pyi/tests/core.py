# Copyright 2019 John Reese
# Licensed under the MIT license

from rst2pyi.core import Converter

from unittest import TestCase


class ConverterTest(TestCase):
    def test_split_types(self):
        fn = Converter._split_types
        self.assertEqual(fn("Optional[int]"), {"Optional", "int"})
        self.assertEqual(fn("Union[int, str]"), {"Union", "int", "str"})
        self.assertEqual(
            fn("Optional[Union[int, str]]"), {"Optional", "Union", "int", "str"}
        )

    def test_convert_types(self):
        fn = Converter._convert_type
        self.assertEqual(fn("int or None"), "Optional[int]")
        self.assertEqual(fn("int or str"), "Union[int, str]")
