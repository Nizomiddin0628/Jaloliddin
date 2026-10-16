/*
 * Taklifnoma sahifasining interaktiv qismlari.
 * Alpine.js komponentlari — hech qanday qurish (build) talab qilinmaydi.
 */

const CFG = window.TAKLIFNOMA || {};

const REDUCED = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

function headers(extra) {
  return Object.assign({ "X-CSRFToken": CFG.csrfToken }, extra || {});
}

function formatSize(bytes) {
  if (bytes < 1024 * 1024) return Math.round(bytes / 1024) + " KB";
  return (bytes / (1024 * 1024)).toFixed(1) + " MB";
}

function firstError(data) {
  const key = Object.keys(data || {})[0];
  if (!key) return null;
  const val = data[key];
  return Array.isArray(val) ? val[0] : String(val);
}

/* ------------------------------------------------- aylantirish animatsiyasi */

/*
 * Bo'limlar ekranga kirganda bir marta paydo bo'ladi.
 * Telefonda «harakatni kamaytirish» yoqilgan bo'lsa, hammasi darhol ko'rinadi.
 */
function watchScroll() {
  const targets = document.querySelectorAll(".appear, .timeline, .slideshow");

  if (REDUCED || !("IntersectionObserver" in window)) {
    targets.forEach((el) => el.classList.add("in"));
    return;
  }

  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add("in");
          observer.unobserve(entry.target);
        }
      });
    },
    { threshold: 0.12, rootMargin: "0px 0px -8% 0px" }
  );

  targets.forEach((el) => observer.observe(el));
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", watchScroll);
} else {
  watchScroll();
}

/* ------------------------------------------------------- o'zi pastga tushish */

/*
 * Sahifa ochilgandan bir necha soniya keyin o'zi sekin pastga tusha boshlaydi.
 * Mehmon tegsa — to'xtamaydi, pauza qiladi: u tinchiganidan keyin o'sha
 * joydan davom etadi. Butunlay to'xtashi faqat sahifa oxiriga yetganda.
 */
function autoScroll() {
  if (REDUCED) return;
  // Mehmon tilni almashtirgan bo'lsa u sahifani allaqachon o'qiyapti
  if (window.scrollY > 40) return;

  const SPEED = 45; // sekundiga piksel
  const START_DELAY = 2000;
  const RESUME_DELAY = 2500; // tegishdan keyin shuncha kutib davom etadi
  const root = document.documentElement;
  let raf = null;
  let last = null;
  let pos = 0;
  let stopped = false;
  let idle = null;
  const events = ["wheel", "touchstart", "pointerdown", "keydown"];

  // Mehmon yozayotgan yoki kamera/rasm oynasi ochiq bo'lsa tegmaymiz.
  function busy() {
    const el = document.activeElement;
    if (el && /^(INPUT|TEXTAREA|SELECT)$/.test(el.tagName)) return true;
    return Array.from(document.querySelectorAll(".cam, .lightbox")).some(
      (n) => n.offsetParent !== null
    );
  }

  function halt() {
    if (raf) cancelAnimationFrame(raf);
    raf = null;
    last = null;
    // CSS'dagi silliq aylanishni qaytaramiz
    root.style.scrollBehavior = "";
  }

  function stop() {
    if (stopped) return;
    stopped = true;
    clearTimeout(idle);
    halt();
    events.forEach((ev) => window.removeEventListener(ev, pause));
  }

  function pause() {
    if (stopped) return;
    halt();
    clearTimeout(idle);
    idle = setTimeout(resume, RESUME_DELAY);
  }

  function resume() {
    if (stopped) return;
    if (busy()) {
      idle = setTimeout(resume, RESUME_DELAY);
      return;
    }
    pos = window.scrollY;
    last = null;
    // CSS'dagi scroll-behavior: smooth har bir qadamni bekor qiladi,
    // shuning uchun aylanish davomida uni vaqtincha o'chiramiz
    root.style.scrollBehavior = "auto";
    raf = requestAnimationFrame(step);
  }

  function step(now) {
    if (stopped) return;
    if (last === null) last = now;
    pos += (SPEED * (now - last)) / 1000;
    last = now;

    const bottom = document.body.scrollHeight - window.innerHeight;
    if (pos >= bottom - 2) return stop();

    // Kasr qiymatni to'plab boramiz, aks holda har kadrda 0 piksel chiqadi
    window.scrollTo(0, pos);
    raf = requestAnimationFrame(step);
  }

  events.forEach((ev) => window.addEventListener(ev, pause, { passive: true }));
  idle = setTimeout(resume, START_DELAY);
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", autoScroll);
} else {
  autoScroll();
}

/* ------------------------------------------------- til almashtirish */

/*
 * Til tugmasi bosilganda sahifa boshiga sakramasin — mehmon qayerda
 * turgan bo'lsa, yangi tilda ham o'sha joydan davom etsin.
 */
const SCROLL_KEY = "toy_scroll";

function keepScrollOnLangSwitch() {
  document.querySelectorAll(".langlink").forEach((link) => {
    link.addEventListener("click", () => {
      try {
        sessionStorage.setItem(SCROLL_KEY, String(window.scrollY));
      } catch (e) {}
    });
  });

  let saved = null;
  try {
    saved = sessionStorage.getItem(SCROLL_KEY);
    sessionStorage.removeItem(SCROLL_KEY);
  } catch (e) {}

  if (saved === null) return;
  const y = parseInt(saved, 10);
  if (!y) return;

  // Brauzerning o'z tiklashini o'chiramiz, aks holda ikkalasi urishadi
  if ("scrollRestoration" in history) history.scrollRestoration = "manual";

  const jump = () => {
    const prev = document.documentElement.style.scrollBehavior;
    document.documentElement.style.scrollBehavior = "auto";
    window.scrollTo(0, y);
    document.documentElement.style.scrollBehavior = prev;
  };

  jump();
  // Rasmlar yuklangach balandlik o'zgaradi, shuning uchun bir necha marta
  [60, 220, 600].forEach((ms) => setTimeout(jump, ms));
  window.addEventListener("load", jump, { once: true });
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", keepScrollOnLangSwitch);
} else {
  keepScrollOnLangSwitch();
}

/* ------------------------------------------------------------ sanoq */

function countdown() {
  return {
    left: { kun: 0, soat: 0, daqiqa: 0, soniya: 0 },
    done: false,
    pulse: false,

    init() {
      this.tick();
      setInterval(() => this.tick(), 1000);
    },

    tick() {
      const ms = new Date(CFG.eventIso).getTime() - Date.now();
      if (ms <= 0) {
        this.done = true;
        return;
      }
      this.done = false;
      this.left = {
        kun: Math.floor(ms / 86400000),
        soat: Math.floor((ms / 3600000) % 24),
        daqiqa: Math.floor((ms / 60000) % 60),
        soniya: Math.floor((ms / 1000) % 60),
      };
      // Soniya raqami almashganda yumshoq harakat
      if (!REDUCED) {
        this.pulse = false;
        requestAnimationFrame(() => {
          this.pulse = true;
        });
      }
    },

    pad(n) {
      return String(n).padStart(2, "0");
    },
  };
}

/* ------------------------------------------------------------ slayd-shou */

/* Rasmlar o'zi almashib turadi, nuqtalar bosilsa qo'lda ham boshqariladi. */
function slideshow() {
  return {
    index: 0,
    count: 0,
    timer: null,

    init() {
      this.count = this.$el.querySelectorAll("img").length;
      if (this.count > 1) this.start();
    },

    start() {
      this.timer = setInterval(() => {
        this.index = (this.index + 1) % this.count;
      }, 5000);
    },

    go(i) {
      this.index = i;
      clearInterval(this.timer);
      this.start();
    },
  };
}

/* ------------------------------------------------------------ javob (RSVP) */

function wishWall() {
  return {
    name: CFG.guestName || "",
    text: "",
    sending: false,
    error: "",
    notice: "",
    all: (CFG.wishes || []).slice(),
    index: 0,
    timer: null,

    init() {
      if (this.all.length > 1) this.resume();
    },

    resume() {
      clearInterval(this.timer);
      if (this.all.length < 2) return;
      this.timer = setInterval(() => this.next(), 6500);
    },

    pause() {
      clearInterval(this.timer);
    },

    next() {
      this.index = (this.index + 1) % this.all.length;
    },

    prev() {
      this.index = (this.index - 1 + this.all.length) % this.all.length;
    },

    async submit() {
      this.error = "";
      if (this.name.trim().length < 2) {
        this.error = "Ismingizni yozing.";
        return;
      }
      if (this.text.trim().length < 3) {
        this.error = "Tilagingizni yozing.";
        return;
      }
      this.sending = true;
      try {
        const res = await fetch("/api/wishes/", {
          method: "POST",
          headers: headers({ "Content-Type": "application/json" }),
          body: JSON.stringify({
            name: this.name.trim(),
            text: this.text.trim(),
            guest_code: CFG.guestCode,
            toy: CFG.toy,
          }),
        });
        const data = await res.json().catch(() => ({}));
        if (!res.ok) throw new Error(data.detail || firstError(data) || "Yuborilmadi.");
        this.text = "";
        if (data.pending) {
          // Tasdiqdan o'tmagan tilak sahifada ko'rinmaydi
          this.notice = CFG.wishPending;
        } else {
          this.all.unshift(data);
          this.index = 0;
          this.notice = CFG.wishAdded;
          this.resume();
        }
      } catch (e) {
        this.error = e.message;
      } finally {
        this.sending = false;
      }
    },
  };
}

/* ------------------------------------------------------------ fayl yuklash */

/*
 * MUHIM — asl sifat.
 * Fayl bu yerda hech qanday qayta ishlovdan o'tmaydi: canvas'ga chizilmaydi,
 * siqilmaydi, o'lchami kichraytirilmaydi. File obyekti FormData'ga qanday
 * bo'lsa shundayligicha qo'shiladi va serverga bir xil baytlar boradi.
 */
// Kamerada yozib olinadigan videoning eng uzun davomiyligi (sekund).
const REC_MAX_SEC = 180;

// Kamera talablari — rasm va video uchun bir xil.
const CAM_VIDEO = {
  facingMode: { ideal: "environment" },
  width: { ideal: 2560 },
  height: { ideal: 1440 },
};

// Kamerada olingan fayl nomi uchun vaqt tamg'asi.
function camStamp() {
  return new Date().toISOString().slice(0, 19).replace(/[:T]/g, "-");
}

function uploader() {
  return {
    name: (function () {
      try {
        return localStorage.getItem("toy_yuklovchi_ismi") || CFG.guestName || "";
      } catch (e) {
        return CFG.guestName || "";
      }
    })(),
    items: [],
    queue: [],
    busy: false,
    dragging: false,
    error: "",
    nextId: 1,

    // Sahifa ichidagi kamera
    camOpen: false,
    camError: "",
    stream: null,

    // Video yozish
    recording: false,
    recSec: 0,
    recorder: null,
    recChunks: [],
    recBytes: 0,
    recTimer: null,

    /*
     * Kamera brauzer ichida ochiladi — jonli tasvir va tugma.
     * Xavfsizlik sababli faqat https yoki localhost'da ishlaydi.
     */
    async openCamera() {
      this.camError = "";
      if (this.name.trim().length < 2) {
        this.error = "Avval ismingizni yozing.";
        return;
      }
      if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        this.camError = "Bu brauzer kamerani qo'llab-quvvatlamaydi.";
        this.camOpen = true;
        return;
      }
      this.camOpen = true;
      try {
        this.stream = await navigator.mediaDevices.getUserMedia({
          video: CAM_VIDEO,
          audio: false,
        });
        await this.$nextTick();
        const video = this.$refs.cam;
        if (video) {
          video.srcObject = this.stream;
          await video.play();
        }
      } catch (e) {
        this.camError =
          "Kameraga ruxsat berilmadi. Brauzer so'roviga «Ruxsat berish» deng. " +
          "Sayt https bo'lmasa kamera umuman ochilmaydi.";
      }
    },

    closeCamera() {
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
      if (this.stream) {
        this.stream.getTracks().forEach((t) => t.stop());
        this.stream = null;
      }
      this.camOpen = false;
      this.camError = "";
    },

    /*
     * Video yozish. Mikrofonga ruxsat faqat shu yerda so'raladi —
     * rasmga oladigan mehmonga mikrofon so'rovi chiqmaydi.
     * Oqim ovoz bilan qaytadan olinadi: ikki oqimni qo'shib yangi
     * MediaStream yasash ba'zi brauzerlarda sahifani yiqitadi.
     * Mikrofonga ruxsat berilmasa video ovozsiz yoziladi.
     */
    async startRec() {
      if (!window.MediaRecorder || !this.stream) {
        this.camError = "Bu brauzer video yozishni qo'llab-quvvatlamaydi.";
        return;
      }
      try {
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
      const video = this.$refs.cam;
      if (!video || !video.videoWidth) return;

      const canvas = document.createElement("canvas");
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;
      canvas.getContext("2d").drawImage(video, 0, 0);

      canvas.toBlob(
        (blob) => {
          if (!blob) return;
          const file = new File([blob], `kamera-${camStamp()}.jpg`, {
            type: "image/jpeg",
          });
          this.addFiles([file]);
          this.closeCamera();
        },
        "image/jpeg",
        0.95
      );
    },

    get doneCount() {
      return this.items.filter((i) => i.state === "done").length;
    },

    stateText(it) {
      if (it.state === "waiting") return "navbatda";
      if (it.state === "uploading") return it.progress + "%";
      if (it.state === "done") return "yuklandi · " + formatSize(it.size);
      return it.note;
    },

    addFiles(fileList) {
      const who = this.name.trim();
      if (who.length < 2) {
        this.error = "Avval ismingizni yozing — rasmlar shu nom bilan saqlanadi.";
        return;
      }
      this.error = "";
      try {
        localStorage.setItem("toy_yuklovchi_ismi", who);
      } catch (e) {}

      const limit = (CFG.maxUploadMb || 512) * 1024 * 1024;
      for (const file of Array.from(fileList)) {
        const tooBig = file.size > limit;
        const item = {
          id: this.nextId++,
          file: file,
          name: file.name,
          size: file.size,
          state: tooBig ? "error" : "waiting",
          note: tooBig ? CFG.maxUploadMb + " MB dan katta" : "",
          progress: 0,
        };
        this.items.push(item);
        if (!tooBig) this.queue.push(item);
      }
      this.run(who);
    },

    async run(who) {
      if (this.busy) return;
      this.busy = true;
      while (this.queue.length) {
        const item = this.queue.shift();
        item.state = "uploading";
        item.progress = 0;
        try {
          await this.send(item, who);
          item.state = "done";
          item.progress = 100;
        } catch (e) {
          item.state = "error";
          item.note = e.message;
        }
      }
      this.busy = false;
    },

    send(item, who) {
      return new Promise((resolve, reject) => {
        const form = new FormData();
        form.append("file", item.file, item.file.name);
        form.append("uploader_name", who);
        form.append("guest_code", CFG.guestCode);
        form.append("toy", CFG.toy || "");

        const xhr = new XMLHttpRequest();
        xhr.open("POST", "/api/uploads/");
        xhr.setRequestHeader("X-CSRFToken", CFG.csrfToken);
        xhr.upload.onprogress = (e) => {
          if (e.lengthComputable) {
            item.progress = Math.round((e.loaded / e.total) * 100);
          }
        };
        xhr.onload = () => {
          let data = {};
          try {
            data = JSON.parse(xhr.responseText);
          } catch (e) {}
          if (xhr.status >= 200 && xhr.status < 300) resolve(data);
          else reject(new Error(data.detail || "Yuklanmadi"));
        };
        xhr.onerror = () => reject(new Error("Aloqa uzildi"));
        xhr.send(form);
      });
    },
  };
}

/* ------------------------------------------------------------ musiqa */

/*
 * Musiqa hech qachon o'zi boshlanmaydi — brauzerlar buni bloklaydi va
 * mehmon uchun ham yoqimsiz. Tugma sukut bo'yicha o'chiq turadi.
 */
function musicPlayer() {
  return {
    playing: false,
    armed: false,

    init() {
      this.$nextTick(() => this.autoStart());
    },

    /*
     * Brauzerlar ovozli avtomatik ijroni bloklaydi. Shuning uchun avval
     * to'g'ridan-to'g'ri urinib ko'ramiz; bloklansa, mehmonning birinchi
     * harakatini (tegish, bosish, aylantirish) kutamiz va o'sha zahoti yoqamiz.
     */
    async autoStart() {
      const audio = this.$refs.audio;
      if (!audio) return;
      audio.muted = false;
      audio.volume = 0.45;
      try {
        await audio.play();
        // Chrome ba'zan xato bermay, ovozsiz ijro qiladi.
        // Shuning uchun haqiqatan yangrayotganini tekshiramiz.
        await new Promise((r) => setTimeout(r, 350));
        if (!audio.paused && audio.currentTime > 0) {
          this.playing = true;
          return;
        }
      } catch (e) {}

      // Ovozli avtoijro bloklandi. Ovozsiz boshlab turamiz — bunga
      // brauzerlar ruxsat beradi — va birinchi tegishda ovozni yoqamiz.
      // Shunda musiqa boshidan emas, o'sha joydan eshitiladi.
      try {
        audio.muted = true;
        await audio.play();
      } catch (e) {}
      this.playing = false;
      this.armFirstTouch();
    },

    armFirstTouch() {
      if (this.armed) return;
      this.armed = true;

      // "scroll" ATAYIN yo'q: sahifa o'zi pastga tushganda ham scroll
      // hodisasi chiqadi, lekin bu foydalanuvchi harakati emas —
      // brauzer ijroni rad etadi va tinglovchi behuda sarflanadi.
      const events = ["pointerdown", "touchstart", "click", "keydown", "wheel"];

      const start = async () => {
        const audio = this.$refs.audio;
        if (!audio) return;
        try {
          audio.muted = false;
          audio.volume = 0.45;
          if (audio.paused) await audio.play();
          await new Promise((r) => setTimeout(r, 200));
          if (!audio.paused && !audio.muted) {
            this.playing = true;
            // Faqat chindan yangragandan keyin tinglovchilarni olib tashlaymiz
            events.forEach((ev) => window.removeEventListener(ev, start));
          }
        } catch (e) {
          this.playing = false;
        }
      };

      events.forEach((ev) => window.addEventListener(ev, start, { passive: true }));
    },

    async toggle() {
      const audio = this.$refs.audio;
      if (!audio) return;
      if (this.playing) {
        audio.pause();
        this.playing = false;
      } else {
        try {
          audio.muted = false;
          audio.volume = 0.45;
          await audio.play();
          this.playing = true;
        } catch (e) {
          this.playing = false;
        }
      }
    },
  };
}