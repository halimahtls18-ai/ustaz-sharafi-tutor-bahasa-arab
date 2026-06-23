"""
==========================================================
 USTAZ SHARAFI - Versi Web (Streamlit)
==========================================================
Chatbot Tutor Nahwu & Sharaf Bahasa Arab - versi browser.
Logikanya sama dengan chatbot.py (versi terminal), hanya
tampilannya diubah menjadi antarmuka web menggunakan Streamlit.

Deploy gratis lewat https://share.streamlit.io
"""

import os
import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

# ----------------------------------------------------------------------------
# 0. KONFIGURASI DASAR
# ----------------------------------------------------------------------------
def get_secret(key, default=""):
    """Ambil API key dari Streamlit secrets (saat deploy) atau .env (saat lokal)."""
    try:
        return st.secrets[key]
    except Exception:
        return os.getenv(key, default)


API_KEY = get_secret("GEMINI_API_KEY", "").strip()
MODEL_NAME = get_secret("MODEL_NAME", "gemini-2.5-flash").strip()
API_URL_TEMPLATE = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"

PERSONA_NAME = "Ustaz Sharafi"
MAHARAH = "Nahwu & Sharaf (Tata Bahasa Arab)"
LEVEL = "Menengah"

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


# ----------------------------------------------------------------------------
# 1. FUNGSI PEMANGGIL AI (Gemini API)
# ----------------------------------------------------------------------------
def _to_gemini_contents(messages):
    contents = []
    for msg in messages:
        role = "model" if msg["role"] == "assistant" else "user"
        contents.append({"role": role, "parts": [{"text": msg["content"]}]})
    return contents


def call_gemini(messages, system=SYSTEM_PROMPT, max_tokens=500):
    if not API_KEY:
        return (
            "⚠️ GEMINI_API_KEY belum diatur. Jika ini berjalan di Streamlit Cloud, "
            "tambahkan secret GEMINI_API_KEY di menu Settings > Secrets. Jika lokal, "
            "isi file .env."
        )
    url = API_URL_TEMPLATE.format(model=MODEL_NAME)
    headers = {"x-goog-api-key": API_KEY, "content-type": "application/json"}
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
# 2. STATE AWAL (pengganti variabel global di versi terminal)
# ----------------------------------------------------------------------------
if "history" not in st.session_state:
    st.session_state.history = []  # riwayat percakapan mode ngobrol
if "quiz_idx" not in st.session_state:
    st.session_state.quiz_idx = 0
if "quiz_score" not in st.session_state:
    st.session_state.quiz_score = 0
if "quiz_log" not in st.session_state:
    st.session_state.quiz_log = []  # [(soal, jawaban, status, penjelasan)]
if "latihan_soal" not in st.session_state:
    st.session_state.latihan_soal = None


# ----------------------------------------------------------------------------
# 3. TAMPILAN UTAMA
# ----------------------------------------------------------------------------
st.set_page_config(page_title="Ustaz Sharafi - Tutor Nahwu & Sharaf", page_icon="🕌")

st.title("🕌 Ustaz Sharafi")
st.caption(f"Tutor {MAHARAH} — Level {LEVEL}")

with st.expander("👋 Salam Pembuka", expanded=False):
    st.markdown(
        "**السَّلَامُ عَلَيْكُمْ وَرَحْمَةُ اللهِ وَبَرَكَاتُهُ**\n\n"
        f"Ahlan wa sahlan! Saya **{PERSONA_NAME}**, tutor khusus **{MAHARAH}** "
        f"untuk level **{LEVEL}**. Saya akan membantu Anda memahami tashrif "
        "(konjugasi) fi'il, isim fa'il, isim maf'ul, dan kaidah nahwu/sharaf "
        "lainnya dengan sabar, in syaa Allah."
    )

mode = st.sidebar.radio(
    "📚 Pilih Mode Pembelajaran",
    ["💬 Ngobrol dengan Ustaz", "📝 Kuis Tashrif Klasik", "✍️ Latihan Tashrif Mandiri", "🗒️ Riwayat Percakapan"],
)

if not API_KEY:
    st.sidebar.warning("GEMINI_API_KEY belum diatur (lihat Settings > Secrets jika di Streamlit Cloud).")


# ----------------------------------------------------------------------------
# 4. MODE 1: NGOBROL BEBAS
# ----------------------------------------------------------------------------
if mode == "💬 Ngobrol dengan Ustaz":
    st.subheader("💬 Ngobrol Bebas")
    st.write("Tanyakan apa saja seputar nahwu, sharaf, atau kosakata Arab.")

    for msg in st.session_state.history:
        with st.chat_message("user" if msg["role"] == "user" else "assistant"):
            st.markdown(msg["content"])

    pertanyaan = st.chat_input("Tulis pertanyaan Anda...")
    if pertanyaan:
        st.session_state.history.append({"role": "user", "content": pertanyaan})
        with st.chat_message("user"):
            st.markdown(pertanyaan)
        with st.chat_message("assistant"):
            with st.spinner(f"{PERSONA_NAME} sedang berpikir..."):
                jawaban = call_gemini(st.session_state.history)
            st.markdown(jawaban)
        st.session_state.history.append({"role": "assistant", "content": jawaban})


# ----------------------------------------------------------------------------
# 5. MODE 2: KUIS TASHRIF KLASIK
# ----------------------------------------------------------------------------
elif mode == "📝 Kuis Tashrif Klasik":
    st.subheader("📝 Kuis Tashrif Klasik")
    total = len(BANK_SOAL)
    idx = st.session_state.quiz_idx

    if idx >= total:
        st.success(f"🎉 Kuis selesai! Skor Akhir: {st.session_state.quiz_score} / {total * 5}")
        for soal, jawaban, status, penjelasan in st.session_state.quiz_log:
            with st.expander(f"{status} — {soal[:50]}..."):
                st.write(f"**Jawaban Anda:** {jawaban}")
                if penjelasan:
                    st.write(f"**Penjelasan:** {penjelasan}")
        if st.button("🔄 Ulangi Kuis"):
            st.session_state.quiz_idx = 0
            st.session_state.quiz_score = 0
            st.session_state.quiz_log = []
            st.rerun()
    else:
        item = BANK_SOAL[idx]
        st.progress(idx / total)
        st.markdown(f"**Soal {idx + 1}/{total}**")
        st.info(item["soal"])

        jawaban = st.text_input("Jawaban Anda", key=f"jawaban_{idx}")
        if st.button("Kirim Jawaban", key=f"submit_{idx}"):
            if item["kunci"].lower() in jawaban.lower():
                st.session_state.quiz_score += 5
                st.success("✅ Mumtaz! Jawaban benar.")
                st.session_state.quiz_log.append((item["soal"], jawaban, "✅ Benar", None))
                st.session_state.quiz_idx += 1
                st.rerun()
            else:
                st.error(f"❌ Kurang tepat. Kunci jawaban: {item['kunci']}")
                with st.spinner(f"{PERSONA_NAME} menyiapkan penjelasan..."):
                    explanation = call_gemini(
                        [{
                            "role": "user",
                            "content": (
                                f"Seorang murid level {LEVEL} menjawab soal tashrif berikut dengan "
                                f"kurang tepat.\nSoal: {item['soal']}\nKunci jawaban: {item['kunci']}\n"
                                f"Jawaban murid: {jawaban}\nJelaskan singkat (3-4 kalimat) mengapa "
                                "kunci jawaban itu benar, dengan gaya ramah dan mendidik."
                            ),
                        }],
                        max_tokens=250,
                    )
                st.warning(f"💡 {explanation}")
                st.session_state.quiz_log.append((item["soal"], jawaban, "❌ Kurang Tepat", explanation))
                if st.button("Lanjut ke Soal Berikutnya ➡️", key=f"next_{idx}"):
                    st.session_state.quiz_idx += 1
                    st.rerun()


# ----------------------------------------------------------------------------
# 6. MODE 3: LATIHAN TASHRIF MANDIRI
# ----------------------------------------------------------------------------
elif mode == "✍️ Latihan Tashrif Mandiri":
    st.subheader("✍️ Latihan Tashrif Mandiri")
    st.write("Masukkan satu fi'il (kata kerja) bahasa Arab, AI akan membuat soal latihan baru untuk Anda.")

    kata = st.text_input("Masukkan Fi'il Madhi (contoh: kataba)")
    if st.button("Buat Soal"):
        if kata.strip():
            with st.spinner(f"{PERSONA_NAME} menyiapkan soal..."):
                soal_ai = call_gemini(
                    [{
                        "role": "user",
                        "content": (
                            f"Buatkan SATU soal latihan tashrif (konjugasi) fi'il bahasa Arab dari "
                            f"kata '{kata}' untuk murid level {LEVEL}. Pilih secara acak salah satu "
                            "bentuk: fi'il madhi, fi'il mudhari', atau fi'il amr, untuk dhamir "
                            "(subjek) tertentu. Format jawabanmu:\n"
                            "SOAL: <pertanyaan dalam Bahasa Indonesia, sebutkan kata aslinya dan "
                            "dhamir target>\nKUNCI: <jawaban transliterasi yang benar>"
                        ),
                    }],
                    max_tokens=200,
                )
            st.session_state.latihan_soal = soal_ai

    if st.session_state.latihan_soal:
        st.info(st.session_state.latihan_soal)
        jawaban_latihan = st.text_input("Jawaban Anda", key="jawaban_latihan")
        if st.button("Koreksi Jawaban"):
            with st.spinner(f"{PERSONA_NAME} mengoreksi..."):
                koreksi = call_gemini(
                    [{
                        "role": "user",
                        "content": (
                            f"Soal yang diberikan kepada murid:\n{st.session_state.latihan_soal}\n\n"
                            f"Jawaban murid: {jawaban_latihan}\nPeriksa apakah jawaban murid benar "
                            "berdasarkan KUNCI pada soal di atas. Jawab dengan format:\n"
                            "STATUS: Benar/Kurang Tepat\nPENJELASAN: <2-3 kalimat>"
                        ),
                    }],
                    max_tokens=250,
                )
            st.success(koreksi)


# ----------------------------------------------------------------------------
# 7. MODE 4: RIWAYAT PERCAKAPAN
# ----------------------------------------------------------------------------
elif mode == "🗒️ Riwayat Percakapan":
    st.subheader("🗒️ Riwayat Percakapan")
    if not st.session_state.history:
        st.write("_Belum ada riwayat percakapan pada sesi ini._")
    else:
        for i, msg in enumerate(st.session_state.history, start=1):
            peran = "Anda" if msg["role"] == "user" else PERSONA_NAME
            st.markdown(f"**{i}. {peran}:** {msg['content']}")
