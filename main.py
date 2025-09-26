import os
from flask import Flask, render_template, request
from pydub import AudioSegment
import speech_recognition as sr

app = Flask(__name__)

# Set path ffmpeg (biar pydub bisa pakai ffmpeg di server Pella)
from pydub.utils import which
AudioSegment.converter = which("ffmpeg")

# Halaman utama (form upload)
@app.route("/")
def index():
    return render_template("index.html")

# Endpoint untuk transkrip audio
@app.route("/transcribe", methods=["POST"])
def transcribe():
    if "file" not in request.files:
        return "❌ Tidak ada file di-upload"

    file = request.files["file"]

    if file.filename == "":
        return "❌ Nama file kosong"

    # Simpan file sementara
    os.makedirs("uploads", exist_ok=True)
    filepath = os.path.join("uploads", file.filename)
    file.save(filepath)

    # Konversi ke WAV (biar SpeechRecognition bisa baca)
    audio = AudioSegment.from_file(filepath)
    wav_path = filepath.rsplit(".", 1)[0] + ".wav"
    audio.export(wav_path, format="wav")

    # Transkripsi dengan Google Speech Recognition
    recognizer = sr.Recognizer()
    with sr.AudioFile(wav_path) as source:
        audio_data = recognizer.record(source)
        try:
            text = recognizer.recognize_google(audio_data, language="id-ID")
        except sr.UnknownValueError:
            text = "[❌ Tidak dikenali]"
        except sr.RequestError as e:
            text = f"[⚠️ Error Google Speech Recognition: {e}]"

    return f"<h3>Hasil Transkrip:</h3><p>{text}</p>"

if __name__ == "__main__":
    # Ambil port dari environment variable (WAJIB di hosting Pella/Heroku)
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
