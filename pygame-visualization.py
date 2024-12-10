import numpy as np
import pygame
import sounddevice as sd
import threading
import queue

# Pygame configuration
pygame.init()
WIDTH, HEIGHT = 1280, 720
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
CLOCK = pygame.time.Clock()
FPS = 15

# Audio configuration
fs = 44100  # Sample rate (samples per second)
FFT_WINDOW_SECONDS = 0.25
FFT_WINDOW_SIZE = int(fs * FFT_WINDOW_SECONDS)
FREQ_MIN = 10
FREQ_MAX = 1000
TOP_NOTES = 3
NOTE_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

# Queue to hold audio data
audio_queue = queue.Queue()

# Hanning window function
window = 0.5 * (1 - np.cos(np.linspace(0, 2 * np.pi, FFT_WINDOW_SIZE, False)))
xf = np.fft.rfftfreq(FFT_WINDOW_SIZE, 1 / fs)

# Helper functions
def freq_to_number(f): return 69 + 12 * np.log2(f / 440.0)
def number_to_freq(n): return 440 * 2.0 ** ((n - 69) / 12.0)
def note_name(n): return NOTE_NAMES[n % 12] + str(int(n / 12 - 1))

def find_top_notes(fft, num):
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
        n0 = int(round(n))
        name = note_name(n0)
        if name not in found_note:
            found_note.add(name)
            found.append((f, name, y))
    return found

def draw_spectrum(fft, top_notes):
    SCREEN.fill((0, 0, 0))
    max_val = np.max(fft)
    if max_val == 0:
        max_val = 1  # Prevent division by zero

    # Plotting the FFT waveform
    for i in range(1, len(fft)):
        x1 = int((i - 1) * WIDTH / len(fft))
        y1 = int(HEIGHT - (fft[i - 1] / max_val * HEIGHT))
        x2 = int(i * WIDTH / len(fft))
        y2 = int(HEIGHT - (fft[i] / max_val * HEIGHT))
        pygame.draw.line(SCREEN, (0, 255, 0), (x1, y1), (x2, y2))

    # Annotating the top notes
    for note in top_notes:
        freq, name, mag = note
        x = int(freq / xf[-1] * WIDTH)
        y = int(HEIGHT - (mag / max_val * HEIGHT))
        pygame.draw.line(SCREEN, (255, 0, 0), (x, HEIGHT), (x, y), 2)
        label = pygame.font.SysFont('Arial', 24).render(name, True, (255, 255, 255))
        SCREEN.blit(label, (x, y - 30))

    pygame.display.flip()

# Callback function to process audio input
def audio_callback(indata, frames, time, status):
    if status:
        print(status)
    audio_queue.put(indata[:, 0])

# Thread to process audio data
def process_audio():
    while running:
        if not audio_queue.empty():
            sample = audio_queue.get()
            if len(sample) >= FFT_WINDOW_SIZE:
                fft = np.fft.rfft(sample[:FFT_WINDOW_SIZE] * window)
                fft = np.abs(fft)
                top_notes = find_top_notes(fft, TOP_NOTES)
                draw_spectrum(fft, top_notes)

# Main visualization loop
stream = sd.InputStream(callback=audio_callback, channels=1, samplerate=fs, blocksize=FFT_WINDOW_SIZE)
try:
    with stream:
        running = True
        audio_thread = threading.Thread(target=process_audio)
        audio_thread.start()
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    print("Quitting...")  # Debug statement
            CLOCK.tick(FPS)
        running = False
        audio_thread.join()
except Exception as e:
    print(f"Error in main loop: {e}")
finally:
    pygame.quit()
    print("Pygame closed successfully")  # Debug statement
