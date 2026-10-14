"""
fix11.py — gallery drag-reorder was broken: an undefined variable `w`.

In panel/views.py gallery_item() the reorder branch filtered by
`wedding=w`, but `w` does not exist in that function — the photo's own
wedding is on `p`. Fixes it to `wedding=p.wedding`.

Run from the project root (where manage.py lives):

    python fix11.py

Safe to run twice: an already-applied edit is skipped.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent

EDITS = []


def edit(path, mark, old, new):
    """mark — faqat o'zgarish kiritilgandan keyin paydo bo'ladigan matn."""
    EDITS.append((path, mark, old, new))


edit(
    "panel/views.py",
    "GalleryPhoto.objects.filter(pk=pid, wedding=p.wedding)",
    "            GalleryPhoto.objects.filter(pk=pid, wedding=w).update(order=i)",
    "            GalleryPhoto.objects.filter(pk=pid, wedding=p.wedding).update(order=i)",
)


def main():
    if not (ROOT / "manage.py").exists():
        sys.exit("XATO: fix11.py ni loyiha papkasiga (manage.py yonida) qo'ying.")

    cache = {}
    done = skipped = 0

    for rel, mark, old, new in EDITS:
        p = ROOT / rel
        if not p.exists():
            sys.exit(f"XATO: {rel} topilmadi.")
        text = cache.get(rel) or p.read_text(encoding="utf-8")
        if mark in text:
            print(f"  o'tkazildi (allaqachon tuzatilgan): {rel}")
            skipped += 1
        elif old in text:
            if text.count(old) != 1:
                sys.exit(f"XATO: {rel} ichida mos joy {text.count(old)} marta uchradi.")
            text = text.replace(old, new, 1)
            done += 1
        else:
            sys.exit(f"XATO: {rel} ichida mos joy topilmadi.")
        cache[rel] = text

    for rel, text in cache.items():
        if done:
            (ROOT / rel).write_text(text, encoding="utf-8")
            print(f"  yozildi: {rel}")

    print(f"\nTayyor. {done} ta o'zgarish qilindi, {skipped} tasi allaqachon bor edi.")
    print("Keyingi qadam: python manage.py check")


if __name__ == "__main__":
    main()
