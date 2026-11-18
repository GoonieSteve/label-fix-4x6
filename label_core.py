"""Vector-preserving 4x6 converter for common carrier shipping label PDFs.

Supports portrait and landscape Letter/A4 carriers and already-4x6 labels.
Safety: unknown/non-label documents are rejected instead of automatically printed.
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path
import re
import fitz

LABEL_W, LABEL_H = 288.0, 432.0
PAD_X, PAD_Y = 9.5, 13.0


class UnrecognizedLabel(ValueError):
    """PDF page cannot be confidently classified as a shipping label."""


@dataclass(frozen=True)
class ConversionResult:
    source: Path
    output: Path
    pages: int
    source_type: str


def label_signals(text: str) -> int:
    t = re.sub(r'\s+', ' ', text).lower()
    categories = (
        ('usps', 'us postal'),
        ('tracking #', 'tracking number', 'tracking no', 'track your parcel'),
        ('ground advantage', 'priority mail', 'first-class package'),
        ('pitney bowes',),
        ('postage paid', 'us postage', 'paid imi'),
        ('ship to', 'deliver to', 'recipient'),
        ('shipping label', 'shipping address'),
        ('fedex', 'fed ex'),
        ('ups ground', 'ups next day', 'ups standard'),
        ('vinted',),
        ('evri', 'inpost', 'royal mail', 'parcel shop', 'mondial relay',
         'chronopost', 'colissimo', 'hermes parcel', 'yodel'),
        ('return service', 'returns label'),
    )
    return sum(any(key in t for key in group) for group in categories)


def looks_like_shipping_label(text: str) -> bool:
    return label_signals(text) >= 1


def _matches_size(page: fitz.Page, w: float, h: float, tol=3.0) -> bool:
    a, b = page.rect.width, page.rect.height
    return abs(a-w) < tol and abs(b-h) < tol


def _is_small_label(page: fitz.Page) -> bool:
    return _matches_size(page, 288, 432) or _matches_size(page, 432, 288)


def _is_sheet(page: fitz.Page) -> bool:
    w, h = page.rect.width, page.rect.height
    # Letter (612x792) and A4 (595x842), including landscape, plus common
    # slightly non-standard virtual-printer dimensions.
    wlo, whi = sorted((w, h))
    return (570 <= wlo <= 645 and 750 <= whi <= 870) or (420 <= wlo <= 670 and 680 <= whi <= 950)


def _label_ratio(r: fitz.Rect) -> bool:
    w, h = r.width, r.height
    if w <= 0 or h <= 0:
        return False
    return ((210 <= w <= 385 and 300 <= h <= 550 and .53 <= w/h <= .82)
            or (300 <= w <= 550 and 210 <= h <= 385 and 1.22 <= w/h <= 1.89))


def _outer_border_candidates(page: fitz.Page) -> list[fitz.Rect]:
    candidates = []
    for drawing in page.get_drawings():
        for item in drawing['items']:
            if item[0] != 're':
                continue
            r = fitz.Rect(item[1]) & page.rect
            if not _label_ratio(r):
                continue
            if r.x0 < -1 or r.y0 < -1 or r.x1 > page.rect.width + 1 or r.y1 > page.rect.height + 1:
                continue
            if r.get_area() >= page.rect.get_area() * .87:
                continue
            candidates.append(r)
    return candidates


def _barcode_like_image(page: fitz.Page, region: fitz.Rect | None = None) -> bool:
    try:
        for image in page.get_image_info():
            box = fitz.Rect(image['bbox'])
            if region and (not box.intersects(region) or (box & region).get_area() < box.get_area()*.5):
                continue
            ratio = box.width / max(box.height, .01)
            if (ratio >= 2.6 and box.width >= 70) or (ratio <= .385 and box.height >= 70):
                return True
    except Exception:
        pass
    return False


def _mono_label_image(page: fitz.Page) -> fitz.Rect | None:
    """Image-only PDFs: accept one bounded monochrome 4x6-shaped bitmap."""
    if page.get_text('text').strip():
        return None
    candidates = []
    for img in page.get_image_info():
        r = fitz.Rect(img['bbox'])
        cs = img.get('cs-name', '').lower()
        if (_label_ratio(r) and r.get_area() >= 70000
                and (img.get('bpc', 8) == 1 or 'gray' in cs)):
            candidates.append(r)
    if len(candidates) == 1:
        return fitz.Rect(candidates[0]) & page.rect
    return None


def _content_bounds(page: fitz.Page) -> fitz.Rect | None:
    """Content-based crop when a label has no explicit 4x6 outer border."""
    text = page.get_text('text')
    # A page mentioning a carrier once may be a receipt or an invoice.
    # Demand at least two distinct label indicators, or one plus a barcode.
    if label_signals(text) < 2 and not (looks_like_shipping_label(text) and _barcode_like_image(page)):
        return _mono_label_image(page)
    boxes = []
    for kind, coords, *rest in page.get_bboxlog():
        if kind not in ('fill-text', 'stroke-text', 'fill-image', 'stroke-path', 'fill-path'):
            continue
        r = fitz.Rect(coords)
        if r.is_empty or r.width < .05 or r.height < .05:
            continue
        # Ignore pure page backgrounds, not the actual barcodes/text.
        if r.width > page.rect.width*.92 and r.height > page.rect.height*.90:
            continue
        boxes.append(r)
    if not boxes:
        return None
    union = boxes[0]
    for r in boxes[1:]:
        union |= r
    if (_label_ratio(union) or
        (200 <= union.width <= 560 and 200 <= union.height <= 550
         and .48 <= union.width / union.height <= 2.02)):
        if union.get_area() < page.rect.get_area() * .70:
            return (fitz.Rect(union.x0-6, union.y0-6, union.x1+6, union.y1+6) & page.rect)
    # Full-sheet layout: only support if multiple shipping tokens AND an
    # identifiable long barcode. Prevent accidental auto-print of invoices.
    if label_signals(page.get_text('text')) >= 2 and _barcode_like_image(page):
        return fitz.Rect(0, 0, page.rect.width, page.rect.height)
    return None


def identify_clip(page: fitz.Page) -> tuple[fitz.Rect, str]:
    """Return clipping rectangle and classification for a supported label."""
    if _is_small_label(page):
        text = page.get_text('text')
        if label_signals(text) >= 2 or _barcode_like_image(page) or _mono_label_image(page):
            return page.rect, 'already label-sized'
        raise UnrecognizedLabel('4x6 document does not appear to be a shipping label')
    if not _is_sheet(page):
        raise UnrecognizedLabel(
            f'Unsupported sheet {page.rect.width/72:.2f} x {page.rect.height/72:.2f} inches')
    borders = _outer_border_candidates(page)
    text = page.get_text('text')
    recognized = label_signals(text) >= 2 or (looks_like_shipping_label(text) and _barcode_like_image(page))
    if not recognized:
        # Some image-only shipping labels have a monochrome image fitted to
        # their border. Avoid treating ordinary drawing rectangles as labels.
        # Require a single big grayscale label image, not a random chart.
        image_box = _mono_label_image(page)
        borders = [r for r in borders if image_box and
                   (image_box & r).get_area() >= r.get_area()*.60]
    if borders:
        top = max(borders, key=lambda r: r.get_area())
        # Reject two distinct labels on one sheet instead of silently cropping one.
        for other in borders:
            if other == top or other.get_area() < top.get_area()*.72:
                continue
            if not top.contains(other) and not other.contains(top):
                raise UnrecognizedLabel('Multiple large label regions found on this page')
        clip = fitz.Rect(top.x0-1.2, top.y0-1.2, top.x1+1.2, top.y1+1.2) & page.rect
        return clip, 'embedded label border (portrait/landscape)'
    box = _content_bounds(page)
    if box:
        return box, 'shipping-label content (portrait/landscape)'
    raise UnrecognizedLabel('No recognizable label region found on this sheet')


def _dominant_text_direction(page: fitz.Page, clip: fitz.Rect) -> tuple[float,float] | None:
    """Choose orientation based on real text baselines, not the sheet's shape."""
    angles = []
    try:
        for block in page.get_text('dict', clip=clip)['blocks']:
            for line in block.get('lines', []):
                if not line.get('spans'):
                    continue
                weight = sum(len(span.get('text', '')) for span in line['spans'])
                if weight < 3:
                    continue
                angles.append((weight, line['dir']))
    except Exception:
        return None
    if not angles:
        return None
    # Largest accumulated text orientation by character count.
    from collections import defaultdict
    buckets = defaultdict(int)
    for weight, direction in angles:
        dx, dy = direction
        axis = 'right' if dx>.70 else ('left' if dx<-.70 else ('down' if dy>.70 else 'up'))
        buckets[axis] += weight
    best = max(buckets, key=buckets.get)
    return {'right': (1,0), 'left': (-1,0), 'down': (0,1), 'up': (0,-1)}[best]


def _turn_to_upright(page: fitz.Page, clip: fitz.Rect) -> int:
    dir = _dominant_text_direction(page, clip)
    if dir == (0,1):
        return 90
    if dir == (0,-1):
        return -90
    if dir == (-1,0):
        return 180
    if dir is None and clip.width > clip.height:
        return 90
    return 0


def convert_document(source: Path, destination: Path) -> ConversionResult:
    source = Path(source).resolve()
    destination = Path(destination).resolve()
    if source == destination:
        raise ValueError('Output must differ from original PDF')
    if not source.is_file() or source.suffix.lower() != '.pdf':
        raise ValueError('Please select a PDF file')
    if source.stat().st_size > 70 * 1024 * 1024:
        raise ValueError('PDF exceeds 70 MB safety limit')
    with fitz.open(source) as original:
        if original.needs_pass:
            raise UnrecognizedLabel('PDF is password protected')
        if not (1 <= len(original) <= 20):
            raise UnrecognizedLabel('Expected a PDF containing 1 to 20 pages')
        # Important: /Rotate can make a portrait PDF appear landscape even when
        # all actual PDF drawing coordinates are portrait. Normalize rotations
        # in memory before bounding boxes; never modify the source on disk.
        for page in original:
            if page.rotation:
                page.set_rotation(0)
        per_page = [identify_clip(page) for page in original]
        out = fitz.open()
        types=[]
        for i, (clip, label_type) in enumerate(per_page):
            page = original[i]
            types.append(label_type)
            turn = _turn_to_upright(page, clip)
            if (label_type == 'already label-sized' and
                abs(page.rect.width-LABEL_W) < 3 and
                abs(page.rect.height-LABEL_H) < 3 and turn == 0):
                out.insert_pdf(original, from_page=i, to_page=i)
            else:
                target = out.new_page(width=LABEL_W, height=LABEL_H)
                usable = fitz.Rect(PAD_X, PAD_Y, LABEL_W-PAD_X, LABEL_H-PAD_Y)
                target.show_pdf_page(usable, original, i, clip=clip,
                                     keep_proportion=True, rotate=turn)
        out.set_metadata({'title':'4x6 shipping label',
                          'subject':'LabelFix 4x6 - thermal label print-ready'})
        destination.parent.mkdir(parents=True, exist_ok=True)
        tmp = destination.with_name(destination.stem+'.partial.pdf')
        try:
            out.save(tmp, garbage=4, deflate=True)
            tmp.replace(destination)
        finally:
            out.close()
            tmp.unlink(missing_ok=True)
        return ConversionResult(source, destination, len(per_page), ', '.join(sorted(set(types))))


def safe_output_name(source: Path, output_folder: Path) -> Path:
    stem = re.sub(r'[^\w .()\-]+', '_', source.stem, flags=re.UNICODE).strip(' .') or 'label'
    name = output_folder / f'{stem}_4x6.pdf'
    if not name.exists():
        return name
    digest = hashlib.sha256(source.read_bytes()).hexdigest()[:10]
    return output_folder / f'{stem}_4x6_{digest}.pdf'
