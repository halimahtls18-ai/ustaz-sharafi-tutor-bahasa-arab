# Ustaz Sharafi — Chatbot Tutor Nahwu & Sharaf Bahasa Arab

Chatbot pembelajaran bahasa Arab berbasis AI dengan persona **Ustaz Sharafi**,
seorang tutor yang fokus mengajarkan **Nahwu & Sharaf** (tata bahasa Arab,
khususnya tashrif/konjugasi fi'il) secara interaktif lewat terminal.

> Proyek ini dibuat untuk memenuhi Ujian Akhir Semester (UAS) mata kuliah
> Pemrograman Bahasa Arab (PBA), Program Studi Pendidikan Bahasa Arab.

## Identitas Mahasiswa

- **Nama**: `<isi nama Anda>`
- **NIM**: `<isi NIM Anda>`
- **Kelas / Semester**: `<isi kelas dan semester>`

> _Jika dikerjakan berkelompok (maksimal 2 orang), tambahkan baris nama & NIM
> anggota kedua di atas._

## Maharah & Level yang Dipilih

- **Maharah**: Nahwu / Sharaf (Tata Bahasa Arab)
- **Level**: Menengah
- **Alasan**: Tashrif (konjugasi) fi'il adalah salah satu kesulitan terbesar
  bagi pembelajar bahasa Arab tingkat menengah, karena perubahan bentuk kata
  berdasarkan dhamir (subjek) sangat banyak variasinya. Chatbot ini dirancang
  untuk melatih kemampuan tersebut secara repetitif namun tetap interaktif,
  dibantu penjelasan dari AI setiap kali murid melakukan kesalahan.

## Layanan API yang Digunakan

- **Google Gemini API** (`https://aistudio.google.com`) — model default:
  `gemini-2.5-flash` (dapat diganti melalui variabel `MODEL_NAME` di file
  `.env`).

## Fitur

- 🧕 **Persona konsisten** — Ustaz Sharafi dengan gaya bahasa dan metode
  mengajar yang khas (ramah, sabar, banyak contoh & transliterasi).
- 💬 **Riwayat percakapan (conversation history)** dalam satu sesi, bisa
  dilihat kembali lewat menu "Riwayat Percakapan".
- 📚 **4 mode pembelajaran**:
  1. **Ngobrol dengan Ustaz** — tanya jawab bebas seputar nahwu/sharaf,
     dijawab langsung oleh AI dengan mempertimbangkan riwayat percakapan.
  2. **Kuis Tashrif Klasik** — 20 soal tashrif fi'il; jika jawaban salah,
     AI akan memberikan penjelasan singkat secara otomatis.
  3. **Latihan Tashrif Mandiri** — masukkan fi'il pilihan Anda sendiri, AI
     akan membuatkan soal latihan baru secara dinamis dan mengoreksinya.
  4. **Riwayat Percakapan** — menampilkan ringkasan seluruh interaksi pada
     sesi yang sedang berjalan.
- 👋 **Pesan pembuka (greeting)** dari persona saat aplikasi dijalankan.
- 🚪 **Perintah keluar** (`exit` / `keluar` / `quit` / `selesai`) yang bisa
  diketik kapan saja, di mode apa saja.
- 🎨 Tampilan terminal yang rapi menggunakan library `rich`.

## Cara Instalasi & Menjalankan

1. **Clone repositori ini**

   ```bash
   git clone https://github.com/<username-anda>/ustaz-sharafi-tutor-bahasa-arab.git
   cd ustaz-sharafi-tutor-bahasa-arab
   ```

2. **Buat virtual environment (opsional, disarankan)**

   ```bash
   python -m venv venv
   source venv/bin/activate      # Windows: venv\Scripts\activate
   ```

3. **Install dependensi**

   ```bash
   pip install -r requirements.txt
   ```

4. **Siapkan API key**

   Salin `.env.example` menjadi `.env`, lalu isi `GEMINI_API_KEY` dengan
   API key Anda dari [Google AI Studio](https://aistudio.google.com/app/apikey).

   ```bash
   cp .env.example .env
   ```

5. **Jalankan aplikasi**

   ```bash
   python chatbot.py
   ```

## Struktur Proyek

```
ustaz-sharafi-tutor-bahasa-arab/
├── chatbot.py        # File utama aplikasi
├── requirements.txt  # Daftar library Python
├── .env.example       # Template variabel lingkungan (API key)
├── .gitignore         # Menyembunyikan .env dari Git
└── README.md          # Dokumentasi proyek (file ini)
```

## Contoh Tampilan

```
🕌 Ustaz Sharafi — Tutor Nahwu & Sharaf
السَّلَامُ عَلَيْكُمْ وَرَحْمَةُ اللهِ وَبَرَكَاتُهُ
Ahlan wa sahlan! Saya Ustaz Sharafi 👳, tutor khusus Nahwu & Sharaf...

📚 Menu Pembelajaran
1. Ngobrol dengan Ustaz
2. Kuis Tashrif Klasik
3. Latihan Tashrif Mandiri
4. Riwayat Percakapan
5. Keluar
```

_(Tambahkan screenshot asli aplikasi Anda di sini sebagai nilai tambah.)_

## Lisensi & Referensi

Sebagian struktur kode (penggunaan library `rich` untuk tampilan terminal)
mengacu pada dokumentasi resmi [rich](https://rich.readthedocs.io/) dan
[Anthropic API Docs](https://docs.claude.com/). Bank soal tashrif disusun
secara mandiri oleh penulis.
