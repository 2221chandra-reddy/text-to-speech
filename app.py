import tkinter as tk
from tkinter import filedialog, messagebox
from TTS.api import TTS
from pydub import AudioSegment
import librosa
import soundfile as sf
import os
import uuid
import re

# folders
VOICE_FOLDER = "voices"
OUTPUT_FOLDER = "outputs"

os.makedirs(VOICE_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# load model
print("Loading model...")
tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2", gpu=False)
print("Ready")

current_voice = None


# ----------------------
# Upload voice
# ----------------------
def upload_voice():
    global current_voice

    file_path = filedialog.askopenfilename(filetypes=[("Audio Files", "*.mp3 *.wav")])
    if not file_path:
        return

    unique = str(uuid.uuid4())
    input_path = os.path.join(VOICE_FOLDER, unique + "_" + os.path.basename(file_path))

    with open(file_path, "rb") as f:
        with open(input_path, "wb") as out:
            out.write(f.read())

    wav_path = os.path.join(VOICE_FOLDER, unique + ".wav")

    if file_path.endswith(".mp3"):
        audio = AudioSegment.from_mp3(file_path)
        audio.export(wav_path, format="wav")
    else:
        wav_path = input_path

    y, sr = librosa.load(wav_path, sr=24000)
    y = librosa.util.normalize(y)
    y, _ = librosa.effects.trim(y)
    y = y[:sr * 6]
    sf.write(wav_path, y, sr)

    current_voice = wav_path
    messagebox.showinfo("Success", "Voice uploaded!")


# ----------------------
# Generate speech
# ----------------------
def generate():
    if current_voice is None:
        messagebox.showerror("Error", "Upload voice first")
        return

    text = text_box.get("1.0", tk.END).strip()
    if not text:
        messagebox.showerror("Error", "Enter text")
        return

    filename = filename_entry.get().strip()
    filename = re.sub(r'[^a-zA-Z0-9_]', '', filename)

    if not filename:
        filename = "speech"

    output_wav = os.path.join(OUTPUT_FOLDER, filename + ".wav")
    output_mp3 = os.path.join(OUTPUT_FOLDER, filename + ".mp3")

    tts.tts_to_file(
        text=text,
        speaker_wav=current_voice,
        language="en",
        file_path=output_wav
    )

    AudioSegment.from_wav(output_wav).export(output_mp3, format="mp3")

    messagebox.showinfo("Done", f"Saved:\n{output_mp3}")


# ----------------------
# UI
# ----------------------
root = tk.Tk()
root.title("Voice Cloning App")
root.geometry("500x500")

tk.Label(root, text="Enter Text").pack()

text_box = tk.Text(root, height=10)
text_box.pack(fill="both", padx=10, pady=10)

tk.Label(root, text="File Name").pack()
filename_entry = tk.Entry(root)
filename_entry.pack(fill="x", padx=10)

tk.Button(root, text="Upload Voice", command=upload_voice).pack(pady=10)
tk.Button(root, text="Generate Speech", command=generate).pack(pady=10)

root.mainloop()
