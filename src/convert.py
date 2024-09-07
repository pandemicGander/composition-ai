import os
from data_conversion.converter import midi_to_ai_format, ai_format_to_midi

def process_midi_files(raw_folder, processed_folder):
  # Check if processed folder exists, create if not
  if not os.path.exists(processed_folder):
    os.makedirs(processed_folder)

  # Iterate through all files in the raw folder
  for file_name in os.listdir(raw_folder):
    if file_name.endswith('.mid') or file_name.endswith('.midi'):
      raw_file_path = os.path.join(raw_folder, file_name)
      processed_file_path = os.path.join(processed_folder, file_name.replace('.mid', '_processed.txt'))

      # Process MIDI file
      formatted_data = midi_to_ai_format(raw_file_path)

      # Save the processed data
      with open(processed_file_path, 'w') as f:
        for line in formatted_data:
          f.write(f"{','.join(map(str, line))}\n")

      print(f"Processed {file_name} and saved to {processed_file_path}")

def reconstruct_midi_files(processed_folder, reconstructed_folder):
  # Check if reconstructed folder exists, create if not
  if not os.path.exists(reconstructed_folder):
    os.makedirs(reconstructed_folder)

  # Iterate through all files in the processed folder
  for file_name in os.listdir(processed_folder):
    if file_name.endswith('_processed.txt'):
      processed_file_path = os.path.join(processed_folder, file_name)
      reconstructed_file_path = os.path.join(reconstructed_folder, file_name.replace('_processed.txt', '_reconstructed.mid'))

      # Load processed data
      with open(processed_file_path, 'r') as f:
        pitch_data = [list(map(int, line.strip().split(','))) for line in f]

      # Reconstruct the MIDI file from the processed pitch data
      ai_format_to_midi(pitch_data, reconstructed_file_path)

      print(f"Reconstructed MIDI saved to {reconstructed_file_path}")

#TODO need a format that also looks like this:
# takes out the rhythm and just leaves the distinct notes
# these rhythms are then saved in a separate format which can apply back to the notes (can also be trained on their own)
# take the octaves so we have a separate voicing model

if __name__ == '__main__':
  raw_folder = 'data/raw_midi'
  ai_format_folder = 'data/ai_format'
  reconstructed_folder = 'data/reconstructed_midi'

  process_midi_files(raw_folder, ai_format_folder)
  reconstruct_midi_files(ai_format_folder, reconstructed_folder)
