"""
fix9.py — in-page camera can now record video, not only take photos.

Run from the project root (where manage.py lives):

    python fix9.py

The script edits four files and prints what it changed. It is safe to run
twice: already-applied edits are reported as "allaqachon bor" and skipped.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent

EDITS = []


def edit(path, mark, old, new):
    """mark — faqat o'zgarish kiritilgandan keyin paydo bo'ladigan matn."""
    EDITS.append((path, mark, old, new))


# ----------------------------------------------------------------- i18n (uz)
edit(
    "invitation/i18n.py",
    '"rec_start": "Video olish"',
    '''        "shoot": "Rasmga olish",
        "close": "Yopish",''',
    '''        "shoot": "Rasmga olish",
        "rec_start": "Video olish",
        "rec_stop": "To'xtatish",
        "close": "Yopish",''',
)

# ----------------------------------------------------------------- i18n (en)
edit(
    "invitation/i18n.py",
    '"rec_start": "Record video"',
    '''        "shoot": "Capture",
        "close": "Close",''',
    '''        "shoot": "Capture",
        "rec_start": "Record video",
        "rec_stop": "Stop",
        "close": "Close",''',
)

# ------------------------------------------------------------- camera modal
edit(
    "invitation/templates/site/index.html",
    'cam__rec',
    '''        <p class="cam__error" x-show="camError" x-text="camError"></p>
        <div class="cam__bar">
          <button type="button" class="btn btn--ghost" @click="closeCamera()">{{ L.close }}</button>
          <button type="button" class="btn" @click="shoot()" x-show="!camError">{{ L.shoot }}</button>
        </div>''',
    '''        <p class="cam__error" x-show="camError" x-text="camError"></p>
        <p class="cam__rec" x-show="recording" x-cloak><i></i><span x-text="recClock"></span></p>
        <div class="cam__bar">
          <button type="button" class="btn btn--ghost" @click="closeCamera()">{{ L.close }}</button>
          <button type="button" class="btn" @click="shoot()" x-show="!camError && !recording">{{ L.shoot }}</button>
          <button type="button" class="btn btn--ghost" @click="startRec()" x-show="!camError && !recording">{{ L.rec_start }}</button>
          <button type="button" class="btn" @click="stopRec()" x-show="recording" x-cloak>{{ L.rec_stop }}</button>
        </div>''',
)

# ----------------------------------------------------------------------- css
edit(
    "static/css/main.css",
    'camblink',
    '''.cam__bar {
  display: flex;
  gap: 0.7rem;
  justify-content: center;
}''',
    '''.cam__rec {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  margin: 0;
  color: #fff;
  font-variant-numeric: tabular-nums;
  letter-spacing: 0.08em;
}

.cam__rec i {
  width: 0.62rem;
  height: 0.62rem;
  border-radius: 50%;
  background: #fff;
  animation: camblink 1.2s steps(1, end) infinite;
}

@keyframes camblink {
  50% {
    opacity: 0;
  }
}

.cam__bar {
  display: flex;
  gap: 0.7rem;
  justify-content: center;
  flex-wrap: wrap;
}''',
)

# ------------------------------------------------------------------- app.js
edit(
    "static/js/app.js",
    'REC_MAX_SEC',
    '''function uploader() {
  return {''',
    '''// Kamerada yozib olinadigan videoning eng uzun davomiyligi (sekund).
const REC_MAX_SEC = 180;

// Kamerada olingan fayl nomi uchun vaqt tamg'asi.
function camStamp() {
  return new Date().toISOString().slice(0, 19).replace(/[:T]/g, "-");
}

function uploader() {
  return {''',
)

edit(
    "static/js/app.js",
    'micStream: null,',
    '''    camOpen: false,
    camError: "",
    stream: null,
''',
    '''    camOpen: false,
    camError: "",
    stream: null,

    // Video yozish
    recording: false,
    recSec: 0,
    recorder: null,
    recChunks: [],
    recBytes: 0,
    recTimer: null,
    micStream: null,
''',
)

edit(
    "static/js/app.js",
    'this.stopRecTimer();',
    '''    closeCamera() {
      if (this.stream) {''',
    '''    closeCamera() {
      // Yozuv ketayotgan bo'lsa — faylni saqlamasdan to'xtatamiz.
      this.stopRecTimer();
      if (this.recorder && this.recorder.state !== "inactive") {
        this.recorder.onstop = null;
        try {
          this.recorder.stop();
        } catch (e) {}
      }
      this.recorder = null;
      this.recChunks = [];
      this.recording = false;
      if (this.micStream) {
        this.micStream.getTracks().forEach((t) => t.stop());
        this.micStream = null;
      }
      if (this.stream) {''',
)

edit(
    "static/js/app.js",
    'async startRec()',
    '''    shoot() {
      const video = this.$refs.cam;''',
    '''    /*
     * Video yozish. Mikrofonga ruxsat faqat shu yerda so'raladi —
     * rasmga oladigan mehmonga mikrofon so'rovi chiqmaydi.
     * Ruxsat berilmasa video ovozsiz yoziladi.
     */
    async startRec() {
      if (!window.MediaRecorder || !this.stream) {
        this.camError = "Bu brauzer video yozishni qo'llab-quvvatlamaydi.";
        return;
      }
      let tracks = this.stream.getVideoTracks();
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
      }

      this.recChunks = [];
      this.recBytes = 0;
      this.recSec = 0;
      const limit = (CFG.maxUploadMb || 512) * 1024 * 1024;

      this.recorder.ondataavailable = (ev) => {
        if (!ev.data || !ev.data.size) return;
        this.recChunks.push(ev.data);
        this.recBytes += ev.data.size;
        // Hajm chegarasiga yetsa — o'zi to'xtaydi, yozilgani saqlanadi.
        if (this.recBytes > limit * 0.95) this.stopRec();
      };
      this.recorder.onstop = () => this.saveRec();

      this.recorder.start(1000);
      this.recording = true;
      this.recTimer = setInterval(() => {
        this.recSec += 1;
        if (this.recSec >= REC_MAX_SEC) this.stopRec();
      }, 1000);
    },

    stopRec() {
      this.stopRecTimer();
      if (this.recorder && this.recorder.state !== "inactive") {
        try {
          this.recorder.stop();
        } catch (e) {}
      }
      this.recording = false;
    },

    stopRecTimer() {
      if (this.recTimer) {
        clearInterval(this.recTimer);
        this.recTimer = null;
      }
    },

    saveRec() {
      const chunks = this.recChunks;
      this.recChunks = [];
      if (!chunks.length) {
        this.closeCamera();
        return;
      }
      const type = (this.recorder && this.recorder.mimeType) || "video/webm";
      const ext = type.indexOf("mp4") !== -1 ? "mp4" : "webm";
      const blob = new Blob(chunks, { type: type });
      const file = new File([blob], `kamera-${camStamp()}.${ext}`, {
        type: type.split(";")[0],
      });
      this.addFiles([file]);
      this.closeCamera();
    },

    get recClock() {
      const m = Math.floor(this.recSec / 60);
      const s = this.recSec % 60;
      return m + ":" + (s < 10 ? "0" + s : s);
    },

    shoot() {
      const video = this.$refs.cam;''',
)

edit(
    "static/js/app.js",
    'camStamp()}.jpg',
    '''          if (!blob) return;
          const stamp = new Date()
            .toISOString()
            .slice(0, 19)
            .replace(/[:T]/g, "-");
          const file = new File([blob], `kamera-${stamp}.jpg`, {''',
    '''          if (!blob) return;
          const file = new File([blob], `kamera-${camStamp()}.jpg`, {''',
)


def main():
    if not (ROOT / "manage.py").exists():
        sys.exit("XATO: fix9.py ni loyiha papkasiga (manage.py yonida) qo'ying.")

    cache = {}
    done = skipped = 0

    # 1-bosqich: hammasini tekshiramiz, keyin yozamiz.
    for rel, mark, old, new in EDITS:
        p = ROOT / rel
        if not p.exists():
            sys.exit(f"XATO: {rel} topilmadi.")
        text = cache.get(rel) or p.read_text(encoding="utf-8")
        if mark in text:
            print(f"  o'tkazildi (allaqachon bor): {rel} — {mark}")
            skipped += 1
        elif old in text:
            if text.count(old) != 1:
                sys.exit(f"XATO: {rel} ichida mos joy {text.count(old)} marta uchradi.")
            text = text.replace(old, new, 1)
            done += 1
        else:
            sys.exit(f"XATO: {rel} ichida mos joy topilmadi. Fayl o'zgartirilgan.")
        cache[rel] = text

    for rel, text in cache.items():
        (ROOT / rel).write_text(text, encoding="utf-8")
        print(f"  yozildi: {rel}")

    print(f"\nTayyor. {done} ta o'zgarish qilindi, {skipped} tasi allaqachon bor edi.")
    print("Keyingi qadam: python manage.py check")


if __name__ == "__main__":
    main()
