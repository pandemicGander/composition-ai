import os
from data_conversion.converter_octave_range_harmony import midi_to_ai_format, ai_format_to_midi

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

def process_midi_files(raw_folder, processed_folder):
  if not os.path.exists(processed_folder):
    os.makedirs(processed_folder)

  for file_name in os.listdir(raw_folder):
    if file_name.lower().endswith('.mid') or file_name.lower().endswith('.midi'):
      raw_file_path = os.path.join(raw_folder, file_name)
      base_name = os.path.splitext(file_name)[0]
      processed_file_path = os.path.join(processed_folder, base_name + '_processed.txt')

      try:
        # Process MIDI file
        formatted_data = midi_to_ai_format(raw_file_path)

        # Save the processed data
        with open(processed_file_path, 'w') as f:
          for vector in formatted_data:
            f.write(','.join(map(str, vector)) + '\n')

        print(f"Processed {file_name} and saved to {processed_file_path}")
      except Exception as e:
        # Log error and continue with the next file
        print(f"Error while processing {file_name}: {e}")
        continue


def reconstruct_midi_files(processed_folder, reconstructed_folder):
  if not os.path.exists(reconstructed_folder):
    os.makedirs(reconstructed_folder)

  for file_name in os.listdir(processed_folder):
    if file_name.endswith('_processed.txt'):
      processed_file_path = os.path.join(processed_folder, file_name)
      reconstructed_file_path = os.path.join(reconstructed_folder, file_name.replace('_processed.txt', '_reconstructed.mid'))

      try:
        # Load processed data
        with open(processed_file_path, 'r') as f:
          pitch_data = [list(map(int, line.strip().split(','))) for line in f]

        # Reconstruct the MIDI file from the processed pitch data
        ai_format_to_midi(pitch_data, reconstructed_file_path)

        print(f"Reconstructed MIDI saved to {reconstructed_file_path}")
      except Exception as e:
        # Log error and continue with the next file
        print(f"Error while reconstructing from {file_name}: {e}")
        continue


def reconstruct_from_predictions(predictions_folder, reconstructed_folder):
  if not os.path.exists(reconstructed_folder):
    os.makedirs(reconstructed_folder)

  for file_name in os.listdir(predictions_folder):
    if file_name.endswith('.txt'):
      prediction_file_path = os.path.join(predictions_folder, file_name)
      reconstructed_file_path = os.path.join(reconstructed_folder, file_name.replace('.txt', '_predicted.mid'))

      try:
        # Load predicted data
        with open(prediction_file_path, 'r') as f:
          pitch_data = [list(map(int, line.strip().split(','))) for line in f]

        # Reconstruct the MIDI file from the predicted pitch data
        ai_format_to_midi(pitch_data, reconstructed_file_path)

        print(f"Reconstructed MIDI from predictions saved to {reconstructed_file_path}")
      except Exception as e:
        # Log error and continue with the next file
        print(f"Error while reconstructing from predictions in {file_name}: {e}")
        continue


if __name__ == '__main__':
  raw_folder = os.path.join(SCRIPT_DIR, 'data', 'raw_midi')
  ai_format_folder = os.path.join(SCRIPT_DIR, 'data', 'ai_format', 'octave_range_harmony')
  reconstructed_folder = os.path.join(SCRIPT_DIR, 'data', 'reconstructed_midi')
  predictions_folder = os.path.join(SCRIPT_DIR, 'data', 'predictions', 'octave_range_harmony')

  process_midi_files(raw_folder, ai_format_folder)
  reconstruct_midi_files(ai_format_folder, reconstructed_folder)
  reconstruct_from_predictions(predictions_folder, reconstructed_folder)
