from music21 import stream, note, midi, chord
import json

def array_to_midi(pitch_arrays, instruments=6, output_midi_path='output_midi.mid'):
  # Create a new music21 stream
  s = stream.Stream()

  # Iterate over each array (each representing a 16th note)
  for i, pitches in enumerate(pitch_arrays):
    # Create a chord for the current beat with the non-zero pitches
    notes = [note.Note(p) for p in pitches if p > 0]

    # If there are no notes, create a rest
    if not notes:
      n = note.Rest()
    else:
      # If there's only one note, don't create a chord
      n = notes[0] if len(notes) == 1 else chord.Chord(notes)

    # Set the duration of the note or chord to a 16th note
    n.duration.type = '16th'

    # Append the note or chord to the stream at the correct offset
    s.insert(i * 0.25, n)  # 0.25 because each array represents a 16th note (there are 4 in a quarter note)

  # Write the stream to a MIDI file
  mf = midi.translate.streamToMidiFile(s)
  mf.open(output_midi_path, 'wb')
  mf.write()
  mf.close()

  return output_midi_path

file_path = 'input_sequence.txt'

# Read and parse the file
with open(file_path, 'r') as file:
  data = file.read()
  pitch_arrays = json.loads(data)
# Example usage with the provided input data



output_midi_path = 'output_midi.mid'

# Convert the arrays to a MIDI file
array_to_midi(pitch_arrays, instruments=6, output_midi_path=output_midi_path)
