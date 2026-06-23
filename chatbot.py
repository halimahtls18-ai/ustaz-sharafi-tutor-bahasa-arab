"""
==========================================================
 USTAZ SHARAFI - Chatbot Tutor Nahwu & Sharaf Bahasa Arab
==========================================================
Proyek UAS - Program Studi Pendidikan Bahasa Arab
Maharah   : Nahwu & Sharaf (Tata Bahasa Arab / Tashrif)
Level     : Menengah
API AI    : Anthropic Claude (https://console.anthropic.com)

Cara pakai singkat:
1. Copy .env.example menjadi .env
2. Isi ANTHROPIC_API_KEY di file .env
3. pip install -r requirements.txt
4. python chatbot.py
"""

import os
import sys
import requests
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table

# ----------------------------------------------------------------------------
# 0. KONFIGURASI DASAR
# ----------------------------------------------------------------------------
load_dotenv()

console = Console()

API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
MODEL_NAME = os.getenv("MODEL_NAME", "gemini-2.5-flash").strip()
API_URL_TEMPLATE = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"

PERSONA_NAME = "Ustaz Sharafi"
MAHARAH = "Nahwu & Sharaf (Tata Bahasa Arab)"
LEVEL = "Menengah"

EXIT_WORDS = {"exit", "keluar", "quit", "selesai"}
BACK_WORDS = {"kembali", "back", "menu"}

SYSTEM_PROMPT = f"""
Kamu adalah {PERSONA_NAME}, seorang ustaz/tutor bahasa Arab yang ramah, sabar, dan
berpengalaman, dengan spesialisasi pada maharah {MAHARAH} untuk murid level {LEVEL}.

Gaya mengajarmu:
- Selalu gunakan sapaan hangat khas pesantren/majelis ilmu (contoh: "Ahsanta!",
  "Mumtaz!", "Tafadhal", "Barakallahu fiik") secara wajar, tidak berlebihan.
- Jelaskan kaidah nahwu/sharaf (tashrif fi'il, isim fa'il, isim maf'ul, wazan, dll)
  dengan bahasa sederhana, contoh konkret, dan transliterasi Latin di samping
  teks Arab agar mudah dibaca pemula-menengah.
- Jika murid bertanya hal di luar bahasa Arab, tetap jawab dengan sopan, lalu
  arahkan kembali ke topik nahwu/sharaf jika relevan.
- Jawaban ringkas dan padat (maksimal sekitar 5-7 kalimat), kecuali diminta
  penjelasan mendalam.
- Selalu bersikap mendidik dan memberi semangat, tidak menggurui secara kasar.
"""

# ----------------------------------------------------------------------------
# 1. BANK SOAL (digunakan pada Mode Kuis Tashrif Klasik)
# ----------------------------------------------------------------------------
BANK_SOAL = [
    {"soal": "Ubah 'Kataba' (Dia laki-laki menulis) ke bentuk SAYA ('Saya telah menulis')!", "kunci": "katabtu"},
    {"soal": "Ubah Fi'il Madhi 'Akala' menjadi Fi'il Amr untuk KAMU LAKI-LAKI!", "kunci": "kul"},
    {"soal": "Ubah 'Huwa Yadzhabu' menjadi bentuk KITA (Nahnu)!", "kunci": "nadzhabu"},
    {"soal": "Bentuk Fi'il Mudhari' dari 'Qara'a' untuk DIA PEREMPUAN (Hiya)?", "kunci": "taqra'u"},
    {"soal": "Ubah 'Jalasa' menjadi Fi'il Amr untuk SEORANG PEREMPUAN!", "kunci": "ijlisi"},
    {"soal": "Bagaimana cara mengatakan 'Kalian laki-laki (Antum) telah belajar' dari kata 'Darasna'?", "kunci": "darastum"},
    {"soal": "Ubah 'Yasrabu' menjadi bentuk LARANGAN untuk laki-laki!", "kunci": "la tasyrab"},
    {"soal": "Ubah Fi'il Madhi 'Fataha' untuk pelaku KAMU PEREMPUAN (Anti)?", "kunci": "fatahti"},
    {"soal": "Ubah Fi'il Mudhari' 'Yusafiru' untuk subjek KAMU LAKI-LAKI (Anta)!", "kunci": "tusafiru"},
    {"soal": "Bagaimana 'Mereka berdua laki-laki (Huma) sedang masuk' dari 'Dakhala'?", "kunci": "yadkhulani"},
    {"soal": "Ubah 'Sami'a' menjadi Isim Fa'il bentuk tunggal laki-laki!", "kunci": "saami"},
    {"soal": "Bentuk jamak dari 'Muslimun' untuk perempuan?", "kunci": "muslimat"},
    {"soal": "Ubah 'Ghasala' menjadi Isim Maf'ul!", "kunci": "maghsul"},
    {"soal": "Ubah Fi'il Mudhari' 'Yatakallamu' untuk SAYA (Ana)?", "kunci": "atakallamu"},
    {"soal": "Ubah perintah 'I'mal' untuk KALIAN PEREMPUAN (Antunna)!", "kunci": "i'malna"},
    {"soal": "Bentuk Fi'il Madhi dari 'Yajlisu'?", "kunci": "jalasa"},
    {"soal": "Ubah 'Anta tusa'idu abaka' untuk subjek MEREKA LAKI-LAKI (Hum)!", "kunci": "yusa'iduna"},
    {"soal": "Apa bentuk Isim Makan dari 'Sajada'?", "kunci": "masjid"},
    {"soal": "Ubah 'Kharija' menjadi Fi'il Amr untuk KALIAN LAKI-LAKI (Antum)!", "kunci": "ukhruju"},
    {"soal": "Bagaimana cara mengatakan 'Kalian berdua (Antuma) telah pulang' dari 'Raja'a'?", "kunci": "raja'tuma"},
]

# Riwayat percakapan sesi (conversation history) - dipakai lintas mode
conversation_history = []


# ----------------------------------------------------------------------------
# 2. UTILITAS
# ----------------------------------------------------------------------------
def is_exit(text: str) -> bool:
    return text.strip().lower() in EXIT_WORDS


def is_back(text: str) -> bool:
    return text.strip().lower() in BACK_WORDS


def farewell():
    console.print(
        Panel.fit(
            f"[bold yellow]{PERSONA_NAME}:[/bold yellow] Jazakumullahu khairan telah "
            "belajar bersama saya hari ini. Semoga ilmu nahwu-sharaf-nya bermanfaat. "
            "Ma'as salamah! 👋",
            border_style="yellow",
        )
    )
    sys.exit(0)


def _to_gemini_contents(messages):
    """Konversi format messages (role: user/assistant) ke format Gemini (role: user/model)."""
    contents = []
    for msg in messages:
        role = "model" if msg["role"] == "assistant" else "user"
        contents.append({"role": role, "parts": [{"text": msg["content"]}]})
    return contents


def call_claude(messages, system=SYSTEM_PROMPT, max_tokens=500):
    """Memanggil Google Gemini API. Mengembalikan string jawaban.
    (Nama fungsi tetap call_claude agar tidak perlu mengubah seluruh pemanggil di bawah.)
    """
    if not API_KEY:
        return (
            "⚠️ GEMINI_API_KEY belum diatur. Silakan buat file .env (lihat "
            ".env.example) dan isi API key Anda agar fitur AI dapat berjalan."
        )

    url = API_URL_TEMPLATE.format(model=MODEL_NAME)
    headers = {
        "x-goog-api-key": API_KEY,
        "content-type": "application/json",
    }
    payload = {
        "contents": _to_gemini_contents(messages),
        "systemInstruction": {"parts": [{"text": system}]},
        "generationConfig": {"maxOutputTokens": max_tokens},
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        data = response.json()
        candidates = data.get("candidates", [])
        if not candidates:
            return "(Tidak ada respons dari AI, coba lagi.)"
        parts = candidates[0].get("content", {}).get("parts", [])
        hasil = "\n".join(p.get("text", "") for p in parts).strip()
        return hasil if hasil else "(Tidak ada respons dari AI, coba lagi.)"
    except requests.exceptions.HTTPError as e:
        return f"⚠️ Gagal menghubungi layanan AI (HTTP {e.response.status_code}). Periksa API key/kuota Anda."
    except requests.exceptions.RequestException as e:
        return f"⚠️ Gagal menghubungi layanan AI: {e}"


# ----------------------------------------------------------------------------
# 3. TAMPILAN
# ----------------------------------------------------------------------------
def print_greeting():
    greeting = f"""
[bold green]السَّلَامُ عَلَيْكُمْ وَرَحْمَةُ اللهِ وَبَرَكَاتُهُ[/bold green]

Ahlan wa sahlan! Saya [bold]{PERSONA_NAME}[/bold] 👳, tutor khusus
[bold]{MAHARAH}[/bold] untuk level [bold]{LEVEL}[/bold].

Saya akan membantu Anda memahami tashrif (konjugasi) fi'il, isim fa'il,
isim maf'ul, dan kaidah nahwu/sharaf lainnya dengan sabar, in syaa Allah.

Ketik salah satu dari [italic]{', '.join(sorted(EXIT_WORDS))}[/italic] kapan
saja untuk keluar dari aplikasi.
"""
    console.print(
        Panel(greeting, title="🕌 Ustaz Sharafi — Tutor Nahwu & Sharaf", border_style="green")
    )


def show_menu():
    table = Table(title="📚 Menu Pembelajaran", show_header=True, header_style="bold cyan")
    table.add_column("No", justify="center")
    table.add_column("Mode")
    table.add_column("Deskripsi")
    table.add_row("1", "Ngobrol dengan Ustaz", "Tanya bebas seputar nahwu, sharaf, atau kosakata Arab")
    table.add_row("2", "Kuis Tashrif Klasik", "20 soal tashrif fi'il, dikoreksi & dijelaskan oleh AI")
    table.add_row("3", "Latihan Tashrif Mandiri", "Masukkan fi'il pilihanmu, AI buatkan soal baru secara otomatis")
    table.add_row("4", "Riwayat Percakapan", "Lihat ringkasan percakapan pada sesi ini")
    table.add_row("5", "Keluar", "Selesai belajar untuk sesi ini")
    console.print(table)


# ----------------------------------------------------------------------------
# 4. MODE 1: NGOBROL BEBAS DENGAN AI (memakai conversation history)
# ----------------------------------------------------------------------------
def mode_ngobrol():
    console.print(
        Panel.fit(
            "[bold]Mode Ngobrol Bebas[/bold] — tanyakan apa saja tentang nahwu/sharaf. "
            "Ketik 'kembali' untuk balik ke menu utama.",
            border_style="cyan",
        )
    )
    while True:
        user_input = Prompt.ask("[bold magenta]Anda[/bold magenta]")
        if is_exit(user_input):
            farewell()
        if is_back(user_input):
            return

        conversation_history.append({"role": "user", "content": user_input})
        with console.status(f"[green]{PERSONA_NAME} sedang berpikir..."):
            reply = call_claude(conversation_history)
        conversation_history.append({"role": "assistant", "content": reply})
        console.print(Panel(reply, title=f"🧕 {PERSONA_NAME}", border_style="green"))


# ----------------------------------------------------------------------------
# 5. MODE 2: KUIS TASHRIF KLASIK (bank soal lokal + penjelasan dari AI)
# ----------------------------------------------------------------------------
def mode_kuis():
    score = 0
    total = len(BANK_SOAL)
    console.print(
        Panel.fit(
            f"[bold]Mode Kuis Tashrif Klasik[/bold] — {total} soal. "
            "Ketik 'kembali' kapan saja untuk berhenti lebih awal.",
            border_style="cyan",
        )
    )
    for i, item in enumerate(BANK_SOAL, start=1):
        console.print(f"\n[bold cyan]📋 Soal {i}/{total}[/bold cyan]")
        console.print(f"[white]{item['soal']}[/white]")

        jawaban = Prompt.ask("[bold magenta]Jawaban Anda[/bold magenta]")
        if is_exit(jawaban):
            farewell()
        if is_back(jawaban):
            break

        conversation_history.append(
            {"role": "user", "content": f"(Kuis) {item['soal']} -> jawaban saya: {jawaban}"}
        )

        if item["kunci"].lower() in jawaban.lower():
            score += 5
            console.print("[bold green]✅ Mumtaz! Jawaban benar.[/bold green]")
            conversation_history.append({"role": "assistant", "content": "Mumtaz, jawaban benar."})
        else:
            console.print(f"[bold red]❌ Kurang tepat.[/bold red] Kunci jawaban: [yellow]{item['kunci']}[/yellow]")
            with console.status(f"[green]{PERSONA_NAME} menyiapkan penjelasan..."):
                explanation_msgs = [
                    {
                        "role": "user",
                        "content": (
                            f"Seorang murid level {LEVEL} menjawab soal tashrif berikut dengan kurang tepat.\n"
                            f"Soal: {item['soal']}\n"
                            f"Kunci jawaban: {item['kunci']}\n"
                            f"Jawaban murid: {jawaban}\n"
                            "Jelaskan singkat (3-4 kalimat) mengapa kunci jawaban itu benar, "
                            "dengan gaya ramah dan mendidik."
                        ),
                    }
                ]
                explanation = call_claude(explanation_msgs, max_tokens=250)
            conversation_history.append({"role": "assistant", "content": explanation})
            console.print(Panel(explanation, title="💡 Penjelasan Ustaz Sharafi", border_style="yellow"))

    console.print(f"\n[bold gold1]🎉 Skor Akhir Anda: {score} / {total * 5} 🎉[/bold gold1]")


# ----------------------------------------------------------------------------
# 6. MODE 3: LATIHAN TASHRIF MANDIRI (soal dibuat dinamis oleh AI)
# ----------------------------------------------------------------------------
def mode_latihan_mandiri():
    console.print(
        Panel.fit(
            "[bold]Mode Latihan Tashrif Mandiri[/bold] — masukkan satu kata fi'il (kata kerja) "
            "bahasa Arab (transliterasi), lalu AI akan membuatkan soal latihan baru untukmu. "
            "Ketik 'kembali' untuk balik ke menu.",
            border_style="cyan",
        )
    )
    while True:
        kata = Prompt.ask("[bold magenta]Masukkan Fi'il Madhi (contoh: kataba)[/bold magenta]")
        if is_exit(kata):
            farewell()
        if is_back(kata):
            return

        with console.status(f"[green]{PERSONA_NAME} menyiapkan soal..."):
            soal_msgs = [
                {
                    "role": "user",
                    "content": (
                        f"Buatkan SATU soal latihan tashrif (konjugasi) fi'il bahasa Arab dari kata "
                        f"'{kata}' untuk murid level {LEVEL}. Pilih secara acak salah satu bentuk: "
                        "fi'il madhi, fi'il mudhari', atau fi'il amr, untuk dhamir (subjek) tertentu. "
                        "Format jawabanmu:\n"
                        "SOAL: <pertanyaan dalam Bahasa Indonesia, sebutkan kata aslinya dan dhamir target>\n"
                        "KUNCI: <jawaban transliterasi yang benar>"
                    ),
                }
            ]
            soal_ai = call_claude(soal_msgs, max_tokens=200)
        conversation_history.append({"role": "assistant", "content": soal_ai})
        console.print(Panel(soal_ai, title="📝 Soal dari Ustaz Sharafi", border_style="cyan"))

        jawaban = Prompt.ask("[bold magenta]Jawaban Anda[/bold magenta]")
        if is_exit(jawaban):
            farewell()
        if is_back(jawaban):
            continue

        conversation_history.append({"role": "user", "content": f"Jawaban saya: {jawaban}"})
        with console.status(f"[green]{PERSONA_NAME} mengoreksi..."):
            koreksi_msgs = [
                {
                    "role": "user",
                    "content": (
                        f"Soal yang diberikan kepada murid:\n{soal_ai}\n\n"
                        f"Jawaban murid: {jawaban}\n"
                        "Periksa apakah jawaban murid benar berdasarkan KUNCI pada soal di atas. "
                        "Jawab dengan format:\nSTATUS: Benar/Kurang Tepat\nPENJELASAN: <2-3 kalimat>"
                    ),
                }
            ]
            koreksi = call_claude(koreksi_msgs, max_tokens=250)
        conversation_history.append({"role": "assistant", "content": koreksi})
        console.print(Panel(koreksi, title="📋 Hasil Koreksi", border_style="green"))


# ----------------------------------------------------------------------------
# 7. MODE 4: LIHAT RIWAYAT PERCAKAPAN
# ----------------------------------------------------------------------------
def mode_riwayat():
    if not conversation_history:
        console.print("[italic]Belum ada riwayat percakapan pada sesi ini.[/italic]")
        return

    table = Table(title="🗒️ Riwayat Percakapan Sesi Ini")
    table.add_column("No", justify="center")
    table.add_column("Peran")
    table.add_column("Isi")
    for i, msg in enumerate(conversation_history, start=1):
        isi = msg["content"]
        if len(isi) > 90:
            isi = isi[:90] + "..."
        peran = "Anda" if msg["role"] == "user" else PERSONA_NAME
        table.add_row(str(i), peran, isi)
    console.print(table)


# ----------------------------------------------------------------------------
# 8. PROGRAM UTAMA
# ----------------------------------------------------------------------------
def main():
    print_greeting()
    while True:
        show_menu()
        pilihan = Prompt.ask("[bold cyan]Pilih mode (1-5)[/bold cyan]")

        if is_exit(pilihan):
            farewell()
        elif pilihan.strip() == "1":
            mode_ngobrol()
        elif pilihan.strip() == "2":
            mode_kuis()
        elif pilihan.strip() == "3":
            mode_latihan_mandiri()
        elif pilihan.strip() == "4":
            mode_riwayat()
        elif pilihan.strip() == "5":
            farewell()
        else:
            console.print("[red]Pilihan tidak dikenali, silakan coba lagi (1-5).[/red]")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[yellow]Aplikasi dihentikan oleh pengguna.[/yellow]")
        sys.exit(0)
