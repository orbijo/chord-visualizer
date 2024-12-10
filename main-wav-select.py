import os
import shutil
import subprocess

# Directory where the WAV files are stored
audio_directory = 'audio'

# List WAV files in the directory
wav_files = [f for f in os.listdir(audio_directory) if f.endswith('.wav')]

# Prompt user to select a WAV file
print("Available WAV files:")
for idx, file in enumerate(wav_files):
    print(f"{idx + 1}. {file}")

selected_idx = int(input("Select a WAV file by number: ")) - 1
selected_file = wav_files[selected_idx]
input_path = os.path.join(audio_directory, selected_file)
output_path = os.path.join(audio_directory, "out.wav")

print(f"Selected file: {selected_file}")

# Ensure the selected file exists
if os.path.exists(input_path):
    # Copy the selected file to out.wav
    shutil.copy(input_path, output_path)
    print(f"Copied {selected_file} to out.wav")

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
else:
    print(f"File {input_path} does not exist.")
