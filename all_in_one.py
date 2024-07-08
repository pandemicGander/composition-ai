from music21 import stream, pitch, note, midi
import json
import numpy as np
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import LSTM, Dense

# Function to convert MIDI to a custom format for AI processing
def midi_to_custom_format(midi_file_path):
  from music21 import converter, note, chord
  midi_stream = converter.parse(midi_file_path)
  result = {}
  for midiData in midi_stream.flat.notesAndRests:
    beat_start = int(midiData.offset * 4)
    beat_end = int((midiData.offset + midiData.duration.quarterLength) * 4)
    if isinstance(midiData, chord.Chord):
      notes_list = [{'pitchClass': n.pitch.pitchClass} for n in midiData.notes]
      for beat in range(beat_start, beat_end):
        result.setdefault(beat, []).extend(notes_list)
    elif isinstance(midiData, note.Note):
      note_dict = {'pitchClass': midiData.pitch.pitchClass}
      for beat in range(beat_start, beat_end):
        result.setdefault(beat, []).append(note_dict)
  return result


# Function to prepare and train the LSTM model
def prepare_and_train_lstm(model_path, json_path):
  with open(json_path, 'r', encoding='utf-8') as file:
    data = json.load(file)
  sequences = np.array(data)
  X = sequences[:, :-1]  # Use all but the last pitch class for input
  y = sequences[:, -1]  # Use the last pitch class for the output
  X = X.reshape((X.shape[0], X.shape[1], 1))

  model = Sequential([
    LSTM(50, activation='relu', input_shape=(X.shape[1], 1)),
    Dense(12, activation='softmax')  # Changed to output 12 units, one for each pitch class
  ])
  model.compile(optimizer='adam', loss='sparse_categorical_crossentropy')  # Use categorical crossentropy for classification
  model.fit(X, y, epochs=200, verbose=1)
  model.save(model_path)
  print("Model trained and saved as", model_path)
  return model

# Function to predict new sequences and convert them to MIDI
def predict_and_convert_to_midi(model, input_sequences, output_midi_path):
  predictions = model.predict(input_sequences)
  # Since we are using softmax, predictions are probabilities for each class
  # We need to pick the class with the highest probability as our prediction
  predicted_classes = np.argmax(predictions, axis=-1)
  predicted_to_midi(predicted_classes, output_midi_path)

# Function to convert predicted pitch classes to MIDI format
def predicted_to_midi(predicted_classes, output_midi_path):
  s = stream.Stream()
  for pc in predicted_classes:
    # Create a Note object for each predicted pitch class
    n = note.Note()
    n.pitch = pitch.Pitch(midi=pc)  # Convert pitch class directly to MIDI note
    n.duration.quarterLength = 1  # Set a standard duration for simplicity
    s.append(n)
  # Save the stream as a MIDI file
  mf = midi.translate.streamToMidiFile(s)
  mf.open(output_midi_path, 'wb')
  mf.write()
  mf.close()
  print(f"Predicted MIDI file saved to: {output_midi_path}")


# Main execution flow
midi_file_path = 'tester2.mid'
formatted_data = midi_to_custom_format(midi_file_path)
output_midi_path = midi_file_path.replace('.mid', '_reconstructed.mid')

# Example usage, assuming previous functions and data saving/loading is handled elsewhere
model_path = 'my_lstm_model.h5'
model = prepare_and_train_lstm(model_path, 'pitch_classes.json')

# Assuming input_data preparation and other details handled correctly
# Predict and generate MIDI from new sequences
input_data = np.array(formatted_data)  # Placeholder for actual formatted data usage
input_data = input_data[:, :-1]  # Assuming data is prepared and appropriate
input_data = input_data.reshape((input_data.shape[0], input_data.shape[1], 1))
predicted_midi_path = 'predicted_output.mid'
predict_and_convert_to_midi(model, input_data, predicted_midi_path)
