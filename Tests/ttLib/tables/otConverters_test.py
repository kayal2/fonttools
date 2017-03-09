from __future__ import print_function, division, absolute_import
from fontTools.misc.py23 import *
from fontTools.misc.loggingTools import CapturingLogHandler
from fontTools.misc.testTools import FakeFont, makeXMLWriter
from fontTools.misc.textTools import deHexStr
import fontTools.ttLib.tables.otConverters as otConverters
from fontTools.ttLib import newTable
from fontTools.ttLib.tables.otBase import OTTableReader, OTTableWriter
import unittest


class GlyphIDTest(unittest.TestCase):
    font = FakeFont(".notdef A B C".split())
    converter = otConverters.GlyphID('GlyphID', 0, None, None)

    def test_readArray(self):
        reader = OTTableReader(deHexStr("0002 0001 DEAD 0002"))
        self.assertEqual(self.converter.readArray(reader, self.font, {}, 4),
                         ["B", "A", "glyph57005", "B"])
        self.assertEqual(reader.pos, 8)

    def test_read(self):
        reader = OTTableReader(deHexStr("0003"))
        self.assertEqual(self.converter.read(reader, self.font, {}), "C")
        self.assertEqual(reader.pos, 2)

    def test_write(self):
        writer = OTTableWriter()
        self.converter.write(writer, self.font, {}, "B")
        self.assertEqual(writer.getData(), deHexStr("0002"))


class LongTest(unittest.TestCase):
    font = FakeFont([])
    converter = otConverters.Long('Long', 0, None, None)

    def test_read(self):
        reader = OTTableReader(deHexStr("FF0000EE"))
        self.assertEqual(self.converter.read(reader, self.font, {}), -16776978)
        self.assertEqual(reader.pos, 4)

    def test_write(self):
        writer = OTTableWriter()
        self.converter.write(writer, self.font, {}, -16777213)
        self.assertEqual(writer.getData(), deHexStr("FF000003"))

    def test_xmlRead(self):
        value = self.converter.xmlRead({"value": "314159"}, [], self.font)
        self.assertEqual(value, 314159)

    def test_xmlWrite(self):
        writer = makeXMLWriter()
        self.converter.xmlWrite(writer, self.font, 291, "Foo", [("attr", "v")])
        xml = writer.file.getvalue().decode("utf-8").rstrip()
        self.assertEqual(xml, '<Foo attr="v" value="291"/>')


class NameIDTest(unittest.TestCase):
    converter = otConverters.NameID('NameID', 0, None, None)

    def makeFont(self):
        nameTable = newTable('name')
        nameTable.setName(u"Demibold Condensed", 0x123, 3, 0, 0x409)
        return {"name": nameTable}

    def test_read(self):
        font = self.makeFont()
        reader = OTTableReader(deHexStr("0123"))
        self.assertEqual(self.converter.read(reader, font, {}), 0x123)

    def test_write(self):
        writer = OTTableWriter()
        self.converter.write(writer, self.makeFont(), {}, 0x123)
        self.assertEqual(writer.getData(), deHexStr("0123"))

    def test_xmlWrite(self):
        writer = makeXMLWriter()
        self.converter.xmlWrite(writer, self.makeFont(), 291,
                                "FooNameID", [("attr", "val")])
        xml = writer.file.getvalue().decode("utf-8").rstrip()
        self.assertEqual(
            xml,
            '<FooNameID attr="val" value="291"/>  <!-- Demibold Condensed -->')

    def test_xmlWrite_missingID(self):
        writer = makeXMLWriter()
        with CapturingLogHandler(otConverters.log, "WARNING") as captor:
            self.converter.xmlWrite(writer, self.makeFont(), 666,
                                    "Entity", [("attrib", "val")])
        self.assertIn("name id 666 missing from name table",
                      [r.msg for r in captor.records])
        xml = writer.file.getvalue().decode("utf-8").rstrip()
        self.assertEqual(
            xml,
            '<Entity attrib="val"'
            ' value="666"/>  <!-- missing from name table -->')


class UInt8Test(unittest.TestCase):
    font = FakeFont([])
    converter = otConverters.UInt8("UInt8", 0, None, None)

    def test_read(self):
        reader = OTTableReader(deHexStr("FE"))
        self.assertEqual(self.converter.read(reader, self.font, {}), 254)
        self.assertEqual(reader.pos, 1)

    def test_write(self):
        writer = OTTableWriter()
        self.converter.write(writer, self.font, {}, 253)
        self.assertEqual(writer.getData(), deHexStr("FD"))

    def test_xmlRead(self):
        value = self.converter.xmlRead({"value": "254"}, [], self.font)
        self.assertEqual(value, 254)

    def test_xmlWrite(self):
        writer = makeXMLWriter()
        self.converter.xmlWrite(writer, self.font, 251, "Foo", [("attr", "v")])
        xml = writer.file.getvalue().decode("utf-8").rstrip()
        self.assertEqual(xml, '<Foo attr="v" value="251"/>')


if __name__ == "__main__":
    import sys
    sys.exit(unittest.main())
