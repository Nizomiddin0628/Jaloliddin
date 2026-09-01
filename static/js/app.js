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
  const targets = document.querySelectorAll(".appear, .band, .timeline");

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

/* ------------------------------------------------------------ javob (RSVP) */

function rsvpForm() {
  return {
    // Shaxsiy havola bilan kelgan mehmonning ismi allaqachon ma'lum —
    // undan qaytadan so'ramaymiz.
    name: CFG.guestName || "",
    attending: null,
    seats: String(CFG.guestSeats || 1),
    phone: "",
    message: "",
    sending: false,
    sent: false,
    error: "",

    async submit() {
      this.error = "";
      if (this.name.trim().length < 2) {
        this.error = "Ismingizni to'liqroq yozing.";
        return;
      }
      if (this.attending === null) {
        this.error = "Kelasizmi yoki yo'q — belgilang.";
        return;
      }
      this.sending = true;
      try {
        const res = await fetch("/api/rsvp/", {
          method: "POST",
          headers: headers({ "Content-Type": "application/json" }),
          body: JSON.stringify({
            name: this.name.trim(),
            attending: this.attending,
            seats: this.attending ? Number(this.seats) : 0,
            phone: this.phone,
            message: this.message,
            guest_code: CFG.guestCode,
          }),
        });
        const data = await res.json().catch(() => ({}));
        if (!res.ok) throw new Error(data.detail || firstError(data) || "Yuborilmadi.");
        this.sent = true;
      } catch (e) {
        this.error = e.message;
      } finally {
        this.sending = false;
      }
    },
  };
}

/* ------------------------------------------------------------ tilaklar */

function wishWall() {
  return {
    name: CFG.guestName || "",
    text: "",
    sending: false,
    error: "",
    fresh: [],

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
          }),
        });
        const data = await res.json().catch(() => ({}));
        if (!res.ok) throw new Error(data.detail || firstError(data) || "Yuborilmadi.");
        this.fresh.unshift(data);
        this.text = "";
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
    async toggle() {
      const audio = this.$refs.audio;
      if (!audio) return;
      if (this.playing) {
        audio.pause();
        this.playing = false;
      } else {
        try {
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