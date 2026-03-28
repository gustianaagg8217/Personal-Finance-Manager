# 🤖 Telegram Bot Setup Guide

## ⚠️ Mengapa Telegram Bot Tidak Berfungsi?

Untuk menjalankan Telegram Bot, Anda perlu **Telegram Bot Token**. Inilah yang sering menjadi masalah:

```
❌ TELEGRAM_BOT_TOKEN environment variable not set!
```

---

## ✅ SOLUSI CEPAT (3 Langkah)

### **Step 1: Buat Bot dengan BotFather**
1. Buka Telegram
2. Cari: **@BotFather**
3. Kirim command: `/newbot`
4. Ikuti instruksi (nama bot, username, dll)
5. **Copy token yang diberikan** (format: `1234567890:ABCDefGHIJKLmnoPQRstUVwxyz...`)

### **Step 2: Jalankan Setup Script**
```bash
setup_telegram.bat
```

Pilihan yang muncul:
- **1) Automatic Setup** - Pilih ini! (Save ke system)
- **2) Manual Setup** - Hanya session saat ini
- **3) Test Token** - Verifikasi token bekerja
- **4) Clear Token** - Hapus token lama

### **Step 3: Restart Terminal**
Tutup dan buka ulang terminal/command prompt, kemudian:
```bash
launcher.bat
```
Kemudian pilih **2) Start Telegram Bot**

---

## 🔧 Alternatif: Manual Setup via Environment Variable

### **Windows (Command Prompt)**
```cmd
set TELEGRAM_BOT_TOKEN=your_token_here
python run_telegram_bot.py
```

### **Windows (PowerShell)**
```powershell
$env:TELEGRAM_BOT_TOKEN="your_token_here"
python run_telegram_bot.py
```

### **Windows (Permanent - System Environment)**
```cmd
setx TELEGRAM_BOT_TOKEN "your_token_here"
```
Kemudian **restart terminal**.

### **Linux/Mac**
```bash
export TELEGRAM_BOT_TOKEN="your_token_here"
python run_telegram_bot.py
```

---

## 📝 Troubleshooting

### **"Invalid Token" Error**
- ✅ Token tidak boleh ada spasi
- ✅ Salin ulang dari @BotFather
- ✅ Token tidak pernah expire, tapi bisa di-reset di BotFather

### **"Bot Token Not Found"**
- ✅ Restart terminal setelah menjalankan `setup_telegram.bat`
- ✅ Gunakan `launcher.bat` opsi 2, akan prompt untuk token
- ✅ Cek environment: `set TELEGRAM_BOT_TOKEN` (CMD) atau `$env:TELEGRAM_BOT_TOKEN` (PowerShell)

### **Bot Error Saat Start**
- ✅ Jalankan `python run_telegram_bot.py` manual untuk debug
- ✅ Cek network/firewall
- ✅ Cek apakah BotFather bot masih aktif
- ✅ Install dependencies: `pip install -r requirements.txt`

---

## 📋 Bot Commands (Setelah Setup Berhasil)

Setelah bot running, gunakan di Telegram:

```
1️⃣ /add_transaction      - Tambah transaksi
2️⃣ /summary              - Lihat ringkasan
3️⃣ /category_report      - Laporan kategori
4️⃣ /monthly_report       - Laporan bulanan
5️⃣ /charts              - Grafik laporan
6️⃣ /set_budget          - Atur anggaran
7️⃣ /transactions        - Kelola transaksi
8️⃣ /analytics           - Analitik & kesehatan
9️⃣ /recurring           - Transaksi berulang
🔟 /export              - Ekspor data
1️⃣1️⃣ /settings          - Pengaturan
1️⃣2️⃣ /help              - Bantuan
```

---

## 🚀 Quick Reference

| Tindakan | Perintah |
|---------|---------|
| Setup Token | `setup_telegram.bat` |
| Test Token | `setup_telegram.bat` → pilih 3 |
| Start Bot (GUI) | `python launcher.py` |
| Start Bot (Menu) | `launcher.bat` → pilih 2 |
| Start Bot (Direct) | `python run_telegram_bot.py` |
| Check Token | `echo %TELEGRAM_BOT_TOKEN%` (CMD) |

---

## 💡 Pro Tips

1. **Simpan token di aman** - Jangan share dengan orang lain!
2. **Gunakan auto-setup** - Lebih mudah dan permanent
3. **Test token dulu** - Sebelum launch bot
4. **Monitor logs** - `telegram_bot.log` untuk debugging
5. **Restart bot** - Kalau ada error, stop dan jalankan ulang

---

## 📞 Still Having Issues?

1. ✅ Run setup: `setup_telegram.bat`
2. ✅ Test token: pilih opsi 3
3. ✅ Jalankan manual: `python run_telegram_bot.py`
4. ✅ Check logs: `telegram_bot.log`
5. ✅ Check docs: `README.md`

---

**Version**: 1.0  
**Last Updated**: 2026-03-28  
**Status**: Production Ready ✅

Selamat! Bot siap digunakan! 🎉
