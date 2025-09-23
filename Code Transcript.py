import os
import zipfile
import speech_recognition as sr
from pydub import AudioSegment
import re
import sys

print("== Selamat Datang di Transkrip Audio ==")

def mp3_to_text(mp3_path):
    # Konversi MP3 ke WAV
    audio = AudioSegment.from_mp3(mp3_path)
    wav_path = "temp.wav"
    audio.export(wav_path, format="wav")

    recognizer = sr.Recognizer()
    with sr.AudioFile(wav_path) as source:
        audio_data = recognizer.record(source)

    try:
        text = recognizer.recognize_google(audio_data, language="id-ID")
        return text
    except sr.UnknownValueError:
        return "[Tidak dikenali]"
    except sr.RequestError as e:
        return f"[Error Google Speech Recognition: {e}]"

def natural_sort_key(text):
    """Supaya urutan chunk_1, chunk_2, ... chunk_10 benar"""
    return [int(num) if num.isdigit() else num for num in re.split(r'(\d+)', text)]

def transcribe_zip(zip_path, extract_dir, output_dir, output_file):
    # Tampilkan informasi path
    print("=== Konfirmasi Path Transkrip ===")
    print(f"ZIP Input        : {zip_path}")
    print(f"Folder Extract   : {extract_dir}")
    print(f"Folder Transkrip : {output_dir}")
    print(f"Nama File Output : {output_file}")
    print("=================================")

    # Konfirmasi
    pilihan = input("Apakah yakin ingin memproses? (Y/N): ").strip().lower()
    if pilihan != "y":
        print("❌ Dibatalkan oleh pengguna.")
        sys.exit()

    # Buat folder hasil transkrip kalau belum ada
    os.makedirs(output_dir, exist_ok=True)

    # Buat folder extract kalau belum ada
    os.makedirs(extract_dir, exist_ok=True)

    # Ekstrak ZIP
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_dir)

    all_text = []

    # Loop semua file chunk MP3 (urut sesuai nomor)
    for file in sorted(os.listdir(extract_dir), key=natural_sort_key):
        if file.endswith(".mp3"):
            mp3_path = os.path.join(extract_dir, file)
            print(f"🎧 Memproses {file}...")

            hasil = mp3_to_text(mp3_path)

            # Tampilkan hasil di terminal
            print(f"📝 Hasil {file}: {hasil}\n")

            # Tambahkan ke list untuk digabung
            all_text.append(hasil)

    # Gabungkan semua transkrip jadi satu teks
    gabungan = " ".join(all_text)
    output_path = os.path.join(output_dir, output_file + ".txt")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(gabungan)

    # Cetak hasil gabungan ke terminal juga
    print("\n================ HASIL GABUNGAN ================\n")
    print(gabungan)
    print("\n✅ Semua transkrip digabung dan disimpan ke", output_path)

if __name__ == "__main__":
    # Minta input dari user
    zip_file = input("Masukkan path file ZIP input: ").strip()
    extract_dir = input("Masukkan folder untuk ekstrak ZIP: ").strip()
    output_dir = input("Masukkan folder hasil transkrip: ").strip()
    output_file = input("Masukkan nama file output (tanpa .txt): ").strip()

    # Jalankan transkrip
    transcribe_zip(zip_file, extract_dir, output_dir, output_file)
