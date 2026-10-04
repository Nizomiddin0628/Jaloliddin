/*
 * Taklifnoma sahifasining harakatlari.
 * Alpine.js komponentlari + bir nechta mustaqil effekt. Qurish (build) kerak emas.
 */

const CFG = window.TAKLIFNOMA || {};
const T = (() => {
  try { return JSON.parse(document.getElementById("ui-text").textContent); } catch (e) { return {}; }
})();
window.T = T;

const REDUCED = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
const GATE_KEY = "toy_parda_ochilgan";
const html = document.documentElement;

function ready(fn) {
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", fn);
  else fn();
}

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

function store(key, value) {
  try {
    if (value === undefined) return localStorage.getItem(key);
    if (value === null) localStorage.removeItem(key);
    else localStorage.setItem(key, value);
  } catch (e) { return null; }
}

/* ===================================================== kirish pardasi */

function intro() {
  return {
    opening: false,
    gone: false,

    init() {
      let seen = false;
      try { seen = sessionStorage.getItem(GATE_KEY) === "1"; } catch (e) {}
      // Til almashtirilganda yoki havola bo'limga olib kelganda konvert qayta chiqmaydi
      if (seen || location.hash) {
        this.gone = true;
        html.classList.add("is-open");
        window.dispatchEvent(new CustomEvent("gate-skipped"));
        afterOpen();
        return;
      }
      html.classList.add("is-locked");
      window.scrollTo(0, 0);
    },

    open() {
      if (this.opening) return;
      this.opening = true;
      try { sessionStorage.setItem(GATE_KEY, "1"); } catch (e) {}
      // Shu bosish — brauzer uchun «foydalanuvchi harakati», musiqa shu yerda yoqiladi
      window.dispatchEvent(new CustomEvent("gate-open"));
      if (navigator.vibrate) { try { navigator.vibrate(15); } catch (e) {} }
      const k = REDUCED ? 0 : 1;
      setTimeout(() => {
        html.classList.add("is-open");
        html.classList.remove("is-locked");
      }, 350 * k);
      setTimeout(() => { this.gone = true; afterOpen(); }, 1650 * k + 10);
    },
  };
}

let opened = false;
function afterOpen() {
  if (opened) return;
  opened = true;
  showDock();
}

/* ===================================================== til almashtirish */

const SCROLL_KEY = "toy_scroll";

function keepScrollOnLangSwitch() {
  document.querySelectorAll(".lang__a").forEach((link) => {
    link.addEventListener("click", () => {
      try { sessionStorage.setItem(SCROLL_KEY, String(window.scrollY)); } catch (e) {}
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
  if ("scrollRestoration" in history) history.scrollRestoration = "manual";
  const jump = () => {
    const prev = html.style.scrollBehavior;
    html.style.scrollBehavior = "auto";
    window.scrollTo(0, y);
    html.style.scrollBehavior = prev;
  };
  jump();
  [60, 220, 600].forEach((ms) => setTimeout(jump, ms));
  window.addEventListener("load", jump, { once: true });
}

/* ===================================================== ko'rinishga kirish */

function watchRise() {
  // Bir bo'lim ichidagi elementlar navbat bilan chiqadi
  const groups = new Map();
  const stagger = (el) => {
    const g = el.closest("section, footer") || document.body;
    const n = groups.get(g) || 0;
    groups.set(g, n + 1);
    el.style.setProperty("--k", Math.min(n, 6));
  };
  const targets = Array.from(document.querySelectorAll("[data-rise], [data-reveal-group]"));
  targets.forEach(stagger);
  if (REDUCED || !("IntersectionObserver" in window)) {
    targets.forEach((el) => el.classList.add("is-in"));
    return;
  }
  const io = new IntersectionObserver((entries) => {
    entries.forEach((e) => {
      if (e.isIntersecting) { e.target.classList.add("is-in"); io.unobserve(e.target); }
    });
  }, { threshold: 0.12, rootMargin: "0px 0px -6% 0px" });
  targets.forEach((el) => io.observe(el));

  // Alpine keyin qo'shgan elementlar uchun ham
  new MutationObserver((list) => {
    list.forEach((m) => m.addedNodes.forEach((n) => {
      if (n.nodeType !== 1) return;
      const els = n.matches && n.matches("[data-rise]") ? [n] : [];
      if (n.querySelectorAll) n.querySelectorAll("[data-rise]").forEach((x) => els.push(x));
      els.forEach((el) => io.observe(el));
    }));
  }).observe(document.body, { childList: true, subtree: true });
}

/* Tepadagi panel surat ustidan o'tgach oq fonga o'tadi */
function solidNav() {
  const nav = document.querySelector("[data-topnav]");
  const hero = document.getElementById("bosh");
  if (!nav || !hero) return;
  const plain = hero.classList.contains("hero--plain");
  const check = () => {
    const past = hero.getBoundingClientRect().bottom < 80;
    nav.classList.toggle("is-solid", plain ? window.scrollY > 10 : past);
  };
  check();
  window.addEventListener("scroll", check, { passive: true });
}

/* ===================================================== menyu */

function showDock() {
  const dock = document.querySelector("[data-dock]");
  const links = Array.from(document.querySelectorAll("[data-nav]"));
  const ids = Array.from(new Set(links.map((a) => a.dataset.nav)));
  const sections = ids.map((id) => document.getElementById(id)).filter(Boolean)
    .sort((a, b) => (a.compareDocumentPosition(b) & Node.DOCUMENT_POSITION_FOLLOWING ? -1 : 1));

  function setActive(id) {
    links.forEach((a) => a.classList.toggle("is-on", a.dataset.nav === id));
  }
  function visibility() {
    if (dock) dock.classList.toggle("is-shown", window.scrollY > window.innerHeight * 0.5);
  }
  // Ekran o'rtasidan yuqorida qolgan oxirgi bo'lim — faol
  let ticking = false;
  function pick() {
    ticking = false;
    const mid = window.innerHeight * 0.45;
    let cur = "bosh";
    sections.forEach((sec) => { if (sec.getBoundingClientRect().top < mid) cur = sec.id; });
    setActive(cur);
  }
  window.addEventListener("scroll", () => {
    if (!ticking) { ticking = true; requestAnimationFrame(pick); }
  }, { passive: true });
  setActive("bosh");
  visibility();
  window.addEventListener("scroll", visibility, { passive: true });
}

ready(() => {
  watchRise();
  solidNav();
  keepScrollOnLangSwitch();
});

/* ===================================================== sanoq */

function countdown() {
  return {
    left: { kun: 0, soat: 0, daqiqa: 0, soniya: 0 },
    done: false,
    timer: null,

    init() {
      this.tick();
      this.timer = setInterval(() => this.tick(), 1000);
    },
    tick() {
      const ms = new Date(CFG.eventIso).getTime() - Date.now();
      if (ms <= 0) { this.done = true; clearInterval(this.timer); return; }
      this.left = {
        kun: Math.floor(ms / 86400000),
        soat: Math.floor((ms / 3600000) % 24),
        daqiqa: Math.floor((ms / 60000) % 60),
        soniya: Math.floor((ms / 1000) % 60),
      };
    },
    pad(n) { return String(n).padStart(2, "0"); },
  };
}

/* ===================================================== galereya */

/* Gorizontal lenta: barmoq yoki tugmalar bilan suriladi, bosilsa kattalashadi. */
function gallery() {
  return {
    open: null,
    count: 0,
    cur: 0,
    progress: 0,
    items: [],

    get src() {
      return this.open === null ? "" : this.items[this.open].dataset.src;
    },

    init() {
      this.items = Array.from(this.$refs.gal.querySelectorAll(".gal__btn"));
      this.count = this.items.length;
      this.$nextTick(() => this.onScroll());
      window.addEventListener("resize", () => this.onScroll(), { passive: true });
    },

    onScroll() {
      const g = this.$refs.gal;
      const max = g.scrollWidth - g.clientWidth;
      this.progress = max > 0 ? Math.max(0.08, g.scrollLeft / max) : 1;
      const left = g.getBoundingClientRect().left;
      let best = 0, dist = Infinity;
      this.items.forEach((el, i) => {
        const d = Math.abs(el.getBoundingClientRect().left - left - parseFloat(getComputedStyle(g).paddingLeft));
        if (d < dist) { dist = d; best = i; }
      });
      this.cur = best;
    },

    slide(d) {
      const i = Math.max(0, Math.min(this.count - 1, this.cur + d));
      const g = this.$refs.gal;
      const target = this.items[i].closest(".gal__item");
      g.scrollTo({ left: target.offsetLeft - parseFloat(getComputedStyle(g).paddingLeft), behavior: REDUCED ? "auto" : "smooth" });
    },

    tap(i) {
      this.open = i;
      html.classList.add("is-locked");
    },
    close() {
      if (this.open === null) return;
      this.open = null;
      html.classList.remove("is-locked");
    },
    step(d) { this.open = (this.open + d + this.count) % this.count; },
  };
}

/* ===================================================== marosim */

function eventCard() {
  return {
    /* .ics fayl — telefon uni bevosita kalendarga qo'shadi */
    calendar() {
      const start = new Date(CFG.eventIso);
      const end = new Date(start.getTime() + 5 * 3600 * 1000);
      const fmt = (d) => d.toISOString().replace(/[-:]/g, "").replace(/\.\d{3}/, "");
      const esc = (s) => String(s || "").replace(/([,;\\])/g, "\\$1").replace(/\n/g, "\\n");
      const ics = [
        "BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//taklifnoma//uz", "BEGIN:VEVENT",
        "UID:" + fmt(start) + "@taklifnoma",
        "DTSTAMP:" + fmt(new Date()),
        "DTSTART:" + fmt(start),
        "DTEND:" + fmt(end),
        "SUMMARY:" + esc(CFG.title),
        "LOCATION:" + esc(CFG.place),
        "BEGIN:VALARM", "TRIGGER:-P1D", "ACTION:DISPLAY", "DESCRIPTION:" + esc(CFG.title), "END:VALARM",
        "END:VEVENT", "END:VCALENDAR",
      ].join("\r\n");
      const url = URL.createObjectURL(new Blob([ics], { type: "text/calendar;charset=utf-8" }));
      const a = document.createElement("a");
      a.href = url;
      a.download = "toy.ics";
      document.body.appendChild(a);
      a.click();
      setTimeout(() => { URL.revokeObjectURL(url); a.remove(); }, 1000);
    },
  };
}

/* ===================================================== javob (RSVP) */

function rsvpForm() {
  const key = "toy_javob_" + (CFG.guestCode || "umumiy");
  let saved = null;
  try { saved = JSON.parse(store(key) || "null"); } catch (e) {}
  return {
    name: CFG.guestName || (saved && saved.name) || "",
    attending: saved ? saved.attending : null,
    seats: (saved && saved.seats) || CFG.guestSeats || 1,
    phone: "",
    sending: false,
    sent: !!saved,
    error: "",

    async submit() {
      this.error = "";
      if (this.name.trim().length < 2) { this.error = T.err_name; return; }
      if (this.attending === null) { this.error = T.err_choice; return; }
      this.sending = true;
      try {
        const res = await fetch("/api/rsvp/", {
          method: "POST",
          headers: headers({ "Content-Type": "application/json" }),
          body: JSON.stringify({
            name: this.name.trim(),
            attending: this.attending,
            seats: this.attending ? Number(this.seats) : 1,
            phone: this.phone,
            message: "",
            guest_code: CFG.guestCode,
          }),
        });
        const data = await res.json().catch(() => ({}));
        if (!res.ok) throw new Error(data.detail || firstError(data) || T.err_send);
        this.sent = true;
        store(key, JSON.stringify({ name: this.name.trim(), attending: this.attending, seats: Number(this.seats) }));
      } catch (e) {
        this.error = e.message === "Failed to fetch" ? T.err_send : e.message;
      } finally {
        this.sending = false;
      }
    },
  };
}

/* ===================================================== duolar */

function duas(n) {
  return {
    i: 0,
    n: n,
    sx: 0,
    timer: null,
    init() { this.auto(); },
    auto() {
      clearInterval(this.timer);
      if (this.n > 1 && !REDUCED) this.timer = setInterval(() => (this.i = (this.i + 1) % this.n), 11000);
    },
    go(d) { this.i = (this.i + d + this.n) % this.n; this.auto(); },
    touchStart(e) { this.sx = e.changedTouches[0].clientX; },
    touchEnd(e) {
      const dx = e.changedTouches[0].clientX - this.sx;
      if (Math.abs(dx) > 50) this.go(dx < 0 ? 1 : -1);
    },
  };
}

/* ===================================================== tilaklar */

function wishWall() {
  return {
    name: CFG.guestName || "",
    text: "",
    sending: false,
    error: "",
    notice: "",
    all: (CFG.wishes || []).slice(),

    /* Kompyuterdagi ikki qator. Tilak kam bo'lsa — bitta qator. */
    get rows() {
      if (this.all.length < 6) return [this.all];
      return [this.all.filter((_, i) => i % 2 === 0), this.all.filter((_, i) => i % 2 === 1)];
    },

    async submit() {
      this.error = ""; this.notice = "";
      if (this.name.trim().length < 2) { this.error = T.err_name; return; }
      if (this.text.trim().length < 3) { this.error = T.err_wish; return; }
      this.sending = true;
      try {
        const res = await fetch("/api/wishes/", {
          method: "POST",
          headers: headers({ "Content-Type": "application/json" }),
          body: JSON.stringify({ name: this.name.trim(), text: this.text.trim(), guest_code: CFG.guestCode }),
        });
        const data = await res.json().catch(() => ({}));
        if (!res.ok) throw new Error(data.detail || firstError(data) || T.err_send);
        this.text = "";
        if (data.pending) {
          this.notice = T.wish_pending;
        } else {
          this.all.unshift(Object.assign(data, { fresh: true }));
          this.notice = T.wish_added;
          this.$nextTick(() => {
            const snap = this.$el.querySelector(".wish-snap");
            if (snap) snap.scrollTo({ left: 0, behavior: "smooth" });
          });
        }
      } catch (e) {
        this.error = e.message === "Failed to fetch" ? T.err_send : e.message;
      } finally {
        this.sending = false;
      }
    },
  };
}

/* ===================================================== fayl yuklash */

/*
 * MUHIM — asl sifat.
 * Fayl bu yerda hech qanday qayta ishlovdan o'tmaydi: siqilmaydi,
 * o'lchami kichraytirilmaydi. File obyekti FormData'ga qanday bo'lsa
 * shundayligicha qo'shiladi. Ko'rinadigan kichik rasm faqat ekranda.
 */
function uploader() {
  return {
    name: store("toy_yuklovchi_ismi") || CFG.guestName || "",
    items: [],
    queue: [],
    busy: false,
    dragging: false,
    error: "",
    nextId: 1,
    camOpen: false,
    camError: "",
    stream: null,

    async openCamera() {
      this.camError = "";
      if (this.name.trim().length < 2) { this.error = T.err_name_first; return; }
      if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        this.camError = T.cam_unsupported; this.camOpen = true; return;
      }
      this.camOpen = true;
      try {
        this.stream = await navigator.mediaDevices.getUserMedia({
          video: { facingMode: { ideal: "environment" }, width: { ideal: 2560 }, height: { ideal: 1440 } },
          audio: false,
        });
        await this.$nextTick();
        const video = this.$refs.cam;
        if (video) { video.srcObject = this.stream; await video.play(); }
      } catch (e) {
        this.camError = T.cam_denied;
      }
    },

    closeCamera() {
      if (this.stream) { this.stream.getTracks().forEach((t) => t.stop()); this.stream = null; }
      this.camOpen = false;
      this.camError = "";
    },

    shoot() {
      const video = this.$refs.cam;
      if (!video || !video.videoWidth) return;
      const canvas = document.createElement("canvas");
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;
      canvas.getContext("2d").drawImage(video, 0, 0);
      canvas.toBlob((blob) => {
        if (!blob) return;
        const stamp = new Date().toISOString().slice(0, 19).replace(/[:T]/g, "-");
        this.addFiles([new File([blob], `kamera-${stamp}.jpg`, { type: "image/jpeg" })]);
        this.closeCamera();
      }, "image/jpeg", 0.95);
    },

    get doneCount() { return this.items.filter((i) => i.state === "done").length; },

    stateText(it) {
      if (it.state === "waiting") return T.st_waiting;
      if (it.state === "uploading") return it.progress + "%";
      if (it.state === "done") return "✓ " + formatSize(it.size);
      return it.note;
    },

    addFiles(fileList) {
      const who = this.name.trim();
      if (who.length < 2) { this.error = T.err_name_first; return; }
      this.error = "";
      store("toy_yuklovchi_ismi", who);
      const limit = (CFG.maxUploadMb || 512) * 1024 * 1024;
      for (const file of Array.from(fileList)) {
        const tooBig = file.size > limit;
        const showable = /^image\/(jpeg|png|gif|webp)$/.test(file.type);
        const item = {
          id: this.nextId++,
          file: file,
          name: file.name,
          size: file.size,
          preview: showable ? URL.createObjectURL(file) : "",
          state: tooBig ? "error" : "waiting",
          note: tooBig ? CFG.maxUploadMb + " " + T.too_big : "",
          progress: 0,
        };
        this.items.unshift(item);
        if (!tooBig) this.queue.push(item);
      }
      this.run(who);
    },

    async run(who) {
      if (this.busy) return;
      this.busy = true;
      while (this.queue.length) {
        const item = this.queue.shift();
        const live = this.items.find((x) => x.id === item.id) || item;
        live.state = "uploading";
        live.progress = 0;
        try {
          await this.send(live, who);
          live.state = "done";
          live.progress = 100;
        } catch (e) {
          live.state = "error";
          live.note = e.message;
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
        const xhr = new XMLHttpRequest();
        xhr.open("POST", "/api/uploads/");
        xhr.setRequestHeader("X-CSRFToken", CFG.csrfToken);
        xhr.upload.onprogress = (e) => {
          if (e.lengthComputable) item.progress = Math.round((e.loaded / e.total) * 100);
        };
        xhr.onload = () => {
          let data = {};
          try { data = JSON.parse(xhr.responseText); } catch (e) {}
          if (xhr.status >= 200 && xhr.status < 300) resolve(data);
          else reject(new Error(data.detail || T.err_send));
        };
        xhr.onerror = () => reject(new Error(T.err_send));
        xhr.send(form);
      });
    },
  };
}

/* ===================================================== musiqa */

/*
 * Brauzerlar ovozni o'zi boshlashni taqiqlaydi. Eshikni ochish tugmasi
 * bosilishi — haqiqiy foydalanuvchi harakati, shuning uchun musiqa aynan
 * o'sha zahoti yoqiladi. Eshik ko'rsatilmagan bo'lsa birinchi tegishni kutamiz.
 */
function musicPlayer() {
  return {
    playing: false,
    armed: false,

    init() {
      const audio = this.$refs.audio;
      audio.volume = 0.45;
      audio.addEventListener("play", () => (this.playing = true));
      audio.addEventListener("pause", () => (this.playing = false));
      window.addEventListener("gate-open", () => this.play());
      window.addEventListener("gate-skipped", () => this.armFirstTouch());
    },

    async play() {
      try { await this.$refs.audio.play(); } catch (e) { this.armFirstTouch(); }
    },

    armFirstTouch() {
      if (this.armed) return;
      this.armed = true;
      const events = ["pointerdown", "touchstart", "keydown"];
      const start = async (e) => {
        // Musiqa tugmasining o'zi bosilsa — tugma o'zi hal qiladi
        if (e && e.target && e.target.closest && e.target.closest(".music")) return off();
        try { await this.$refs.audio.play(); off(); } catch (err) {}
      };
      const off = () => events.forEach((ev) => window.removeEventListener(ev, start, true));
      events.forEach((ev) => window.addEventListener(ev, start, { capture: true, passive: true }));
    },

    async toggle() {
      const audio = this.$refs.audio;
      if (!audio.paused) { audio.pause(); return; }
      try { await audio.play(); } catch (e) {}
    },
  };
}
