# 🎨 Gemini Desktop Blender Bridge (Pi Agent Skill)

[![Blender](https://img.shields.io/badge/Blender-4.x%20%7C%205.x-E87D0D?logo=blender&logoColor=white)](https://www.blender.org/)
[![Pi Agent](https://img.shields.io/badge/Agent-Pi%20Coding%20Agent-6C5CE7)](https://github.com/earendil-works/pi)
[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

Jembatan dua arah (bidirectional bridge) real-time antara **Pi Terminal Coding Agent (didukung Gemini Flash / LLM)** dan aplikasi **Blender Desktop**. 

Cukup minta di terminal Pi seperti: *"Buatkan mobil low-poly warna merah di Blender"*, dan model 3D akan **langsung muncul dan ter-update di 3D Viewport Blender Anda seketika!**

---

## 🏛️ Arsitektur Sistem (System Architecture)

```
┌─────────────────────────────────────────────────────────────────┐
│                    Terminal / Pi Coding Agent                   │
│                                                                 │
│   User Prompt: "Buatkan kursi kayu di Blender"                  │
│       │                                                         │
│       ▼                                                         │
│   [Gemini Flash / LLM] ───> Generates bpy Python Script         │
│       │                                                         │
│       ▼                                                         │
│   [send_to_blender.py] (Client CLI)                             │
└───────────────┬─────────────────────────────────┬───────────────┘
                │                                 │
     (Primary: HTTP REST POST)        (Fallback: File Watcher)
     http://localhost:9876/execute    ~/.blender_bridge/task.py
                │                                 │
                ▼                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Blender Desktop GUI                        │
│                                                                 │
│   [blender_bridge.py] (Threaded Server + Modal Timer)           │
│       │                                                         │
│       ▼                                                         │
│   bpy.app.timers (Main Thread Execution)                        │
│       │                                                         │
│       ├──> Executes bpy script (Mesh, Materials, Modifiers)     │
│       └──> Triggers 3D Viewport Redraw (Immediate Visual Update)│
│                                                                 │
│   🎉 3D Asset langsung muncul di layar Anda!                    │
└─────────────────────────────────────────────────────────────────┘
```

### Keunggulan Arsitektur Dual-Transport:
1. **HTTP REST (Fast):** Mengirim kode secara instan via endpoint HTTP lokal (`http://localhost:9876/execute`).
2. **File Watcher (Zero-Config Fallback):** Sangat ideal untuk pengguna WSL2 ke Windows Desktop di mana firewall sering memblokir port jaringan. Script otomatis menulis ke shared directory `~/.blender_bridge/task.py` yang dipantau Blender setiap 100ms.

---

## 🚀 Fitur Utama

- ⚡ **Real-time Live Sync:** Objek langsung terbuat di Viewport tanpa perlu me-reload file.
- 🧱 **Dukungan PBR Material & Modifier:** Agent otomatis mengatur *Principled BSDF*, warna, roughness, metallic, bevel, dan subsurf.
- 📦 **Export Langsung ke `.glb`:** Bisa minta agent untuk langsung mengekspor hasil ke format binary 3D `.glb` / `.gltf`.
- 🔄 **Multi-Platform & WSL2 Ready:** Berjalan lancar di Linux, macOS, Windows native, serta WSL2 -> Windows Desktop.
- 🛡️ **Thread-Safe:** Eksekusi kode dilakukan di thread utama Blender (`bpy.app.timers`) untuk mencegah crash atau context error.

---

## 📂 Struktur Repositori

```bash
gemini-desktop-bridge-skill/
├── README.md                      # Dokumentasi & panduan
├── install.sh                     # Script installer 1-klik untuk Pi Agent
├── blender_addon/
│   └── blender_bridge.py          # Script listener yang dijalankan di Blender
├── skill/
│   ├── SKILL.md                   # Definisi Skill untuk Pi Coding Agent
│   └── scripts/
│       └── send_to_blender.py     # Script pengirim (HTTP + File Watcher)
└── examples/
    ├── 01_coffee_cup.py           # Contoh: Cangkir kopi prosedural
    ├── 02_lowpoly_car.py          # Contoh: Mobil low-poly dengan roda
    └── 03_export_glb.py           # Contoh: Objek kristal + export .glb
```

---

## 🛠️ Panduan Instalasi & Penggunaan

### Langkah 1: Pasang Skill di Pi Coding Agent
Jalankan perintah ini di terminal Anda:

```bash
git clone https://github.com/FidelCristopher/gemini-desktop-bridge-skill.git
cd gemini-desktop-bridge-skill
./install.sh
```
*Script ini akan otomatis meng-copy skill ke `~/.pi/agent/skills/blender-bridge/`.*

---

### Langkah 2: Jalankan Listener di Blender Desktop
1. Buka aplikasi **Blender** di desktop Anda.
2. Buka tab **Scripting** (di menu atas).
3. Klik tombol **Open** (atau klik **New** lalu paste isi file `blender_addon/blender_bridge.py`).
4. Klik tombol **Run Script** (atau tekan `Alt + P`).
5. Di tab 3D Viewport (tekan tombol `N` untuk membuka sidebar), Anda juga akan melihat tab baru **Pi Bridge** dengan status:
   ```
   🟢 Status: Active (Port 9876)
   ```

---

### Langkah 3: Gunakan di Terminal Pi!
Sekarang Anda cukup berbicara dengan Pi di terminal:

> **User:** *"Tolong buatkan meja kayu low-poly lengkap dengan 4 kaki di Blender"*
> 
> **Pi:** *(Mengenerate kode Python `bpy` dan otomatis mengirimkannya ke Blender)*
> 
> **Hasil:** Meja kayu langsung muncul di layar Blender Anda! ✨

---

## 💬 Contoh Perintah yang Bisa Anda Minta

- *"Buatkan cangkir kopi keramik dengan uap dan gagang"*
- *"Buatkan mobil sport low-poly dengan roda hitam dan bodi merah metallic"*
- *"Buatkan pohon low-poly dengan daun berbentuk icosohedron"*
- *"Hapus semua objek di scene lalu buatkan donat dengan icing warna pink"*
- *"Buatkan pedang sci-fi dengan material neon emission dan ekspor ke format .glb"*

---

## 🧪 Tes Manual (CLI Test)

Jika ingin menguji koneksi tanpa chat ke agent:

```bash
# Cek status koneksi Blender
python3 skill/scripts/send_to_blender.py --status

# Kirim contoh cangkir kopi ke Blender
python3 skill/scripts/send_to_blender.py --file examples/01_coffee_cup.py

# Kirim contoh mobil low-poly ke Blender
python3 skill/scripts/send_to_blender.py --file examples/02_lowpoly_car.py
```

---

## 🤝 Kontribusi & Lisensi

Dibuat dengan ❤️ oleh [Fidel Cristopher](https://github.com/FidelCristopher).
Proyek ini dilisensikan di bawah [MIT License](LICENSE). Pull Request dan saran sangat dipersilakan!
