/* Boshqaruv paneli — Alpine komponentlari. Qurish (build) kerak emas. */

const P = window.PANEL || {};
const REDUCED = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

function toast(text, kind) {
  window.dispatchEvent(new CustomEvent("toast", { detail: { text, kind: kind || "success" } }));
}

async function post(url, data, json) {
  const opts = {
    method: "POST",
    headers: { "X-CSRFToken": P.csrf, "X-Requested-With": "fetch" },
    credentials: "same-origin",
  };
  if (json) {
    opts.headers["Content-Type"] = "application/json";
    opts.body = JSON.stringify(data || {});
  } else {
    const fd = data instanceof FormData ? data : new FormData();
    if (!(data instanceof FormData)) Object.entries(data || {}).forEach(([k, v]) => fd.append(k, v));
    opts.body = fd;
  }
  const res = await fetch(url, opts);
  const body = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(body.detail || "Saqlanmadi. Qayta urinib ko'ring.");
  return body;
}

/* Qatorni chiroyli yo'qotish */
function vanish(el) {
  if (!el) return;
  if (REDUCED) return el.remove();
  el.style.height = el.offsetHeight + "px";
  el.classList.add("is-leaving");
  requestAnimationFrame(() => {
    el.style.height = "0px";
    el.style.marginTop = "0px";
    el.style.marginBottom = "0px";
    el.style.paddingTop = "0px";
    el.style.paddingBottom = "0px";
  });
  setTimeout(() => el.remove(), 450);
}

/* Raqamlar 0 dan sanab chiqadi */
function countUp() {
  if (REDUCED) return;
  document.querySelectorAll("[data-count]").forEach((el) => {
    const end = parseInt(el.dataset.count, 10);
    if (!end || end < 2) return;
    const t0 = performance.now();
    const dur = Math.min(1400, 500 + end * 12);
    (function frame(now) {
      const p = Math.min(1, (now - t0) / dur);
      el.textContent = Math.round(end * (1 - Math.pow(1 - p, 3)));
      if (p < 1) requestAnimationFrame(frame);
    })(t0);
  });
}
document.addEventListener("DOMContentLoaded", countUp);

/* ------------------------------------------------------------ umumiy qobiq */

function shell() {
  return {
    more: false,
    ask: null,
    toasts: [],
    n: 0,
    init() {
      window.addEventListener("toast", (e) => {
        const t = { id: ++this.n, text: e.detail.text, kind: e.detail.kind };
        this.toasts.push(t);
        setTimeout(() => (this.toasts = this.toasts.filter((x) => x.id !== t.id)), 3600);
      });
    },
    askFor(o) { this.ask = o; },
    async copy(text) {
      try {
        await navigator.clipboard.writeText(text);
      } catch (e) {
        const ta = document.createElement("textarea");
        ta.value = text;
        ta.style.position = "fixed";
        ta.style.opacity = "0";
        document.body.appendChild(ta);
        ta.select();
        document.execCommand("copy");
        ta.remove();
      }
      toast("Havola nusxalandi");
    },
    confirmDelete(evt, url, name) {
      const row = evt.target.closest("[data-row]");
      this.askFor({
        text: `${name} o'chirilsinmi? Buni qaytarib bo'lmaydi.`,
        yes: "O'chirish",
        go: async () => {
          try {
            await post(url, {});
            vanish(row);
            toast("O'chirildi");
          } catch (e) {
            toast(e.message, "error");
          }
        },
      });
    },
  };
}

/* ------------------------------------------------------------ bosh sahifa */

function toggles(initial) {
  return {
    s: initial,
    async set(field, value) {
      const old = this.s[field];
      this.s[field] = value;
      try {
        await post("/panel/holat/", { field, value }, true);
        const names = {
          mode: value === "thanks" ? "Rahmat sahifasi yoqildi" : "Taklifnoma rejimi yoqildi",
          rsvp_open: value ? "Javob qabul qilish ochildi" : "Javob qabul qilish yopildi",
          uploads_open: value ? "Rasm yuklash ochildi" : "Rasm yuklash yopildi",
          wishes_need_approval: value ? "Tilaklar endi tekshiriladi" : "Tilaklar darhol chiqadi",
          show_english: value ? "Ingliz tili tugmasi yoqildi" : "Ingliz tili tugmasi o'chirildi",
        };
        toast(names[field] || "Saqlandi");
      } catch (e) {
        this.s[field] = old;
        toast(e.message, "error");
      }
    },
  };
}

/* ------------------------------------------------------------ mehmonlar */

function guestsPage() {
  return {
    adding: false,
    mode: "one",
    qr: null,
    lines(text) { return text.split("\n").filter((l) => l.trim()).length; },
  };
}

/* ------------------------------------------------------------ tilaklar */

function wishesPage(pending) {
  return {
    pending: pending,
    async act(evt, url, act, card) {
      const el = evt.target.closest("[data-row]");
      const run = async () => {
        try {
          const r = await post(url, { act });
          this.pending = r.pending;
          if (act === "delete") vanish(el);
          else card.visible = act === "show";
          toast(r.msg);
        } catch (e) {
          toast(e.message, "error");
        }
      };
      if (act === "delete") {
        this.askFor({ text: "Tilak o'chirilsinmi?", yes: "O'chirish", go: run });
      } else {
        run();
      }
    },
  };
}

/* ------------------------------------------------------------ galereya */

function galleryPage(url) {
  return {
    over: false,
    busy: false,
    progress: 0,
    send(files) {
      const list = Array.from(files || []).filter((f) => f.type.startsWith("image/"));
      if (!list.length) return toast("Rasm fayl tanlang", "error");
      const fd = new FormData();
      list.forEach((f) => fd.append("images", f));
      this.busy = true;
      this.progress = 0;
      const xhr = new XMLHttpRequest();
      xhr.open("POST", url);
      xhr.setRequestHeader("X-CSRFToken", P.csrf);
      xhr.setRequestHeader("X-Requested-With", "fetch");
      xhr.upload.onprogress = (e) => {
        if (e.lengthComputable) this.progress = Math.round((e.loaded / e.total) * 100);
      };
      xhr.onload = () => {
        if (xhr.status >= 200 && xhr.status < 300) location.reload();
        else { this.busy = false; toast("Yuklanmadi. Fayl juda katta bo'lishi mumkin.", "error"); }
      };
      xhr.onerror = () => { this.busy = false; toast("Aloqa uzildi", "error"); };
      xhr.send(fd);
    },
    async saveCaption(form) {
      try {
        await post(form.action, new FormData(form));
        toast("Izoh saqlandi");
      } catch (e) {
        toast(e.message, "error");
        throw e;
      }
    },
  };
}

/* ------------------------------------------------------------ fayl tanlash */

function filePick(initial, name) {
  return {
    url: initial,
    fileName: "",
    fresh: false,
    isImage: name !== "music",
    pick(e) {
      const f = e.target.files[0];
      if (!f) return;
      this.url = URL.createObjectURL(f);
      this.fileName = f.name + " — saqlash tugmasini bosing";
      this.fresh = true;
    },
  };
}

/* ------------------------------------------------------------ esdalik ko'rgich */

function viewer() {
  return {
    i: null,
    items: [],
    init() {
      this.items = Array.from(this.$el.querySelectorAll(".mcard__open")).map((b) => ({
        src: b.dataset.src, video: b.dataset.video === "1",
      }));
    },
    get cur() { return this.i === null ? null : this.items[this.i]; },
    open(i) { this.i = i; document.documentElement.style.overflow = "hidden"; },
    close() { this.i = null; document.documentElement.style.overflow = ""; },
    step(d) {
      if (this.i === null) return;
      this.i = (this.i + d + this.items.length) % this.items.length;
    },
  };
}
