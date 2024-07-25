import os
from data_conversion.converter import midi_to_custom_format, extractPitchesForAIFormat

def process_all_midi_files(raw_folder, processed_folder):
  # Check if processed folder exists, create if not
  if not os.path.exists(processed_folder):
    os.makedirs(processed_folder)

  # Iterate through all files in the raw folder
  for file_name in os.listdir(raw_folder):
    if file_name.endswith('.mid') or file_name.endswith('.midi'):
      raw_file_path = os.path.join(raw_folder, file_name)
      processed_file_path = os.path.join(processed_folder, file_name.replace('.mid', '_processed.txt'))

      # Process MIDI file
      formatted_data = midi_to_custom_format(raw_file_path)
      pitch_data = extractPitchesForAIFormat(formatted_data)

      # Save the processed data
      with open(processed_file_path, 'w') as f:
        for line in pitch_data:
          f.write(f"{','.join(map(str, line))}\n")

      print(f"Processed {file_name} and saved to {processed_file_path}")

if __name__ == '__main__':
  raw_folder = 'data/raw'
  processed_folder = 'data/processed'
  process_all_midi_files(raw_folder, processed_folder)
