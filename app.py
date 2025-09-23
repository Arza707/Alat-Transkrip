import os
import zipfile
import re
import tempfile
from flask import Flask, request, jsonify
import speech_recognition as sr
from pydub import AudioSegment

app = Flask(__name__)

# ---- Fungsi bantu ----
def mp3_to_text(mp3_path):
    """Konversi file MP3 jadi teks (menggunakan Google Speech Recognition)."""
    audio = AudioSegment.from_mp3(mp3_path)
    wav_path = mp3_path.replace(".mp3", ".wav")
    audio.export(wav_path, format="wav")

    recognizer = sr.Recognizer()
    with sr.AudioFile(wav_path) as source:
        audio_data = recognizer.record(source)

    try:
        return recognizer.recognize_google(audio_data, language="id-ID")
    except sr.UnknownValueError:
        return "[Tidak dikenali]"
    except sr.RequestError as e:
        return f"[Error Google Speech Recognition: {e}]"

def natural_sort_key(text):
    """Supaya urutan file chunk_1, chunk_2 ... chunk_10 benar."""
    return [int(num) if num.isdigit() else num for num in re.split(r'(\d+)', text)]

# ---- Endpoint API ----
@app.route("/")
def home():
    return jsonify({"message": "✅ API Transkrip Aktif di Replit 🚀"})

@app.route("/transkrip", methods=["POST"])
def transkrip():
    if "file" not in request.files:
        return jsonify({"error": "Upload file ZIP lewat form-data dengan key 'file'"}), 400

    zip_file = request.files["file"]

    # bikin folder sementara
    with tempfile.TemporaryDirectory() as extract_dir:
        zip_path = os.path.join(extract_dir, "input.zip")
        zip_file.save(zip_path)

        # ekstrak ZIP
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)

        all_text = []
        for file in sorted(os.listdir(extract_dir), key=natural_sort_key):
            if file.endswith(".mp3"):
                mp3_path = os.path.join(extract_dir, file)
                hasil = mp3_to_text(mp3_path)
                all_text.append(hasil)

        gabungan = " ".join(all_text)
        return jsonify({
            "status": "ok",
            "total_chunk": len(all_text),
            "hasil": gabungan
        })

# ---- Run server ----
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
