#!/usr/bin/env python3
"""Thanh Hoa 1 full solver.

1. Detect the appended AES ZIP (flag.txt) inside lyknctf.mp4
2. Extract audio, render a spectrogram (the hidden password 'RAUMAPHATAU'
   is painted into the ~8-12 kHz band)
3. Decrypt flag.txt with pyzipper

Flag: LYKNCTF{NGU01_TH4NH_H04_4N_R4U_M4_PH4_DU0NG_T4U}

Deps: pip install pyzipper imageio-ffmpeg scipy numpy matplotlib
"""
import sys, os, subprocess
import pyzipper


def inspect_zip(path):
    with pyzipper.AESZipFile(path) as z:
        for info in z.infolist():
            # compress_type 99 == AES; flag_bits & 1 == encrypted
            print(f"{info.filename}  method={info.compress_type}  "
                  f"encrypted={bool(info.flag_bits & 1)}  size={info.file_size}")


def make_spectrogram(mp4_path, out_png="spectrogram.png"):
    import imageio_ffmpeg
    import numpy as np
    from scipy.io import wavfile
    from scipy import signal
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    ff = imageio_ffmpeg.get_ffmpeg_exe()
    wav = "audio.wav"
    subprocess.run([ff, "-y", "-i", mp4_path, "-vn", "-acodec", "pcm_s16le",
                    "-ar", "44100", "-ac", "1", wav],
                   check=True, capture_output=True)
    sr, data = wavfile.read(wav)
    if data.ndim > 1:
        data = data[:, 0]
    data = data.astype(np.float32)
    f, t, Sxx = signal.spectrogram(data, fs=sr, nperseg=4096, noverlap=3900)
    Sxx_db = 10 * np.log10(Sxx + 1e-10)
    mask = (f >= 7500) & (f <= 12800)          # the hidden-text band
    plt.figure(figsize=(60, 6))
    plt.pcolormesh(t, f[mask], Sxx_db[mask], shading='auto', cmap='inferno')
    plt.tight_layout()
    plt.savefig(out_png, dpi=100)
    print("Spectrogram written to", out_png,
          "-> read the letters, they spell: RAUMAPHATAU")


def crack(path, password=b"RAUMAPHATAU"):
    with pyzipper.AESZipFile(path) as z:
        return z.read("flag.txt", pwd=password)


if __name__ == "__main__":
    mp4 = sys.argv[1] if len(sys.argv) > 1 else "lyknctf.mp4"
    print("== ZIP entries ==")
    inspect_zip(mp4)
    if "--spectrogram" in sys.argv:
        make_spectrogram(mp4)
    print("FLAG:", crack(mp4).decode())
