"""Synthetic regression suite: contains no genuine addresses, barcodes, or postage."""
import hashlib
from pathlib import Path
import tempfile
import unittest
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import fitz
from label_core import convert_document, UnrecognizedLabel, safe_output_name


def synthetic_label(path: Path, *, landscape=False, n_pages=1):
    width, height = (792, 612) if landscape else (612, 792)
    pdf = fitz.open()
    for _ in range(n_pages):
        page = pdf.new_page(width=width, height=height)
        left, top = 60, 40
        page.draw_rect(fitz.Rect(left, top, left + 286, top + 429), width=1.2)
        page.insert_text((left + 16, top + 37), 'USPS SHIPPING LABEL - TEST ONLY', fontsize=11)
        page.insert_text((left + 16, top + 67), 'USPS TRACKING # - NOT VALID', fontsize=10)
        page.insert_text((left + 16, top + 97), 'TEST LABEL DO NOT SHIP', fontsize=11)
        page.insert_text((left + 16, top + 350), 'USPS TRACKING # - TEST', fontsize=10)
        for i in range(85):
            x = left + 17 + i * 2.8
            w = 1.7 if i % 3 == 0 else 0.8
            page.draw_rect(fitz.Rect(x, top+366, x+w, top+405), fill=(0,0,0), color=None)
    pdf.save(path)
    pdf.close()


def synthetic_report(path: Path):
    pdf = fitz.open()
    page = pdf.new_page(width=792, height=612)
    page.insert_text((50, 80), 'QUARTERLY FINANCIAL REPORT', fontsize=18)
    page.draw_rect(fitz.Rect(70, 110, 430, 460))
    page.insert_text((75, 170), 'Net income', fontsize=14)
    pdf.save(path)
    pdf.close()


class ConversionRegression(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def test_letter_portrait_to_4x6(self):
        src, dst = self.root/'input.pdf', self.root/'output.pdf'
        synthetic_label(src)
        before = hashlib.sha256(src.read_bytes()).digest()
        result = convert_document(src, dst)
        self.assertEqual(result.pages, 1)
        self.assertEqual(before, hashlib.sha256(src.read_bytes()).digest())
        with fitz.open(dst) as pdf:
            self.assertEqual(len(pdf), 1)
            self.assertEqual((pdf[0].rect.width, pdf[0].rect.height), (288, 432))
            self.assertIn('DO NOT SHIP', pdf[0].get_text())
            self.assertIn('USPS TRACKING', pdf[0].get_text())
            self.assertTrue(pdf[0].get_drawings())

    def test_letter_landscape_to_4x6(self):
        src, dst = self.root/'landscape.pdf', self.root/'portrait_4x6.pdf'
        synthetic_label(src, landscape=True)
        convert_document(src, dst)
        with fitz.open(dst) as pdf:
            self.assertEqual((pdf[0].rect.width, pdf[0].rect.height), (288, 432))
            self.assertIn('DO NOT SHIP', pdf[0].get_text())

    def test_multipage_preserved(self):
        src, dst = self.root/'two.pdf', self.root/'two_4x6.pdf'
        synthetic_label(src, landscape=True, n_pages=2)
        res = convert_document(src, dst)
        self.assertEqual(res.pages, 2)
        with fitz.open(dst) as pdf:
            self.assertEqual(len(pdf), 2)

    def test_non_shipping_report_rejected(self):
        src, dst = self.root/'report.pdf', self.root/'report_out.pdf'
        synthetic_report(src)
        with self.assertRaises(UnrecognizedLabel):
            convert_document(src, dst)
        self.assertFalse(dst.exists())

    def test_original_pdf_not_overwritten(self):
        src = self.root/'sample.pdf'
        synthetic_label(src)
        with self.assertRaises(ValueError):
            convert_document(src, src)

    def test_output_collision_creates_stable_suffix(self):
        src = self.root/'label.pdf'
        synthetic_label(src)
        dest = self.root/'converted'
        dest.mkdir()
        first = safe_output_name(src, dest)
        self.assertEqual(first.name, 'label_4x6.pdf')
        first.write_bytes(b'existing converted label placeholder')
        second = safe_output_name(src, dest)
        self.assertNotEqual(first, second)
        self.assertEqual(second, safe_output_name(src, dest))


if __name__ == '__main__':
    unittest.main()
