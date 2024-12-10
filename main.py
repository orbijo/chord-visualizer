import os
import sounddevice as sd
from scipy.io.wavfile import write
import subprocess

# Setting the sample rate for the audio
fs = 44100  # Sample rate (samples per second)

# Getting user input for recording duration
second = 5  # Duration in seconds
print("Recording....\n")

# Recording audio using sounddevice library
record_voice = sd.rec(int(second * fs), samplerate=fs, channels=2)  # Recording stereo audio
sd.wait()  # Wait for recording to complete

# Ensure the 'audio' directory exists
audio_directory = 'audio'
if not os.path.exists(audio_directory):
    os.makedirs(audio_directory)

# Saving the recorded audio to a WAV file in the 'audio' folder
output_path = os.path.join(audio_directory, "out.wav")
write(output_path, fs, record_voice)

print("Finished...\nPlease check the 'audio' folder for the recording.")

# Run chord-visualizer.py script
subprocess.run(["python", "chord-visualizer.py"])

print("chord-visualizer.py script executed.")

# Playing movie.mp4
movie_file = "movie.mp4"
if os.path.exists(movie_file):
    if os.name == 'nt':  # For Windows
        os.startfile(movie_file)
    elif os.name == 'posix':  # For macOS and Linux
        subprocess.run(["open", movie_file])  # macOS
        subprocess.run(["xdg-open", movie_file])  # Linux
else:
    print(f"File {movie_file} does not exist.")
