"""
fix10.py — fixes the Chrome tab crash when starting a video recording.

The camera is now re-opened once with audio instead of mixing two streams
into a new MediaStream, and webm (vp9 + opus) is preferred over mp4.

Run from the project root (where manage.py lives):

    python fix10.py

Safe to run twice: already-applied edits are reported and skipped.
Requires fix9.py to have been applied first.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent

EDITS = []


def edit(path, mark, old, new):
    """mark — faqat o'zgarish kiritilgandan keyin paydo bo'ladigan matn."""
    EDITS.append((path, mark, old, new))


# 1 — kamera talablari bitta joyga chiqarildi
edit(
    "static/js/app.js",
    "const CAM_VIDEO",
    '''const REC_MAX_SEC = 180;

// Kamerada olingan fayl nomi uchun vaqt tamg'asi.''',
    '''const REC_MAX_SEC = 180;

// Kamera talablari — rasm va video uchun bir xil.
const CAM_VIDEO = {
  facingMode: { ideal: "environment" },
  width: { ideal: 2560 },
  height: { ideal: 1440 },
};

// Kamerada olingan fayl nomi uchun vaqt tamg'asi.''',
)

# 2 — alohida mikrofon oqimi endi kerak emas
edit(
    "static/js/app.js",
    "    recTimer: null,\n\n    /*",
    '''    recTimer: null,
    micStream: null,
''',
    '''    recTimer: null,
''',
)

# 3 — openCamera umumiy talablardan foydalanadi
edit(
    "static/js/app.js",
    "video: CAM_VIDEO,\n          audio: false,",
    '''        this.stream = await navigator.mediaDevices.getUserMedia({
          video: {
            facingMode: { ideal: "environment" },
            width: { ideal: 2560 },
            height: { ideal: 1440 },
          },
          audio: false,
        });''',
    '''        this.stream = await navigator.mediaDevices.getUserMedia({
          video: CAM_VIDEO,
          audio: false,
        });''',
)

# 4 — closeCamera'dan mikrofon oqimi olib tashlandi
edit(
    "static/js/app.js",
    "      this.recording = false;\n      if (this.stream) {",
    '''      this.recording = false;
      if (this.micStream) {
        this.micStream.getTracks().forEach((t) => t.stop());
        this.micStream = null;
      }
      if (this.stream) {''',
    '''      this.recording = false;
      if (this.stream) {''',
)

# 5 — izoh
edit(
    "static/js/app.js",
    "MediaStream yasash ba'zi brauzerlarda",
    '''     * Ruxsat berilmasa video ovozsiz yoziladi.
     */''',
    '''     * Oqim ovoz bilan qaytadan olinadi: ikki oqimni qo'shib yangi
     * MediaStream yasash ba'zi brauzerlarda sahifani yiqitadi.
     * Mikrofonga ruxsat berilmasa video ovozsiz yoziladi.
     */''',
)

# 6 — yozishning o'zi: bitta oqim, webm birinchi, zaxira MediaRecorder
edit(
    "static/js/app.js",
    "const withSound = await navigator.mediaDevices.getUserMedia",
    '''      let tracks = this.stream.getVideoTracks();
      try {
        this.micStream = await navigator.mediaDevices.getUserMedia({
          audio: true,
        });
        tracks = tracks.concat(this.micStream.getAudioTracks());
      } catch (e) {
        this.micStream = null;
      }

      const mime =
        [
          "video/mp4",
          "video/webm;codecs=vp9,opus",
          "video/webm;codecs=vp8,opus",
          "video/webm",
        ].find(
          (t) =>
            MediaRecorder.isTypeSupported && MediaRecorder.isTypeSupported(t)
        ) || "";

      try {
        this.recorder = new MediaRecorder(
          new MediaStream(tracks),
          mime ? { mimeType: mime } : undefined
        );
      } catch (e) {
        this.camError = "Video yozishni boshlab bo'lmadi.";
        return;
      }''',
    '''      try {
        const withSound = await navigator.mediaDevices.getUserMedia({
          video: CAM_VIDEO,
          audio: true,
        });
        this.stream.getTracks().forEach((t) => t.stop());
        this.stream = withSound;
        await this.$nextTick();
        const video = this.$refs.cam;
        if (video) {
          video.srcObject = withSound;
          await video.play();
        }
      } catch (e) {
        // Ovozsiz davom etamiz — eski oqim joyida qoladi.
      }

      const mime =
        [
          "video/webm;codecs=vp9,opus",
          "video/webm;codecs=vp8,opus",
          "video/webm",
          "video/mp4",
        ].find(
          (t) =>
            MediaRecorder.isTypeSupported && MediaRecorder.isTypeSupported(t)
        ) || "";

      try {
        this.recorder = new MediaRecorder(
          this.stream,
          mime ? { mimeType: mime } : undefined
        );
      } catch (e) {
        try {
          this.recorder = new MediaRecorder(this.stream);
        } catch (e2) {
          this.camError = "Video yozishni boshlab bo'lmadi.";
          return;
        }
      }''',
)


def main():
    if not (ROOT / "manage.py").exists():
        sys.exit("XATO: fix10.py ni loyiha papkasiga (manage.py yonida) qo'ying.")

    cache = {}
    done = skipped = 0

    for rel, mark, old, new in EDITS:
        p = ROOT / rel
        if not p.exists():
            sys.exit(f"XATO: {rel} topilmadi.")
        text = cache.get(rel) or p.read_text(encoding="utf-8")
        if mark in text:
            print(f"  o'tkazildi (allaqachon bor): {mark[:40]}")
            skipped += 1
        elif old in text:
            if text.count(old) != 1:
                sys.exit(f"XATO: {rel} ichida mos joy {text.count(old)} marta uchradi.")
            text = text.replace(old, new, 1)
            done += 1
        else:
            sys.exit(
                f"XATO: {rel} ichida mos joy topilmadi.\n"
                "Avval fix9.py ishga tushirilganmi? Fayl qo'lda o'zgartirilgan bo'lishi mumkin."
            )
        cache[rel] = text

    for rel, text in cache.items():
        (ROOT / rel).write_text(text, encoding="utf-8")
        print(f"  yozildi: {rel}")

    print(f"\nTayyor. {done} ta o'zgarish qilindi, {skipped} tasi allaqachon bor edi.")
    print("Keyingi qadam: brauzerda Ctrl+Shift+R bilan sahifani yangilang.")


if __name__ == "__main__":
    main()
