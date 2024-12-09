import os
import numpy as np
import matplotlib.pyplot as plt
from scipy.io import wavfile
import plotly.graph_objects as go
import subprocess
import glob

# CONFIG THIS 1ST
PATH = 'audio'
FILENAME = 'cmaj'
AUDIO_FILE = os.path.join(PATH, FILENAME + '.wav')

FPS = 30
FFT_WINDOW_SECONDS = 0.25
FREQ_MIN = 10
FREQ_MAX = 1000
TOP_NOTES = 3
NOTE_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
RESOLUTION = (1920, 1080)
SCALE = 2
MAX_DURATION = 3

# Create output directory
os.makedirs('frames', exist_ok=True)

# Load audio
fs, data = wavfile.read(AUDIO_FILE)
audio = data.T[0]  # first channel
FFT_WINDOW_SIZE = int(fs * FFT_WINDOW_SECONDS)
AUDIO_LENGTH = len(audio) / fs
FRAME_COUNT = int(AUDIO_LENGTH * FPS)
FRAME_OFFSET = int(len(audio) / FRAME_COUNT)

# FFT setup
window = 0.5 * (1 - np.cos(np.linspace(0, 2 * np.pi, FFT_WINDOW_SIZE, False)))
xf = np.fft.rfftfreq(FFT_WINDOW_SIZE, 1 / fs)

# Helper functions
def freq_to_number(f): return 69 + 12 * np.log2(f / 440.0)
def number_to_freq(n): return 440 * 2.0**((n - 69) / 12.0)
def note_name(n): return NOTE_NAMES[n % 12] + str(int(n / 12 - 1))

def plot_fft(p, xf, fs, notes):
    layout = go.Layout(
        title="Frequency Spectrum",
        autosize=False,
        width=RESOLUTION[0],
        height=RESOLUTION[1],
        xaxis_title="Frequency (Hz)",
        yaxis_title="Magnitude",
        font={'size': 24}
    )
    fig = go.Figure(layout=layout)
    fig.add_trace(go.Scatter(x=xf, y=p))
    for note in notes:
        fig.add_annotation(x=note[0] + 10, y=note[2], text=note[1], font={'size': 24}, showarrow=False)
    return fig

def extract_sample(audio, frame_number):
    end = frame_number * FRAME_OFFSET
    begin = int(end - FFT_WINDOW_SIZE)
    if begin < 0:
        return np.concatenate([np.zeros(abs(begin)), audio[:end]])
    return audio[begin:end]

# Find max amplitude for scaling
mx = 0
for frame_number in range(FRAME_COUNT):
    sample = extract_sample(audio, frame_number)
    fft = np.abs(np.fft.rfft(sample * window))
    mx = max(mx, np.max(fft))

# Generate frames
MAX_FRAMES = int(FPS * MAX_DURATION)
for frame_number in range(min(FRAME_COUNT, MAX_FRAMES)):
    sample = extract_sample(audio, frame_number)
    fft = np.abs(np.fft.rfft(sample * window)) / mx
    fig = plot_fft(fft, xf, fs, [])
    fig.write_image(f"frames/frame{frame_number}.png", scale=SCALE)

# Create video
subprocess.run([
    "ffmpeg", "-y", "-r", str(FPS), "-f", "image2", "-s", "1920x1080",
    "-i", "frames/frame%d.png", "-i", AUDIO_FILE,
    "-c:v", "libx264", "-pix_fmt", "yuv420p", "-t", str(MAX_DURATION),
    "movie.mp4"
])

print("Video saved as movie.mp4.")
