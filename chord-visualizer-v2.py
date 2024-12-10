import numpy as np
import plotly.graph_objects as go
import pygame
import threading
import queue
import time

# Pygame configuration
pygame.init()
WIDTH, HEIGHT = 1280, 720
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Chord Visualizer")
CLOCK = pygame.time.Clock()
FPS = 30

# Audio configuration
RATE = 44100
FFT_WINDOW_SECONDS = 0.25
FFT_WINDOW_SIZE = int(RATE * FFT_WINDOW_SECONDS)
TOP_NOTES = 3
NOTE_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

# Queue to hold audio data
audio_queue = queue.Queue()

# Helper functions
def freq_to_number(f): 
    return 69 + 12 * np.log2(f / 440.0) if f != 0 else -np.inf

def note_name(n): 
    return NOTE_NAMES[n % 12] + str(int(n / 12 - 1))

def find_top_notes(fft, xf, num):
    if np.max(fft) < 0.001:
        return []
    lst = [x for x in enumerate(fft)]
    lst = sorted(lst, key=lambda x: x[1], reverse=True)
    found = []
    found_note = set()
    for idx in range(len(lst)):
        if len(found) >= num:
            break
        f = xf[lst[idx][0]]
        y = lst[idx][1]
        n = freq_to_number(f)
        if n == -np.inf:
            continue
        n0 = int(round(n))
        name = note_name(n0)
        if name not in found_note:
            found_note.add(name)
            found.append((f, name, y))
    return found

def generate_plotly_frame(fft, xf, top_notes):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=xf, y=fft, mode='lines', name='FFT'))
    for note in top_notes:
        fig.add_annotation(x=note[0], y=note[2], text=note[1], showarrow=True, arrowhead=1)
    fig.update_layout(width=WIDTH, height=HEIGHT, xaxis_title="Frequency", yaxis_title="Magnitude")
    return fig

def save_plotly_frame(fig, frame_path):
    fig.write_image(frame_path, engine="kaleido")

def draw_pygame_frame(frame_path):
    frame = pygame.image.load(frame_path)
    SCREEN.blit(frame, (0, 0))
    pygame.display.flip()

def audio_callback(indata, frames, time, status):
    if status:
        print(status)
    audio_queue.put(indata[:, 0])

def process_audio():
    xf = np.fft.rfftfreq(FFT_WINDOW_SIZE, 1 / RATE)
    while running:
        if not audio_queue.empty():
            sample = audio_queue.get()
            if len(sample) >= FFT_WINDOW_SIZE:
                fft = np.abs(np.fft.rfft(sample[:FFT_WINDOW_SIZE] * np.hanning(FFT_WINDOW_SIZE)))
                top_notes = find_top_notes(fft, xf, TOP_NOTES)
                fig = generate_plotly_frame(fft, xf, top_notes)
                save_plotly_frame(fig, "current_frame.png")
                draw_pygame_frame("current_frame.png")

# Main loop
import sounddevice as sd
stream = sd.InputStream(callback=audio_callback, channels=1, samplerate=RATE, blocksize=FFT_WINDOW_SIZE)
try:
    with stream:
        running = True
        audio_thread = threading.Thread(target=process_audio)
        audio_thread.start()
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    print("Quitting...")
            CLOCK.tick(FPS)
        running = False
        audio_thread.join()
except Exception as e:
    print(f"Error in main loop: {e}")
finally:
    pygame.quit()
    print("Pygame closed successfully")
