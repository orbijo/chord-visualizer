import pygame
import math
import pyaudio

#Pygame Init
screen_width = 1280
screen_height = 720
pygame.init()
pygame.display.set_caption("Chord Visualizer")
screen = pygame.display.set_mode((screen_width, screen_height))
clock = pygame.time.Clock()

#Audio Init
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100

p = pyaudio.PyAudio()
stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK
                )

def get_microphone_input_level():
    data = stream.read(CHUNK)
    rms = 0
    for i in range(0, len(data), 2):
        sample = int.from_bytes(data[i:i + 2], byteorder='little', signed=True)
        rms += sample * sample
    rms = math.sqrt(rms / (CHUNK / 2))
    return rms

def draw_sine_wave(amplitude):
    screen.fill((255, 255, 255))
    points = []
    if amplitude > 10:
        for x in range(screen_width):
            y = screen_height/2 + int(amplitude * math.sin(x * 0.02))
            points.append((x, y))
    else:
        points.append((0, screen_height/2))
        points.append((screen_width, screen_height/2))

    pygame.draw.lines(screen, (0, 0, 255), False, points, 2)
    pygame.display.flip()

running = True
amplitude = 100

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    amplitude_adjustment = get_microphone_input_level() / 50
    amplitude = max(10, amplitude_adjustment)

    draw_sine_wave(amplitude)
    clock.tick(60)

pygame.quit()
