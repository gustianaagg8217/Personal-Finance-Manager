# 🚀 Personal Finance Manager - Launcher Guide

## Pengenalan

Personal Finance Manager kini dilengkapi dengan **tiga pilihan launcher** untuk kemudahan penggunaan:

1. **GUI Launcher** (Gui Principal) - `launcher.py`
2. **Batch Menu** (Menu Command Line) - `launcher.bat`
3. **Desktop Shortcut Generator** - `create_shortcut.bat`

---

## 📋 Opsi Launcher

### 1️⃣ GUI Launcher (`launcher.py`) - RECOMMENDED ✨

**Cara Menggunakan:**
```bash
python launcher.py
```

**Fitur:**
- ✅ Interface visual yang user-friendly
- ✅ Status sistem real-time (Python version, files, database)
- ✅ Tombol untuk start CLI atau Telegram Bot
- ✅ Kontrol process (start, stop, restart)
- ✅ Link ke dokumentasi
- ✅ Timestamp aktif
- ✅ Color-coded status indicators

**Menu Options:**
- **▶ Start CLI** - Jalankan aplikasi desktop lengkap (12 menu items)
- **▶ Start Telegram Bot** - Jalankan bot Telegram (12 commands)
- **▶ Start Both** - Jalankan CLI dan Bot bersamaan
- **⏹ Stop All** - Hentikan semua proses running
- **🔄 Restart All** - Restart semua proses
- **📖 Documentation** - Buka README.md

---

### 2️⃣ Batch Menu Launcher (`launcher.bat`)

**Cara Menggunakan:**
```bash
launcher.bat
```
Atau double-click `launcher.bat` di File Explorer

**Fitur:**
- ✅ Menu interaktif di command line
- ✅ Pilihan simpel: 1-5
- ✅ Tidak perlu Python command
- ✅ Cocok untuk quick launch

**Menu Options:**
```
1) Start CLI Application
2) Start Telegram Bot
3) Start Both (CLI + Bot)
4) Stop All Running Processes
5) View Documentation
0) Exit
```

---

### 3️⃣ Desktop Shortcut Generator (`create_shortcut.bat`)

**Cara Menggunakan:**
- Double-click `create_shortcut.bat`
- Atau run dari command line:
```bash
create_shortcut.bat
```

**Hasil:**
- Membuat shortcut di Desktop: `Personal Finance Manager.lnk`
- Double-click shortcut untuk launch GUI Launcher

---

## 🎯 Rekomendasi Penggunaan

| Situasi | Gunakan |
|---------|---------|
| Pertama kali menggunakan | `create_shortcut.bat` (buat shortcut) |
| Usage sehari-hari | Double-click shortcut di Desktop |
| Automation / Script | `launcher.bat` (batch friendly) |
| Advanced control | `launcher.py` (GUI dengan monitoring) |
| Dari terminal | `python launcher.py` atau `launcher.bat` |

---

## 📊 System Requirements

- **Python 3.8+** ✅
- **Windows / Linux / Mac** ✅
- **Tkinter** (included dengan Python) ✅
- **Internet** (untuk Telegram Bot) ✅

---

## ⚡ Quick Start

### Opsi 1: GUI (Recommended)
```bash
python launcher.py
```

### Opsi 2: Batch
```bash
launcher.bat
```

### Opsi 3: Desktop Shortcut
```bash
create_shortcut.bat
```
Kemudian double-click shortcut yang tercipta.

---

## 🔧 Troubleshooting

### "Python not found"
- **Solusi**: Install Python dari https://python.org
- Pastikan "Add to PATH" di-check saat instalasi

### GUI tidak muncul
- **Solusi**: Tkinter mungkin tidak terinstall
- Jalankan: `pip install tk`

### Bot tidak start
- **Solusi**: Check TELEGRAM_BOT_TOKEN di `configs/`
- Pastikan bot sudah dicreate di Telegram BotFather

### CLI tidak start
- **Solusi**: Check folder `configs/` dan database `trades.db`
- Jalankan `main.py` manual untuk diagnostik

---

## 📚 Dokumentasi Lengkap

- **CLI Menu**: 12 menu items lengkap
  1. Add Transaction
  2. Summary
  3. Category Report
  4. Monthly Report
  5. Charts
  6. Set Budget
  7. Manage Transactions
  8. Analytics & Health
  9. Recurring Transactions
  10. Export Data
  11. Settings
  12. Help

- **Telegram Bot**: 12 commands sama dengan CLI
  - `/add_transaction` - Tambah transaksi
  - `/summary` - Lihat ringkasan
  - `/category_report` - Laporan kategori
  - `/monthly_report` - Laporan bulanan
  - `/charts` - Grafik laporan
  - `/set_budget` - Atur anggaran
  - `/transactions` - Kelola transaksi
  - `/analytics` - Analitik & kesehatan
  - `/recurring` - Transaksi berulang
  - `/export` - Ekspor data
  - `/settings` - Pengaturan
  - `/help` - Bantuan

---

## 💡 Tips

1. **Mulai dengan launcher.bat** jika belum familiar
2. **Buat shortcut** untuk akses cepat di Desktop
3. **Monitor status** di GUI Launcher
4. **Stop All** jika ada issues
5. **Check logs** di console untuk debugging

---

## 📞 Support

Untuk masalah atau pertanyaan:
- Check README.md di folder utama
- Review logs di console output
- Restart application

---

**Version**: 1.0  
**Last Updated**: 2026-03-28  
**Status**: Production Ready ✅

Selamat menggunakan Personal Finance Manager! 🎉
